from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from decimal import Decimal
import uuid

from .models import ItemListing, Offer, Order, OrderStatusHistory
from accounts.fcm_service import notify_user
from .background_jobs import run_after_commit


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_offer(request, listing_id):
    """
    Buyer sends an offer on a negotiable listing

    POST /api/marketplace/listings/{id}/offer/
    Body: {
        "proposed_price": 5000,
        "message": "Will you take 5k?",
        "delivery_method": "pickup"
    }
    """
    listing = get_object_or_404(ItemListing, id=listing_id, status='active')
    buyer = request.user

    if listing.seller == buyer:
        return Response({'error': 'You cannot make an offer on your own listing'}, status=status.HTTP_400_BAD_REQUEST)

    if not listing.is_negotiable:
        return Response({'error': 'This item is not negotiable. Use Buy Now instead.'}, status=status.HTTP_400_BAD_REQUEST)

    proposed_price = request.data.get('proposed_price')
    message = request.data.get('message', '').strip()
    delivery_method = request.data.get('delivery_method', 'pickup')

    if not proposed_price:
        return Response({'error': 'proposed_price is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        proposed_price = Decimal(str(proposed_price))
        if proposed_price <= 0:
            raise ValueError
    except Exception:
        return Response({'error': 'proposed_price must be a positive number'}, status=status.HTTP_400_BAD_REQUEST)

    if delivery_method not in ['campusdeal', 'seller', 'pickup']:
        return Response({'error': 'Invalid delivery method'}, status=status.HTTP_400_BAD_REQUEST)

    # Cancel any existing pending offer from this buyer on this item
    Offer.objects.filter(item=listing, buyer=buyer, status='pending').update(status='expired')

    offer = Offer.objects.create(
        item=listing,
        buyer=buyer,
        proposed_price=proposed_price,
        message=message,
        delivery_method=delivery_method,
    )

    # Notify seller
    run_after_commit(
        'offer-notify-seller',
        notify_user,
        listing.seller,
        'New Offer Received',
        f'{buyer.get_full_name() or buyer.username} offered ₦{proposed_price:,.0f} for your {listing.title}',
        notification_type='new_offer',
        related_id=offer.id,
    )

    return Response({
        'offer_id': offer.id,
        'status': offer.status,
        'proposed_price': str(offer.proposed_price),
        'message': 'Offer sent. Waiting for seller response.',
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_offer(request, offer_id):
    """
    Seller accepts or rejects an offer

    POST /api/marketplace/offers/{id}/respond/
    Body: {"action": "accept"} or {"action": "reject"}
    """
    offer = get_object_or_404(Offer, id=offer_id)
    seller = request.user

    if offer.item.seller != seller:
        return Response({'error': 'You do not own this listing'}, status=status.HTTP_403_FORBIDDEN)

    if offer.status != 'pending':
        return Response({'error': f'Offer is already {offer.status}'}, status=status.HTTP_400_BAD_REQUEST)

    action = request.data.get('action')
    if action not in ['accept', 'reject']:
        return Response({'error': 'action must be accept or reject'}, status=status.HTTP_400_BAD_REQUEST)

    if action == 'reject':
        offer.status = 'rejected'
        offer.save()

        run_after_commit(
            'offer-reject-notify',
            notify_user,
            offer.buyer,
            'Offer Rejected',
            f'Your offer of ₦{offer.proposed_price:,.0f} for {offer.item.title} was rejected.',
            notification_type='offer_rejected',
            related_id=offer.id,
        )

        return Response({'message': 'Offer rejected', 'offer_id': offer.id})

    # Accept — create order at agreed price
    try:
        with db_transaction.atomic():
            item = ItemListing.objects.select_for_update().get(id=offer.item.id)

            if item.status != 'active':
                return Response({'error': 'Item is no longer available'}, status=status.HTTP_400_BAD_REQUEST)

            item_price = offer.proposed_price
            service_fee = item_price * Decimal('0.035')
            delivery_fee = Decimal('500.00') if offer.delivery_method == 'campusdeal' else Decimal('0.00')
            total_amount = item_price + service_fee + delivery_fee

            order = Order.objects.create(
                item=item,
                buyer=offer.buyer,
                seller=seller,
                delivery_method=offer.delivery_method,
                item_price=item_price,
                service_fee=service_fee,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                status='payment_pending',
            )

            if offer.delivery_method == 'campusdeal':
                order.waybill_number = f'WB{uuid.uuid4().hex[:8].upper()}'
                order.save()

            item.status = 'pending'
            item.save()

            OrderStatusHistory.objects.create(
                order=order,
                from_status='',
                to_status='payment_pending',
                changed_by=seller,
            )

            offer.status = 'accepted'
            offer.order = order
            offer.save()

        # Expire all other pending offers on this item
        Offer.objects.filter(item=offer.item, status='pending').exclude(id=offer.id).update(status='expired')

        run_after_commit(
            'offer-accept-notify',
            notify_user,
            offer.buyer,
            'Offer Accepted!',
            f'Your offer of ₦{offer.proposed_price:,.0f} for {offer.item.title} was accepted. Proceed to payment.',
            notification_type='offer_accepted',
            related_id=order.order_id,
        )

        return Response({
            'message': 'Offer accepted. Order created.',
            'offer_id': offer.id,
            'order_id': order.order_id,
            'total_amount': str(total_amount),
            'breakdown': {
                'item_price': str(item_price),
                'service_fee': str(service_fee),
                'delivery_fee': str(delivery_fee),
            },
        }, status=status.HTTP_201_CREATED)

    except Exception:
        return Response({'error': 'Failed to create order from offer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_offers(request):
    """
    List offers — buyers see their sent offers, sellers see offers on their listings

    GET /api/marketplace/offers/
    Query params: ?role=buyer or ?role=seller, ?status=pending
    """
    role = request.query_params.get('role', 'buyer')
    offer_status = request.query_params.get('status')

    if role == 'seller':
        offers = Offer.objects.filter(item__seller=request.user).select_related('item', 'buyer', 'order')
    else:
        offers = Offer.objects.filter(buyer=request.user).select_related('item', 'buyer', 'order')

    if offer_status:
        offers = offers.filter(status=offer_status)

    data = [{
        'id': o.id,
        'item_id': o.item.id,
        'item_title': o.item.title,
        'item_image': o.item.image_1.url if o.item.image_1 else None,
        'buyer_id': o.buyer.id,
        'buyer_name': o.buyer.get_full_name() or o.buyer.username,
        'proposed_price': str(o.proposed_price),
        'message': o.message,
        'delivery_method': o.delivery_method,
        'status': o.status,
        'order_id': o.order.order_id if o.order else None,
        'created_at': o.created_at,
    } for o in offers]

    return Response({'count': len(data), 'results': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listing_offers(request, listing_id):
    """
    Seller views all offers on a specific listing

    GET /api/marketplace/listings/{id}/offers/
    """
    listing = get_object_or_404(ItemListing, id=listing_id, seller=request.user)
    offers = Offer.objects.filter(item=listing).select_related('buyer').order_by('-created_at')

    data = [{
        'id': o.id,
        'buyer_id': o.buyer.id,
        'buyer_name': o.buyer.get_full_name() or o.buyer.username,
        'proposed_price': str(o.proposed_price),
        'message': o.message,
        'delivery_method': o.delivery_method,
        'status': o.status,
        'order_id': o.order.order_id if o.order else None,
        'created_at': o.created_at,
    } for o in offers]

    return Response({'count': len(data), 'results': data})
