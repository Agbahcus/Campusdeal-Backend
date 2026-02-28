from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import HostelListing
from .hostel_serializers import (
    HostelListingSerializer,
    HostelListingPublicSerializer,
    HostelListingAdminSerializer,
    HostelVerificationSerializer
)


class HostelPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


# ============ PUBLIC ENDPOINTS (Students) ============

@api_view(['GET'])
@permission_classes([AllowAny])
def browse_hostels(request):
    """
    Browse verified hostel listings (Students)
    
    GET /api/marketplace/hostels/
    
    Query params:
    - location: ilorin|malete|offa
    - min_rent: decimal
    - max_rent: decimal
    - amenities: comma-separated (e.g., "WiFi,Security,Laundry")
    - search: text query
    - page: page number
    """
    # Only show verified and active hostels to students
    hostels = HostelListing.objects.filter(
        is_verified=True,
        is_active=True
    ).select_related('landlord', 'landlord__profile')
    
    # Apply filters
    location = request.query_params.get('location')
    if location:
        hostels = hostels.filter(location=location)
    
    min_rent = request.query_params.get('min_rent')
    if min_rent:
        hostels = hostels.filter(rent_per_month__gte=min_rent)
    
    max_rent = request.query_params.get('max_rent')
    if max_rent:
        hostels = hostels.filter(rent_per_month__lte=max_rent)
    
    # Filter by amenities
    amenities = request.query_params.get('amenities')
    if amenities:
        amenity_list = [a.strip() for a in amenities.split(',')]
        for amenity in amenity_list:
            hostels = hostels.filter(amenities__contains=[amenity])
    
    # Search in name, address, description
    search = request.query_params.get('search')
    if search:
        hostels = hostels.filter(
            Q(name__icontains=search) |
            Q(address__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Order by newest first
    hostels = hostels.order_by('-created_at')
    
    # Pagination
    paginator = HostelPagination()
    page = paginator.paginate_queryset(hostels, request)
    
    if page is not None:
        serializer = HostelListingPublicSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = HostelListingPublicSerializer(hostels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_hostel(request, hostel_id):
    """
    Get single hostel detail
    
    GET /api/marketplace/hostels/{id}/
    """
    hostel = get_object_or_404(
        HostelListing.objects.select_related('landlord', 'landlord__profile'),
        id=hostel_id,
        is_verified=True,
        is_active=True
    )
    
    # Increment view count (don't count landlord's own views)
    if not request.user.is_authenticated or request.user != hostel.landlord:
        hostel.views_count += 1
        hostel.save(update_fields=['views_count'])
    
    serializer = HostelListingPublicSerializer(hostel)
    return Response(serializer.data)


# ============ LANDLORD ENDPOINTS ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_hostel(request):
    """
    Create hostel listing (Landlord only)
    
    POST /api/marketplace/hostels/create/
    Content-Type: multipart/form-data
    """
    # Check user is landlord
    if request.user.profile.user_type != 'landlord':
        return Response(
            {"error": "Only landlords can create hostel listings"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check phone verified
    if not request.user.profile.phone_verified:
        return Response(
            {"error": "Phone number must be verified before creating listings"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if suspended
    if request.user.profile.is_suspended:
        return Response(
            {"error": "Your account is suspended"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = HostelListingSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        hostel = serializer.save()
        
        return Response({
            "message": "Hostel listing created successfully. It will be visible to students after admin verification.",
            "hostel": HostelListingSerializer(hostel).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_hostels(request):
    """
    Get current landlord's hostel listings
    
    GET /api/marketplace/hostels/my-listings/
    """
    # Check user is landlord
    if request.user.profile.user_type != 'landlord':
        return Response(
            {"error": "Only landlords can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    hostels = HostelListing.objects.filter(
        landlord=request.user
    ).order_by('-created_at')
    
    # Filter by verification status if provided
    is_verified = request.query_params.get('is_verified')
    if is_verified is not None:
        is_verified_bool = is_verified.lower() == 'true'
        hostels = hostels.filter(is_verified=is_verified_bool)
    
    serializer = HostelListingSerializer(hostels, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_hostel(request, hostel_id):
    """
    Update hostel listing (Landlord only - own listings)
    
    PATCH /api/marketplace/hostels/{id}/update/
    """
    hostel = get_object_or_404(HostelListing, id=hostel_id)
    
    # Check ownership
    if hostel.landlord != request.user:
        return Response(
            {"error": "You don't have permission to edit this listing"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = HostelListingSerializer(
        hostel,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    
    if serializer.is_valid():
        # If listing was verified and landlord updates it, mark for re-verification
        if hostel.is_verified and any(field in request.data for field in ['name', 'address', 'description', 'rent_per_month']):
            hostel.is_verified = False
            hostel.verification_notes = "Re-verification needed after landlord update"
        
        serializer.save()
        
        return Response({
            "message": "Hostel listing updated successfully",
            "hostel": serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_hostel(request, hostel_id):
    """
    Deactivate hostel listing (Landlord only)
    
    DELETE /api/marketplace/hostels/{id}/delete/
    """
    hostel = get_object_or_404(HostelListing, id=hostel_id)
    
    # Check ownership
    if hostel.landlord != request.user:
        return Response(
            {"error": "You don't have permission to delete this listing"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Soft delete - mark as inactive
    hostel.is_active = False
    hostel.save()
    
    return Response(
        {"message": "Hostel listing deactivated successfully"},
        status=status.HTTP_200_OK
    )


# ============ ADMIN ENDPOINTS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_hostels(request):
    """
    Get hostels pending verification (Admin only)
    
    GET /api/marketplace/hostels/admin/pending/
    """
    # Check admin permission
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    hostels = HostelListing.objects.filter(
        is_verified=False,
        is_active=True
    ).select_related('landlord', 'landlord__profile').order_by('-created_at')
    
    serializer = HostelListingAdminSerializer(hostels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_hostels_admin(request):
    """
    Get all hostel listings (Admin only)
    
    GET /api/marketplace/hostels/admin/all/
    """
    # Check admin permission
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    hostels = HostelListing.objects.select_related(
        'landlord',
        'landlord__profile'
    ).order_by('-created_at')
    
    # Apply filters
    is_verified = request.query_params.get('is_verified')
    if is_verified is not None:
        hostels = hostels.filter(is_verified=is_verified.lower() == 'true')
    
    is_active = request.query_params.get('is_active')
    if is_active is not None:
        hostels = hostels.filter(is_active=is_active.lower() == 'true')
    
    location = request.query_params.get('location')
    if location:
        hostels = hostels.filter(location=location)
    
    serializer = HostelListingAdminSerializer(hostels, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_hostel(request, hostel_id):
    """
    Verify or reject hostel listing (Admin only)
    
    POST /api/marketplace/hostels/{id}/verify/
    """
    # Check admin permission
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    hostel = get_object_or_404(HostelListing, id=hostel_id)
    
    serializer = HostelVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Update verification status
    hostel.is_verified = serializer.validated_data['is_verified']
    hostel.verification_notes = serializer.validated_data.get('verification_notes', '')
    
    if 'is_active' in serializer.validated_data:
        hostel.is_active = serializer.validated_data['is_active']
    
    hostel.save()
    
    action = "approved" if hostel.is_verified else "rejected"
    
    return Response({
        "message": f"Hostel listing {action} successfully",
        "hostel": HostelListingAdminSerializer(hostel).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hostel_stats(request):
    """
    Get hostel statistics (Admin only)
    
    GET /api/marketplace/hostels/admin/stats/
    """
    # Check admin permission
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    total_hostels = HostelListing.objects.count()
    verified_hostels = HostelListing.objects.filter(is_verified=True).count()
    pending_hostels = HostelListing.objects.filter(is_verified=False, is_active=True).count()
    active_hostels = HostelListing.objects.filter(is_active=True).count()
    
    by_location = {}
    for location_code, location_name in HostelListing.LOCATION_CHOICES:
        by_location[location_name] = HostelListing.objects.filter(
            location=location_code,
            is_verified=True,
            is_active=True
        ).count()
    
    return Response({
        "total_hostels": total_hostels,
        "verified_hostels": verified_hostels,
        "pending_verification": pending_hostels,
        "active_hostels": active_hostels,
        "by_location": by_location
    })