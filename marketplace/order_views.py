from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import uuid

from .models import ItemListing, Order, OrderStatusHistory, WalletTransaction
from .order_serializers import (
    OrderSerializer,
    OrderListSerializer,
    InitiateOrderSerializer,
    CheckoutOrderSerializer,
    OrderStatusUpdateSerializer,
    OrderStatusHistorySerializer,
    PaymentInitializationSerializer,
)
from .payment_service import paystack_service
from .ledger_service import FinancialLedgerService
from .idempotency import build_reference, get_request_id
from .background_jobs import (
    refresh_financial_reconciliation_snapshot,
    run_after_commit,
    send_finance_alert,
    send_user_sms_notification,
)
from accounts.models import Profile
from accounts.fcm_service import notify_user


# ============ ORDER MANAGEMENT ============

def _can_update_order_status(user, order, new_status):
    if new_status in ['seller_preparing', 'with_courier', 'delivered']:
        return order.seller == user
    if new_status == 'cancelled':
        return user in [order.buyer, order.seller]
    return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_order(request):
    """
    Seller creates an order for a buyer after negotiation

    POST /api/marketplace/orders/initiate/
    Body: {
        "item_id": 123,
        "buyer_id": 456,
        "delivery_method": "pickup"
    }
    """
    serializer = InitiateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    seller = request.user
    item_id = serializer.validated_data['item_id']
    buyer_id = serializer.validated_data['buyer_id']
    delivery_method = serializer.validated_data['delivery_method']

    try:
        with db_transaction.atomic():
            item = ItemListing.objects.select_for_update().get(id=item_id)

            if item.seller != seller:
                return Response({'error': "You don't own this item"}, status=status.HTTP_403_FORBIDDEN)

            if item.status != 'active':
                return Response({'error': 'Item is not available for sale'}, status=status.HTTP_400_BAD_REQUEST)

            if delivery_method == 'campusdeal' and not item.allow_campusdeal_delivery:
                return Response({'error': 'CampusDeal delivery not available for this item'}, status=status.HTTP_400_BAD_REQUEST)
            if delivery_method == 'seller' and not item.allow_seller_delivery:
                return Response({'error': 'Seller delivery not available for this item'}, status=status.HTTP_400_BAD_REQUEST)
            if delivery_method == 'pickup' and not item.allow_pickup:
                return Response({'error': 'Pickup not available for this item'}, status=status.HTTP_400_BAD_REQUEST)

            from django.contrib.auth.models import User
            buyer = get_object_or_404(User, id=buyer_id)

            if buyer == seller:
                return Response({'error': 'Buyer and seller cannot be the same user'}, status=status.HTTP_400_BAD_REQUEST)

            item_price = item.price
            service_fee = item_price * Decimal('0.035')
            delivery_fee = Decimal('500.00') if delivery_method == 'campusdeal' else Decimal('0.00')
            total_amount = item_price + service_fee + delivery_fee

            order = Order.objects.create(
                item=item,
                buyer=buyer,
                seller=seller,
                delivery_method=delivery_method,
                item_price=item_price,
                service_fee=service_fee,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                status='payment_pending',
            )

            if delivery_method == 'campusdeal':
                order.waybill_number = f'WB{uuid.uuid4().hex[:8].upper()}'
                order.save()

            item.status = 'pending'
            item.save()

            OrderStatusHistory.objects.create(
                order=order, from_status='', to_status='payment_pending', changed_by=seller
            )

        # Notify buyer to pay
        run_after_commit(
            'initiate-order-notify-buyer',
            notify_user,
            buyer,
            'Order Created — Pay Now',
            f'{seller.get_full_name() or seller.username} created an order for {item.title}. Total: ₦{total_amount:,.0f}. Proceed to payment.',
            notification_type='order_created',
            related_id=order.order_id,
        )

        return Response({
            'order_id': order.order_id,
            'total_amount': str(total_amount),
            'breakdown': {
                'item_price': str(item_price),
                'service_fee': str(service_fee),
                'delivery_fee': str(delivery_fee),
            },
            'waybill_number': order.waybill_number,
            'payment_required': True,
            'message': 'Order created. Waiting for buyer payment.',
        }, status=status.HTTP_201_CREATED)

    except ItemListing.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Order creation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buyer_order(request):
    """
    Buyer directly creates an order for a non-negotiable item

    POST /api/marketplace/orders/buy/
    Body: {
        "item_id": 123,
        "delivery_method": "pickup"
    }
    """
    item_id = request.data.get('item_id')
    delivery_method = request.data.get('delivery_method', 'pickup')

    if not item_id:
        return Response({'error': 'item_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    if delivery_method not in ['campusdeal', 'seller', 'pickup']:
        return Response({'error': 'Invalid delivery method'}, status=status.HTTP_400_BAD_REQUEST)

    buyer = request.user

    try:
        with db_transaction.atomic():
            item = ItemListing.objects.select_for_update().get(id=item_id)

            if item.is_negotiable:
                return Response(
                    {'error': 'This item is negotiable. Contact the seller to agree on a price first.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if item.status != 'active':
                return Response({'error': 'Item is not available for sale'}, status=status.HTTP_400_BAD_REQUEST)

            if item.seller == buyer:
                return Response({'error': 'You cannot buy your own item'}, status=status.HTTP_400_BAD_REQUEST)

            if delivery_method == 'campusdeal' and not item.allow_campusdeal_delivery:
                return Response({'error': 'CampusDeal delivery not available for this item'}, status=status.HTTP_400_BAD_REQUEST)
            if delivery_method == 'seller' and not item.allow_seller_delivery:
                return Response({'error': 'Seller delivery not available for this item'}, status=status.HTTP_400_BAD_REQUEST)
            if delivery_method == 'pickup' and not item.allow_pickup:
                return Response({'error': 'Pickup not available for this item'}, status=status.HTTP_400_BAD_REQUEST)

            item_price = item.price
            service_fee = item_price * Decimal('0.035')
            delivery_fee = Decimal('500.00') if delivery_method == 'campusdeal' else Decimal('0.00')
            total_amount = item_price + service_fee + delivery_fee

            order = Order.objects.create(
                item=item,
                buyer=buyer,
                seller=item.seller,
                delivery_method=delivery_method,
                item_price=item_price,
                service_fee=service_fee,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                status='payment_pending',
            )

            if delivery_method == 'campusdeal':
                order.waybill_number = f'WB{uuid.uuid4().hex[:8].upper()}'
                order.save()

            item.status = 'pending'
            item.save()

            OrderStatusHistory.objects.create(
                order=order, from_status='', to_status='payment_pending', changed_by=buyer
            )

        # Notify seller
        run_after_commit(
            'buyer-order-notify-seller',
            notify_user,
            item.seller,
            'New Order Received',
            f'{buyer.get_full_name() or buyer.username} bought your {item.title}. Order {order.order_id} created.',
            notification_type='order_created',
            related_id=order.order_id,
        )

        return Response({
            'order_id': order.order_id,
            'total_amount': str(total_amount),
            'breakdown': {
                'item_price': str(item_price),
                'service_fee': str(service_fee),
                'delivery_fee': str(delivery_fee),
            },
            'waybill_number': order.waybill_number,
            'message': 'Order created. Please proceed to payment.',
        }, status=status.HTTP_201_CREATED)

    except ItemListing.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Order creation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_order(request, order_id):
    """
    POST /api/marketplace/orders/{order_id}/checkout/
    """
    buyer = request.user
    order = get_object_or_404(Order, order_id=order_id, buyer=buyer)

    if order.status != 'payment_pending':
        return Response({'error': 'Order is not awaiting payment'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CheckoutOrderSerializer(data=request.data, context={'order': order})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    payment_method = serializer.validated_data['payment_method']
    idempotency_key = get_request_id(request, fallback='checkout')

    if order.delivery_method in ['campusdeal', 'seller']:
        order.delivery_address = serializer.validated_data.get('delivery_address', '')
        order.delivery_phone = serializer.validated_data.get('delivery_phone', '')
        order.save()

    if payment_method == 'wallet':
        return process_wallet_payment(order, buyer)
    elif payment_method == 'paystack':
        return initialize_paystack_payment(order, buyer, idempotency_key=idempotency_key)
    else:
        return Response({'error': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)


def process_wallet_payment(order, buyer):
    if order.status != 'payment_pending':
        return Response({'error': 'Order is not awaiting payment'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with db_transaction.atomic():
            profile = Profile.objects.select_for_update().get(user=buyer)

            if profile.wallet_balance < order.total_amount:
                return Response({
                    'error': 'Insufficient wallet balance',
                    'available': str(profile.wallet_balance),
                    'required': str(order.total_amount),
                }, status=status.HTTP_400_BAD_REQUEST)

            balance_before = profile.wallet_balance

            from django.db.models import F
            Profile.objects.filter(user=buyer).update(wallet_balance=F('wallet_balance') - order.total_amount)
            profile.refresh_from_db()

            WalletTransaction.objects.create(
                user=buyer,
                transaction_type='debit',
                amount=order.total_amount,
                source='purchase',
                related_order=order,
                balance_before=balance_before,
                balance_after=profile.wallet_balance,
            )

            order.status = 'paid'
            order.funds_held = True
            order.payment_method = 'wallet'
            order.paid_at = timezone.now()
            order.save()

            OrderStatusHistory.objects.create(
                order=order, from_status='payment_pending', to_status='paid', changed_by=buyer
            )

            FinancialLedgerService.record_order_payment(order=order, payment_method='wallet', created_by=buyer)

        run_after_commit(
            'wallet-payment-notify-seller',
            notify_user,
            order.seller,
            'Payment Received',
            f'Payment of ₦{order.total_amount:,.0f} received for order {order.order_id}. Prepare the item.',
            notification_type='payment_received',
            related_id=order.order_id,
        )

        return Response({
            'success': True,
            'order_id': order.order_id,
            'status': 'paid',
            'message': 'Payment successful. Seller will prepare your item.',
            'waybill_number': order.waybill_number,
        })

    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Payment processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def initialize_paystack_payment(order, buyer, idempotency_key='checkout'):
    if order.status != 'payment_pending':
        return Response({'error': 'Order is not awaiting payment'}, status=status.HTTP_400_BAD_REQUEST)

    if order.paystack_reference and order.paystack_access_code:
        return Response({
            'authorization_url': f'https://checkout.paystack.com/{order.paystack_access_code}',
            'access_code': order.paystack_access_code,
            'reference': order.paystack_reference,
            'message': 'Existing payment session reused',
        })

    reference = build_reference('PAY', order.order_id, buyer.id, 'paystack', idempotency_key)
    callback_url = f'{settings.FRONTEND_URL}/payment/verify'

    metadata = {
        'order_id': order.order_id,
        'buyer_id': buyer.id,
        'custom_fields': [{'display_name': 'Order ID', 'variable_name': 'order_id', 'value': order.order_id}],
    }

    result = paystack_service.initialize_payment(
        email=buyer.email,
        amount=order.total_amount * 100,
        reference=reference,
        callback_url=callback_url,
        metadata=metadata,
    )

    if result.get('status'):
        order.paystack_reference = reference
        order.paystack_access_code = result['data']['access_code']
        order.save()
        return Response({
            'authorization_url': result['data']['authorization_url'],
            'access_code': result['data']['access_code'],
            'reference': reference,
        })
    else:
        return Response({
            'error': 'Payment initialization failed',
            'message': result.get('message'),
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    POST /api/marketplace/payments/verify/
    """
    reference = request.data.get('reference')
    if not reference:
        return Response({'error': 'Reference is required'}, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, paystack_reference=reference)

    if request.user != order.buyer and not request.user.is_staff:
        return Response({'error': "You don't have permission to verify this payment"}, status=status.HTTP_403_FORBIDDEN)

    if order.status == 'paid' and order.funds_held:
        return Response({'success': True, 'order_id': order.order_id, 'status': 'paid', 'message': 'Payment already verified'})

    result = paystack_service.verify_payment(reference)

    if result.get('status') and result['data']['status'] == 'success':
        metadata = result['data'].get('metadata') or {}
        verified_buyer_id = metadata.get('buyer_id')
        if verified_buyer_id and int(verified_buyer_id) != request.user.id:
            return Response({'error': 'Payment reference does not belong to this user'}, status=status.HTTP_403_FORBIDDEN)

        with db_transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            if order.status == 'paid' and order.funds_held:
                return Response({'success': True, 'order_id': order.order_id, 'status': 'paid', 'message': 'Payment already verified'})

            old_status = order.status
            order.status = 'paid'
            order.funds_held = True
            order.payment_method = 'paystack'
            order.paid_at = timezone.now()
            order.save()

            OrderStatusHistory.objects.create(order=order, from_status=old_status, to_status='paid', changed_by=request.user)
            FinancialLedgerService.record_order_payment(order=order, payment_method='paystack', created_by=request.user)

            run_after_commit('order-payment-seller-sms', send_user_sms_notification, order.seller,
                f'CampusDeal payment received for order {order.order_id}. Buyer payment is now secured.')
            run_after_commit('order-payment-buyer-sms', send_user_sms_notification, order.buyer,
                f'CampusDeal payment verified for order {order.order_id}. Your payment is now secured.')
            run_after_commit('order-payment-seller-push', notify_user, order.seller,
                'Payment Received', f'₦{order.total_amount:,.0f} secured for order {order.order_id}. Prepare the item.',
                notification_type='payment_received', related_id=order.order_id)
            run_after_commit('order-payment-reconcile', refresh_financial_reconciliation_snapshot,
                f'paystack payment {order.order_id}')

        return Response({'success': True, 'order_id': order.order_id, 'status': 'paid', 'message': 'Payment verified successfully'})
    else:
        send_finance_alert(
            subject='CampusDeal payment verification failed',
            message=f'Reference: {reference}\nUser: {request.user.id}\nPaystack: {result.get("message") or result.get("error")}',
        )
        return Response({'success': False, 'message': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def paystack_webhook(request):
    """
    POST /api/marketplace/payments/webhook/
    """
    paystack_signature = request.headers.get('x-paystack-signature')

    if not paystack_service.verify_webhook_signature(request.body, paystack_signature):
        send_finance_alert(subject='CampusDeal webhook signature rejected', message='Invalid signature.')
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

    event = request.data.get('event')
    data = request.data.get('data')

    if event == 'charge.success':
        reference = data['reference']
        try:
            with db_transaction.atomic():
                order = Order.objects.select_for_update().get(paystack_reference=reference)

                if order.status == 'paid' and order.funds_held:
                    return Response({'status': 'success'})

                old_status = order.status
                order.status = 'paid'
                order.funds_held = True
                order.payment_method = 'paystack'
                order.paid_at = timezone.now()
                order.save()

                OrderStatusHistory.objects.create(order=order, from_status=old_status, to_status='paid')
                FinancialLedgerService.record_order_payment(order=order, payment_method='paystack', created_by=None)

                run_after_commit('webhook-seller-sms', send_user_sms_notification, order.seller,
                    f'CampusDeal payment received for order {order.order_id}.')
                run_after_commit('webhook-buyer-sms', send_user_sms_notification, order.buyer,
                    f'CampusDeal payment verified for order {order.order_id}.')
                run_after_commit('webhook-seller-push', notify_user, order.seller,
                    'Payment Received', f'Order {order.order_id} paid. Prepare the item.',
                    notification_type='payment_received', related_id=order.order_id)
                run_after_commit('webhook-reconcile', refresh_financial_reconciliation_snapshot,
                    f'webhook payment {order.order_id}')

        except Order.DoesNotExist:
            send_finance_alert(subject='CampusDeal webhook unknown reference',
                message=f'Unknown reference: {reference}')
        except Exception as exc:
            send_finance_alert(subject='CampusDeal webhook processing failed',
                message=f'Reference: {reference}\nError: {exc}')

    return Response({'status': 'success'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """
    GET /api/marketplace/orders/
    """
    user = request.user
    role = request.query_params.get('role', 'buyer')

    if role not in ['buyer', 'seller']:
        return Response({'error': 'Invalid role. Must be buyer or seller.'}, status=status.HTTP_400_BAD_REQUEST)

    orders = Order.objects.filter(buyer=user) if role == 'buyer' else Order.objects.filter(seller=user)

    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.select_related('item', 'buyer', 'seller').order_by('-created_at')
    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    """
    GET /api/marketplace/orders/{order_id}/
    """
    order = get_object_or_404(Order.objects.select_related('item', 'buyer', 'seller'), order_id=order_id)

    if request.user not in [order.buyer, order.seller]:
        return Response({'error': "You don't have permission to view this order"}, status=status.HTTP_403_FORBIDDEN)

    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    PATCH /api/marketplace/orders/{order_id}/update-status/
    """
    order = get_object_or_404(Order, order_id=order_id)
    serializer = OrderStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_status = serializer.validated_data['status']
    notes = serializer.validated_data.get('notes', '')

    if not _can_update_order_status(request.user, order, new_status):
        return Response({'error': "You don't have permission to set this status"}, status=status.HTTP_403_FORBIDDEN)

    if order.status == new_status:
        return Response({'success': True, 'order_id': order.order_id, 'status': new_status, 'message': f'Order already in {new_status} status'})

    old_status = order.status
    order.status = new_status
    if new_status == 'delivered':
        order.delivered_at = timezone.now()
    order.save()

    OrderStatusHistory.objects.create(order=order, from_status=old_status, to_status=new_status, notes=notes, changed_by=request.user)

    # Notify the other party
    recipient = order.buyer if request.user == order.seller else order.seller
    run_after_commit(
        'order-status-push',
        notify_user,
        recipient,
        'Order Update',
        f'Order {order.order_id} status changed to {new_status}.',
        notification_type='order_status',
        related_id=order.order_id,
    )

    return Response({'success': True, 'order_id': order.order_id, 'status': new_status, 'message': f'Order status updated to {new_status}'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_delivery(request, order_id):
    """
    POST /api/marketplace/orders/{order_id}/confirm-delivery/
    """
    order = get_object_or_404(Order, order_id=order_id, buyer=request.user)

    if order.status != 'delivered':
        return Response({'error': 'Order must be delivered before confirmation'}, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        from django.db.models import F
        seller_profile = Profile.objects.select_for_update().get(user=order.seller)
        balance_before = seller_profile.wallet_balance

        Profile.objects.filter(user=order.seller).update(wallet_balance=F('wallet_balance') + order.item_price)
        seller_profile.refresh_from_db()

        WalletTransaction.objects.create(
            user=order.seller,
            transaction_type='credit',
            amount=order.item_price,
            source='sale',
            related_order=order,
            balance_before=balance_before,
            balance_after=seller_profile.wallet_balance,
        )

        order.status = 'completed'
        order.completed_at = timezone.now()
        order.funds_released_to_seller = True
        order.save()

        order.item.status = 'sold'
        order.item.save()

        OrderStatusHistory.objects.create(order=order, from_status='delivered', to_status='completed', changed_by=request.user)

    run_after_commit(
        'confirm-delivery-notify-seller',
        notify_user,
        order.seller,
        'Payment Released!',
        f'Buyer confirmed delivery for order {order.order_id}. ₦{order.item_price:,.0f} added to your wallet.',
        notification_type='delivery_confirmed',
        related_id=order.order_id,
    )

    return Response({'success': True, 'message': 'Delivery confirmed. Funds released to seller.', 'order_id': order.order_id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_status_history(request, order_id):
    """
    GET /api/marketplace/orders/{order_id}/status-history/
    """
    order = get_object_or_404(Order, order_id=order_id)

    if request.user not in [order.buyer, order.seller]:
        return Response({'error': "You don't have permission to view this order"}, status=status.HTTP_403_FORBIDDEN)

    history = order.status_history.all().order_by('-created_at')
    serializer = OrderStatusHistorySerializer(history, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """
    POST /api/marketplace/orders/{order_id}/cancel/
    """
    order = get_object_or_404(Order, order_id=order_id)

    if request.user not in [order.buyer, order.seller]:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if order.status in ['completed', 'cancelled', 'refunded']:
        return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        old_status = order.status

        if order.status == 'paid' and order.funds_held:
            FinancialLedgerService.process_order_refund(order=order, created_by=request.user, source='refund')

        order.status = 'cancelled'
        order.save()

        if order.item.status == 'pending':
            order.item.status = 'active'
            order.item.save()

        OrderStatusHistory.objects.create(order=order, from_status=old_status, to_status='cancelled', changed_by=request.user, notes='Order cancelled by user')

    # Notify the other party
    recipient = order.buyer if request.user == order.seller else order.seller
    run_after_commit(
        'cancel-order-notify',
        notify_user,
        recipient,
        'Order Cancelled',
        f'Order {order.order_id} has been cancelled.',
        notification_type='order_status',
        related_id=order.order_id,
    )

    return Response({'message': 'Order cancelled successfully', 'refund_amount': str(order.total_amount) if old_status == 'paid' else '0.00'})
