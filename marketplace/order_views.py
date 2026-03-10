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

from .models import (
    ItemListing, 
    Order, 
    OrderStatusHistory, 
    WalletTransaction
)
from .order_serializers import (
    OrderSerializer,
    OrderListSerializer,
    InitiateOrderSerializer,
    CheckoutOrderSerializer,
    OrderStatusUpdateSerializer,
    OrderStatusHistorySerializer,
    PaymentInitializationSerializer
)
from .payment_service import paystack_service
from accounts.models import Profile


# ============ ORDER MANAGEMENT ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_order(request):
    """
    Seller confirms sale and creates order
    
    POST /api/marketplace/orders/initiate/
    Body: {
        "item_id": 123,
        "buyer_id": 456,
        "delivery_method": "campusdeal"  // or "seller" or "pickup"
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
            # Lock the item row to prevent concurrent orders
            item = ItemListing.objects.select_for_update().get(id=item_id)
            
            if item.seller != seller:
                return Response(
                    {"error": "You don't own this item"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if item.status != 'active':
                return Response(
                    {"error": "Item is not available for sale"},
                    status=status.HTTP_400_BAD_REQUEST
                )
    
            # Validate delivery method is allowed
            if delivery_method == 'campusdeal' and not item.allow_campusdeal_delivery:
                return Response(
                    {"error": "CampusDeal delivery not available for this item"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if delivery_method == 'seller' and not item.allow_seller_delivery:
                return Response(
                    {"error": "Seller delivery not available for this item"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if delivery_method == 'pickup' and not item.allow_pickup:
                return Response(
                    {"error": "Pickup not available for this item"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get buyer
            from django.contrib.auth.models import User
            buyer = get_object_or_404(User, id=buyer_id)
            
            # Calculate fees
            item_price = item.price
            service_fee = item_price * Decimal('0.035')  # 3.5% platform fee
            
            # Delivery fee logic
            if delivery_method == 'campusdeal':
                delivery_fee = Decimal('500.00')
            else:
                delivery_fee = Decimal('0.00')
            
            total_amount = item_price + service_fee + delivery_fee
            
            # Create order
            order = Order.objects.create(
                item=item,
                buyer=buyer,
                seller=seller,
                delivery_method=delivery_method,
                item_price=item_price,
                service_fee=service_fee,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                status='payment_pending'
            )
            
            # Generate waybill if CampusDeal delivery
            if delivery_method == 'campusdeal':
                order.waybill_number = f"WB{uuid.uuid4().hex[:8].upper()}"
                order.save()
            
            # Update item status ATOMICALLY
            item.status = 'pending'
            item.save()
            
            # Log status change
            OrderStatusHistory.objects.create(
                order=order,
                from_status='',
                to_status='payment_pending',
                changed_by=seller
            )
        
        return Response({
            "order_id": order.order_id,
            "total_amount": str(total_amount),
            "breakdown": {
                "item_price": str(item_price),
                "service_fee": str(service_fee),
                "delivery_fee": str(delivery_fee)
            },
            "waybill_number": order.waybill_number,
            "payment_required": True,
            "message": "Order created. Waiting for buyer payment."
        }, status=status.HTTP_201_CREATED)
        
    except ItemListing.DoesNotExist:
        return Response(
            {"error": "Item not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Order creation failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_order(request, order_id):
    """
    Buyer proceeds to payment
    
    POST /api/marketplace/orders/{order_id}/checkout/
    Body: {
        "payment_method": "paystack",  // or "wallet"
        "delivery_address": "123 Main St",  // required for delivery
        "delivery_phone": "+2348012345678"  // required for delivery
    }
    """
    buyer = request.user
    order = get_object_or_404(Order, order_id=order_id, buyer=buyer)
    
    if order.status != 'payment_pending':
        return Response(
            {"error": "Order is not awaiting payment"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = CheckoutOrderSerializer(
        data=request.data,
        context={'order': order}
    )
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    payment_method = serializer.validated_data['payment_method']
    
    # Update delivery details if applicable
    if order.delivery_method in ['campusdeal', 'seller']:
        order.delivery_address = serializer.validated_data.get('delivery_address', '')
        order.delivery_phone = serializer.validated_data.get('delivery_phone', '')
        order.save()
    
    if payment_method == 'wallet':
        return process_wallet_payment(order, buyer)
    elif payment_method == 'paystack':
        return initialize_paystack_payment(order, buyer)
    else:
        return Response(
            {"error": "Invalid payment method"},
            status=status.HTTP_400_BAD_REQUEST
        )


def process_wallet_payment(order, buyer):
    """Process payment using wallet balance with race condition protection"""
    
    try:
        with db_transaction.atomic():
            # Lock the profile row to prevent concurrent access
            profile = Profile.objects.select_for_update().get(user=buyer)
            
            # Check balance
            if profile.wallet_balance < order.total_amount:
                return Response({
                    "error": "Insufficient wallet balance",
                    "available": str(profile.wallet_balance),
                    "required": str(order.total_amount)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store balance before
            balance_before = profile.wallet_balance
            
            # Use F() expression for atomic update
            from django.db.models import F
            Profile.objects.filter(user=buyer).update(
                wallet_balance=F('wallet_balance') - order.total_amount
            )
            
            # Refresh to get new balance
            profile.refresh_from_db()
            
            # Log transaction
            WalletTransaction.objects.create(
                user=buyer,
                transaction_type='debit',
                amount=order.total_amount,
                source='purchase',
                related_order=order,
                balance_before=balance_before,
                balance_after=profile.wallet_balance
            )
            
            # Update order
            order.status = 'paid'
            order.funds_held = True
            order.payment_method = 'wallet'
            order.paid_at = timezone.now()
            order.save()
            
            # Log status change
            OrderStatusHistory.objects.create(
                order=order,
                from_status='payment_pending',
                to_status='paid',
                changed_by=buyer
            )
        
        return Response({
            "success": True,
            "order_id": order.order_id,
            "status": "paid",
            "message": "Payment successful. Seller will prepare your item.",
            "waybill_number": order.waybill_number
        })
        
    except Profile.DoesNotExist:
        return Response(
            {"error": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Payment processing failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def initialize_paystack_payment(order, buyer):
    """Initialize payment with Paystack"""
    
    # Generate unique reference
    reference = f"{order.order_id}_{int(timezone.now().timestamp())}"
    
    # Callback URL (frontend will handle this)
    callback_url = f"{settings.FRONTEND_URL}/payment/verify"
    
    # Prepare metadata
    metadata = {
        "order_id": order.order_id,
        "buyer_id": buyer.id,
        "custom_fields": [
            {
                "display_name": "Order ID",
                "variable_name": "order_id",
                "value": order.order_id
            }
        ]
    }
    
    # Initialize with Paystack
    result = paystack_service.initialize_payment(
        email=buyer.email,
        amount=order.total_amount * 100,  # Convert to kobo
        reference=reference,
        callback_url=callback_url,
        metadata=metadata
    )
    
    if result.get('status'):
        # Save Paystack reference
        order.paystack_reference = reference
        order.paystack_access_code = result['data']['access_code']
        order.save()
        
        return Response({
            "authorization_url": result['data']['authorization_url'],
            "access_code": result['data']['access_code'],
            "reference": reference
        })
    else:
        return Response({
            "error": "Payment initialization failed",
            "message": result.get('message')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verify Paystack payment
    
    POST /api/marketplace/payments/verify/
    Body: {
        "reference": "CD123_1234567890"
    }
    """
    reference = request.data.get('reference')
    
    if not reference:
        return Response(
            {"error": "Reference is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get order
    order = get_object_or_404(Order, paystack_reference=reference)
    
    # Verify with Paystack
    result = paystack_service.verify_payment(reference)
    
    if result.get('status') and result['data']['status'] == 'success':
        # Payment successful
        with db_transaction.atomic():
            order.status = 'paid'
            order.funds_held = True
            order.payment_method = 'paystack'
            order.paid_at = timezone.now()
            order.save()
            
            # Log status change
            OrderStatusHistory.objects.create(
                order=order,
                from_status='payment_pending',
                to_status='paid',
                changed_by=request.user
            )
        
        # TODO: Send notification to seller
        
        return Response({
            "success": True,
            "order_id": order.order_id,
            "status": "paid",
            "message": "Payment verified successfully"
        })
    else:
        return Response({
            "success": False,
            "message": "Payment verification failed"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def paystack_webhook(request):
    """
    Receive and process Paystack webhooks
    This is called by Paystack when payment events occur
    
    POST /api/marketplace/payments/webhook/
    """
    # Verify webhook signature
    paystack_signature = request.headers.get('x-paystack-signature')
    
    if not paystack_service.verify_webhook_signature(request.body, paystack_signature):
        return Response(
            {"error": "Invalid signature"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Process event
    event = request.data.get('event')
    data = request.data.get('data')
    
    if event == 'charge.success':
        # Payment successful
        reference = data['reference']
        
        try:
            order = Order.objects.get(paystack_reference=reference)
            
            with db_transaction.atomic():
                order.status = 'paid'
                order.funds_held = True
                order.payment_method = 'paystack'
                order.paid_at = timezone.now()
                order.save()
                
                # Log status change
                OrderStatusHistory.objects.create(
                    order=order,
                    from_status='payment_pending',
                    to_status='paid'
                )
            
            # TODO: Send notification to seller
            
        except Order.DoesNotExist:
            pass
    
    return Response({"status": "success"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """
    Get user's orders (buyer or seller view)
    
    GET /api/marketplace/orders/
    Query params:
    - role: buyer|seller
    - status: payment_pending|paid|delivered|completed|cancelled
    """
    user = request.user
    role = request.query_params.get('role', 'buyer')
    
    if role == 'buyer':
        orders = Order.objects.filter(buyer=user)
    else:
        orders = Order.objects.filter(seller=user)
    
    # Filter by status if provided
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
    Get single order detail
    
    GET /api/marketplace/orders/{order_id}/
    """
    order = get_object_or_404(
        Order.objects.select_related('item', 'buyer', 'seller'),
        order_id=order_id
    )
    
    # Check user is buyer or seller
    if request.user not in [order.buyer, order.seller]:
        return Response(
            {"error": "You don't have permission to view this order"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """
    Update order status (seller only for most statuses)
    
    PATCH /api/marketplace/orders/{order_id}/update-status/
    Body: {
        "status": "seller_preparing",
        "notes": "Item is being packed"
    }
    """
    order = get_object_or_404(Order, order_id=order_id)
    
    serializer = OrderStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    new_status = serializer.validated_data['status']
    notes = serializer.validated_data.get('notes', '')
    
    # Validate user can update status
    if new_status in ['seller_preparing', 'with_courier']:
        if order.seller != request.user:
            return Response(
                {"error": "Only seller can update to this status"},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Update order
    old_status = order.status
    order.status = new_status
    
    if new_status == 'delivered':
        order.delivered_at = timezone.now()
    
    order.save()
    
    # Log status change
    OrderStatusHistory.objects.create(
        order=order,
        from_status=old_status,
        to_status=new_status,
        notes=notes,
        changed_by=request.user
    )
    
    return Response({
        "success": True,
        "order_id": order.order_id,
        "status": new_status,
        "message": f"Order status updated to {new_status}"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_delivery(request, order_id):
    """
    Buyer confirms delivery - triggers fund release to seller
    
    POST /api/marketplace/orders/{order_id}/confirm-delivery/
    """
    order = get_object_or_404(Order, order_id=order_id, buyer=request.user)
    
    if order.status not in ['delivered', 'paid']:
        return Response(
            {"error": "Order must be delivered before confirmation"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order with atomic wallet update
    with db_transaction.atomic():
        # Lock seller profile
        from django.db.models import F
        seller_profile = Profile.objects.select_for_update().get(user=order.seller)
        balance_before = seller_profile.wallet_balance
        
        # Use F() expression for atomic update
        Profile.objects.filter(user=order.seller).update(
            wallet_balance=F('wallet_balance') + order.item_price
        )
        
        # Refresh to get new balance
        seller_profile.refresh_from_db()
        
        # Log wallet transaction
        WalletTransaction.objects.create(
            user=order.seller,
            transaction_type='credit',
            amount=order.item_price,
            source='sale',
            related_order=order,
            balance_before=balance_before,
            balance_after=seller_profile.wallet_balance
        )
        
        # Update order
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.funds_released_to_seller = True
        order.save()
        
        # Update item status
        order.item.status = 'sold'
        order.item.save()
        
        # Log status change
        OrderStatusHistory.objects.create(
            order=order,
            from_status='delivered',
            to_status='completed',
            changed_by=request.user
        )
    
    return Response({
        "success": True,
        "message": "Delivery confirmed. Funds released to seller.",
        "order_id": order.order_id
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_status_history(request, order_id):
    """
    Get order status history
    
    GET /api/marketplace/orders/{order_id}/status-history/
    """
    order = get_object_or_404(Order, order_id=order_id)
    
    # Check permission
    if request.user not in [order.buyer, order.seller]:
        return Response(
            {"error": "You don't have permission to view this order"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    history = order.status_history.all().order_by('-created_at')
    serializer = OrderStatusHistorySerializer(history, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel order and process refund if paid"""
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.user not in [order.buyer, order.seller]:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    if order.status in ['completed', 'cancelled', 'refunded']:
        return Response({"error": "Order cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
    
    with db_transaction.atomic():
        old_status = order.status
        
        if order.status == 'paid' and order.funds_held:
            profile = Profile.objects.select_for_update().get(user=order.buyer)
            balance_before = profile.wallet_balance
            Profile.objects.filter(user=order.buyer).update(wallet_balance=F('wallet_balance') + order.total_amount)
            profile.refresh_from_db()
            
            WalletTransaction.objects.create(user=order.buyer, transaction_type='credit', amount=order.total_amount, source='refund', related_order=order, balance_before=balance_before, balance_after=profile.wallet_balance)
        
        order.status = 'cancelled'
        order.save()
        
        if order.item.status == 'pending':
            order.item.status = 'active'
            order.item.save()
        
        OrderStatusHistory.objects.create(order=order, from_status=old_status, to_status='cancelled', changed_by=request.user, notes='Order cancelled by user')
    
    return Response({"message": "Order cancelled successfully", "refund_amount": str(order.total_amount) if old_status == 'paid' else "0.00"})
