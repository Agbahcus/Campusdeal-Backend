from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ItemCategory, ItemListing, Order, ItemReview, WalletTransaction
from accounts.serializers import UserSerializer


class ItemCategorySerializer(serializers.ModelSerializer):
    """Serializer for item categories"""
    class Meta:
        model = ItemCategory
        fields = ['id', 'name', 'icon', 'is_active']
        read_only_fields = ['id']


class ItemListingSerializer(serializers.ModelSerializer):
    """Serializer for item listings"""
    seller = UserSerializer(read_only=True)
    seller_id = serializers.IntegerField(write_only=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ItemListing
        fields = [
            'id',
            'seller',
            'seller_id',
            'title',
            'description',
            'category',
            'category_name',
            'condition',
            'price',
            'is_negotiable',
            'location',
            'allow_campusdeal_delivery',
            'allow_seller_delivery',
            'allow_pickup',
            'image_1',
            'image_2',
            'image_3',
            'status',
            'views_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'seller', 'views_count', 'created_at', 'updated_at', 'status']
    
    def validate(self, data):
        """Validate that at least one delivery option is selected"""
        allow_campusdeal = data.get('allow_campusdeal_delivery', False)
        allow_seller = data.get('allow_seller_delivery', False)
        allow_pickup = data.get('allow_pickup', False)
        
        if not (allow_campusdeal or allow_seller or allow_pickup):
            raise serializers.ValidationError(
                "At least one delivery option must be selected"
            )
        
        return data
    
    def create(self, validated_data):
        """Create listing with authenticated user as seller"""
        request = self.context.get('request')
        validated_data['seller'] = request.user
        return super().create(validated_data)


class ItemListingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing browsing (less data)"""
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    seller_rating = serializers.DecimalField(
        source='seller.profile.rating', 
        max_digits=3, 
        decimal_places=2, 
        read_only=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ItemListing
        fields = [
            'id',
            'title',
            'price',
            'is_negotiable',
            'condition',
            'location',
            'image_1',
            'category_name',
            'seller_name',
            'seller_rating',
            'views_count',
            'created_at'
        ]


class ItemReviewSerializer(serializers.ModelSerializer):
    """Serializer for item reviews"""
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.get_full_name', read_only=True)
    
    class Meta:
        model = ItemReview
        fields = [
            'id',
            'order',
            'reviewer',
            'reviewer_name',
            'reviewee',
            'reviewee_name',
            'rating',
            'comment',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for wallet transactions"""
    class Meta:
        model = WalletTransaction
        fields = [
            'id',
            'transaction_type',
            'amount',
            'source',
            'reference',
            'balance_before',
            'balance_after',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']