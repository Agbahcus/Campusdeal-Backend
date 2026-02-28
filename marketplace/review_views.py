from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction

from .models import ItemReview, Order
from .serializers import ItemReviewSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    """
    Leave a review after order completion
    
    POST /api/marketplace/reviews/
    Body: {
        "order_id": "CD1A2B3C4D5E6F7G",
        "rating": 5,
        "comment": "Great seller! Item as described."
    }
    """
    user = request.user
    order_id = request.data.get('order_id')
    rating = request.data.get('rating')
    comment = request.data.get('comment', '')
    
    # Validate order exists
    order = get_object_or_404(Order, order_id=order_id)
    
    # Check user is buyer or seller
    if user not in [order.buyer, order.seller]:
        return Response(
            {"error": "You are not part of this order"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check order is completed
    if order.status != 'completed':
        return Response(
            {"error": "Can only review completed orders"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already reviewed
    if ItemReview.objects.filter(order=order, reviewer=user).exists():
        return Response(
            {"error": "You have already reviewed this order"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError()
    except (ValueError, TypeError):
        return Response(
            {"error": "Rating must be between 1 and 5"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Determine who is being reviewed
    if user == order.buyer:
        reviewee = order.seller
    else:
        reviewee = order.buyer
    
    # Create review
    with db_transaction.atomic():
        review = ItemReview.objects.create(
            order=order,
            reviewer=user,
            reviewee=reviewee,
            rating=rating,
            comment=comment
        )
        
        # Update reviewee's rating
        reviewee.profile.update_rating(rating)
    
    return Response(
        ItemReviewSerializer(review).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_reviews(request, user_id):
    """
    Get reviews for a specific user
    
    GET /api/marketplace/users/{user_id}/reviews/
    """
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    
    reviews = ItemReview.objects.filter(
        reviewee=user
    ).select_related('reviewer', 'order').order_by('-created_at')
    
    serializer = ItemReviewSerializer(reviews, many=True)
    
    return Response({
        "user_id": user_id,
        "average_rating": str(user.profile.rating),
        "total_reviews": user.profile.total_ratings,
        "reviews": serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_review(request, order_id):
    """
    Get review for a specific order
    
    GET /api/marketplace/orders/{order_id}/review/
    """
    order = get_object_or_404(Order, order_id=order_id)
    
    # Check user is buyer or seller
    if request.user not in [order.buyer, order.seller]:
        return Response(
            {"error": "You don't have access to this order"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        review = ItemReview.objects.get(order=order)
        serializer = ItemReviewSerializer(review)
        return Response(serializer.data)
    except ItemReview.DoesNotExist:
        return Response(
            {"message": "No review yet for this order"},
            status=status.HTTP_404_NOT_FOUND
        )