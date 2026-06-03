from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ItemCategory, ItemListing
from .serializers import ItemCategorySerializer, ItemListingListSerializer
from .views import _seed_default_categories


@api_view(['GET'])
@permission_classes([AllowAny])
def home_feed(request):
    """
    Single endpoint for mobile app home screen.
    Returns featured listings, categories, and user stats in one call.

    GET /api/marketplace/feed/
    """
    _seed_default_categories()

    listings = ItemListing.objects.filter(status='active').select_related(
        'seller', 'seller__profile', 'category'
    ).order_by('-created_at')[:12]

    categories = ItemCategory.objects.filter(is_active=True)

    user_stats = {}
    unread_notifications = 0

    if request.user.is_authenticated:
        from .models import Order
        from communication.models import Message, Chat
        from django.db.models import Q
        from accounts.models import Notification

        user_stats = {
            'pending_orders': Order.objects.filter(
                Q(buyer=request.user) | Q(seller=request.user),
                status__in=['payment_pending', 'paid', 'seller_preparing', 'with_courier', 'delivered']
            ).count(),
            'wallet_balance': str(request.user.profile.wallet_balance),
            'unread_messages': Message.objects.filter(
                chat__in=Chat.objects.filter(
                    Q(participant_1=request.user) | Q(participant_2=request.user)
                ),
                is_read=False
            ).exclude(sender=request.user).count(),
        }
        unread_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

    return Response({
        'featured_listings': ItemListingListSerializer(listings, many=True).data,
        'categories': ItemCategorySerializer(categories, many=True).data,
        'user_stats': user_stats,
        'unread_notifications': unread_notifications,
    })
