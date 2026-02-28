from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import ItemCategory, ItemListing, ItemReview
from .serializers import (
    ItemCategorySerializer,
    ItemListingSerializer,
    ItemListingListSerializer,
    ItemReviewSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============ ITEM CATEGORIES ============

@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    """
    List all active item categories
    
    GET /api/marketplace/categories/
    """
    categories = ItemCategory.objects.filter(is_active=True)
    serializer = ItemCategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    """
    Create new category (Admin only in production)
    
    POST /api/marketplace/categories/
    """
    # TODO: Add admin permission check
    serializer = ItemCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============ ITEM LISTINGS ============

@api_view(['GET'])
@permission_classes([AllowAny])
def browse_listings(request):
    """
    Browse all active listings with filters
    
    GET /api/marketplace/listings/
    
    Query params:
    - location: ilorin|malete|offa
    - category: category_id
    - condition: new|fairly_used|used
    - min_price: decimal
    - max_price: decimal
    - search: text query (searches title and description)
    - page: page number
    """
    listings = ItemListing.objects.filter(status='active').select_related(
        'seller', 'seller__profile', 'category'
    )
    
    # Apply filters
    location = request.query_params.get('location')
    if location:
        listings = listings.filter(location=location)
    
    category_id = request.query_params.get('category')
    if category_id:
        listings = listings.filter(category_id=category_id)
    
    condition = request.query_params.get('condition')
    if condition:
        listings = listings.filter(condition=condition)
    
    min_price = request.query_params.get('min_price')
    if min_price:
        listings = listings.filter(price__gte=min_price)
    
    max_price = request.query_params.get('max_price')
    if max_price:
        listings = listings.filter(price__lte=max_price)
    
    search = request.query_params.get('search')
    if search:
        listings = listings.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Pagination
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(listings, request)
    
    if page is not None:
        serializer = ItemListingListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = ItemListingListSerializer(listings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_listing(request):
    """
    Create a new item listing
    
    POST /api/marketplace/listings/
    
    Body (multipart/form-data):
    {
        "title": "Engineering Textbook",
        "description": "Used calculus book in good condition",
        "category": 1,
        "condition": "fairly_used",
        "price": "2000.00",
        "is_negotiable": true,
        "location": "ilorin",
        "allow_pickup": true,
        "allow_seller_delivery": false,
        "allow_campusdeal_delivery": false,
        "image_1": <file>,
        "image_2": <file> (optional),
        "image_3": <file> (optional)
    }
    """
    # Check if user's phone is verified
    if not request.user.profile.phone_verified:
        return Response(
            {"error": "Phone number must be verified before creating listings"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if user is suspended
    if request.user.profile.is_suspended:
        return Response(
            {"error": "Your account is suspended"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ItemListingSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        listing = serializer.save()
        return Response(
            ItemListingSerializer(listing).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_listing(request, listing_id):
    """
    Get single listing detail
    
    GET /api/marketplace/listings/{id}/
    """
    listing = get_object_or_404(
        ItemListing.objects.select_related('seller', 'seller__profile', 'category'),
        id=listing_id
    )
    
    # Increment view count (don't count seller's own views)
    if not request.user.is_authenticated or request.user != listing.seller:
        listing.increment_views()
    
    serializer = ItemListingSerializer(listing)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_listing(request, listing_id):
    """
    Update listing (seller only)
    
    PATCH /api/marketplace/listings/{id}/
    """
    listing = get_object_or_404(ItemListing, id=listing_id)
    
    # Check ownership
    if listing.seller != request.user:
        return Response(
            {"error": "You don't have permission to edit this listing"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Don't allow editing sold items
    if listing.status == 'sold':
        return Response(
            {"error": "Cannot edit sold items"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ItemListingSerializer(
        listing, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_listing(request, listing_id):
    """
    Remove/deactivate listing (seller only)
    
    DELETE /api/marketplace/listings/{id}/
    """
    listing = get_object_or_404(ItemListing, id=listing_id)
    
    # Check ownership
    if listing.seller != request.user:
        return Response(
            {"error": "You don't have permission to delete this listing"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Don't allow deleting items with pending orders
    if listing.status == 'pending':
        return Response(
            {"error": "Cannot delete listing with pending orders"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Soft delete - mark as removed instead of actually deleting
    listing.status = 'removed'
    listing.save()
    
    return Response(
        {"message": "Listing removed successfully"},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_listings(request):
    """
    Get current user's listings
    
    GET /api/marketplace/my-listings/
    
    Query params:
    - status: active|pending|sold|removed
    """
    listings = ItemListing.objects.filter(seller=request.user).select_related('category')
    
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        listings = listings.filter(status=status_filter)
    
    # Order by newest first
    listings = listings.order_by('-created_at')
    
    # Pagination
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(listings, request)
    
    if page is not None:
        serializer = ItemListingListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = ItemListingListSerializer(listings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_listings(request, user_id):
    """
    Get listings by specific user
    
    GET /api/marketplace/users/{user_id}/listings/
    """
    listings = ItemListing.objects.filter(
        seller_id=user_id,
        status='active'
    ).select_related('category')
    
    serializer = ItemListingListSerializer(listings, many=True)
    return Response(serializer.data)