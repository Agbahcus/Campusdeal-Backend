from rest_framework import serializers
from .models import HostelListing
from accounts.serializers import UserSerializer


class HostelListingSerializer(serializers.ModelSerializer):
    """Full hostel listing serializer"""
    landlord = UserSerializer(read_only=True)
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)
    landlord_phone = serializers.CharField(source='landlord.profile.phone_number', read_only=True)
    
    class Meta:
        model = HostelListing
        fields = [
            'id',
            'landlord',
            'landlord_name',
            'landlord_phone',
            'name',
            'address',
            'description',
            'location',
            'latitude',
            'longitude',
            'rent_per_month',
            'amenities',
            'contact_phone',
            'image_1',
            'image_2',
            'image_3',
            'is_active',
            'is_verified',
            'verification_notes',
            'views_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'landlord',
            'is_active',
            'is_verified',
            'verification_notes',
            'views_count',
            'created_at',
            'updated_at'
        ]
    
    def create(self, validated_data):
        """Create hostel listing with authenticated landlord"""
        request = self.context.get('request')
        validated_data['landlord'] = request.user
        return super().create(validated_data)


class HostelListingPublicSerializer(serializers.ModelSerializer):
    """Public hostel listing serializer for students (verified only)"""
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)
    landlord_rating = serializers.DecimalField(
        source='landlord.profile.rating',
        max_digits=3,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = HostelListing
        fields = [
            'id',
            'landlord_name',
            'landlord_rating',
            'name',
            'address',
            'description',
            'location',
            'latitude',
            'longitude',
            'rent_per_month',
            'amenities',
            'contact_phone',
            'image_1',
            'image_2',
            'image_3',
            'views_count',
            'created_at'
        ]


class HostelListingAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for verification workflow"""
    landlord_name = serializers.CharField(source='landlord.get_full_name', read_only=True)
    landlord_phone = serializers.CharField(source='landlord.profile.phone_number', read_only=True)
    landlord_email = serializers.CharField(source='landlord.email', read_only=True)
    
    class Meta:
        model = HostelListing
        fields = [
            'id',
            'landlord',
            'landlord_name',
            'landlord_phone',
            'landlord_email',
            'name',
            'address',
            'description',
            'location',
            'latitude',
            'longitude',
            'rent_per_month',
            'amenities',
            'contact_phone',
            'image_1',
            'image_2',
            'image_3',
            'is_active',
            'is_verified',
            'verification_notes',
            'views_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'landlord', 'created_at', 'updated_at', 'views_count']


class HostelVerificationSerializer(serializers.Serializer):
    """Serializer for admin verification actions"""
    is_verified = serializers.BooleanField()
    verification_notes = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)