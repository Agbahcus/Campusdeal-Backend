from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Order, OrderStatusHistory
from .serializers import ItemListingSerializer
from accounts.serializers import UserSerializer
from decimal import Decimal


class OrderSerializer(serializers.ModelSerializer):
    """Full order serializer with all details"""
    item = ItemListingSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'item',
            'buyer',
            'seller',
            'delivery_method',
            'delivery_address',
            'delivery_phone',
            'waybill_number',
            'item_price',
            'service_fee',
            'delivery_fee',
            'total_amount',
            'paystack_reference',
            'payment_method',
            'status',
            'funds_held',
            'funds_released_to_seller',
            'created_at',
            'paid_at',
            'delivered_at',
            'completed_at'
        ]
        read_only_fields = [
            'id',
            'order_id',
            'item',
            'buyer',
            'seller',
            'item_price',
            'service_fee',
            'delivery_fee',
            'total_amount',
            'paystack_reference',
            'payment_method',
            'status',
            'funds_held',
            'funds_released_to_seller',
            'created_at',
            'paid_at',
            'delivered_at',
            'completed_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order lists"""
    item_title = serializers.CharField(source='item.title', read_only=True)
    item_image = serializers.ImageField(source='item.image_1', read_only=True)
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'item_title',
            'item_image',
            'buyer_name',
            'seller_name',
            'total_amount',
            'status',
            'delivery_method',
            'created_at'
        ]


class InitiateOrderSerializer(serializers.Serializer):
    """Serializer for seller to initiate order"""
    item_id = serializers.IntegerField()
    buyer_id = serializers.IntegerField()
    delivery_method = serializers.ChoiceField(
        choices=['campusdeal', 'seller', 'pickup']
    )


class CheckoutOrderSerializer(serializers.Serializer):
    """Serializer for buyer checkout"""
    payment_method = serializers.ChoiceField(choices=['wallet', 'paystack'])
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    delivery_phone = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate delivery details are provided for delivery orders"""
        order = self.context.get('order')
        
        if order and order.delivery_method in ['campusdeal', 'seller']:
            if not data.get('delivery_address'):
                raise serializers.ValidationError({
                    'delivery_address': 'Delivery address is required for this delivery method'
                })
            if not data.get('delivery_phone'):
                raise serializers.ValidationError({
                    'delivery_phone': 'Delivery phone is required for this delivery method'
                })
        
        return data


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(
        choices=[
            'seller_preparing',
            'with_courier',
            'delivered',
            'cancelled'
        ]
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    changed_by_name = serializers.CharField(
        source='changed_by.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id',
            'from_status',
            'to_status',
            'notes',
            'changed_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentInitializationSerializer(serializers.Serializer):
    """Response for Paystack payment initialization"""
    authorization_url = serializers.URLField()
    access_code = serializers.CharField()
    reference = serializers.CharField()


class PaymentVerificationSerializer(serializers.Serializer):
    """Serializer for payment verification"""
    reference = serializers.CharField()