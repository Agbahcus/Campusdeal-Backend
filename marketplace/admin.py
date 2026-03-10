from django.contrib import admin
from .models import (
    ItemCategory, 
    ItemListing, 
    Order, 
    OrderStatusHistory, 
    WalletTransaction, 
    ItemReview,
    RefundRequest,
    HostelListing,
    Withdrawal
)


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(ItemListing)
class ItemListingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'seller', 
        'price', 
        'condition', 
        'location', 
        'status',
        'views_count',
        'created_at'
    ]
    list_filter = ['status', 'condition', 'location', 'created_at']
    search_fields = ['title', 'description', 'seller__username']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('seller', 'title', 'description', 'category', 'condition')
        }),
        ('Pricing', {
            'fields': ('price', 'is_negotiable')
        }),
        ('Location & Delivery', {
            'fields': (
                'location', 
                'allow_campusdeal_delivery', 
                'allow_seller_delivery', 
                'allow_pickup'
            )
        }),
        ('Images', {
            'fields': ('image_1', 'image_2', 'image_3')
        }),
        ('Status & Metrics', {
            'fields': ('status', 'views_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id',
        'item',
        'buyer',
        'seller',
        'total_amount',
        'status',
        'delivery_method',
        'created_at'
    ]
    list_filter = ['status', 'delivery_method', 'payment_method', 'created_at']
    search_fields = ['order_id', 'buyer__username', 'seller__username', 'item__title']
    readonly_fields = [
        'order_id', 
        'created_at', 
        'paid_at', 
        'delivered_at', 
        'completed_at'
    ]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'item', 'buyer', 'seller', 'status')
        }),
        ('Delivery', {
            'fields': (
                'delivery_method', 
                'delivery_address', 
                'delivery_phone', 
                'waybill_number'
            )
        }),
        ('Financials', {
            'fields': (
                'item_price', 
                'service_fee', 
                'delivery_fee', 
                'total_amount'
            )
        }),
        ('Payment', {
            'fields': (
                'payment_method',
                'paystack_reference',
                'paystack_access_code',
            )
        }),
        ('Escrow', {
            'fields': (
                'funds_held',
                'funds_released_to_seller',
                'payout_reference'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at', 'delivered_at', 'completed_at')
        }),
    )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'from_status', 'to_status', 'changed_by', 'created_at']
    list_filter = ['to_status', 'created_at']
    search_fields = ['order__order_id']
    readonly_fields = ['created_at']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'transaction_type',
        'amount',
        'source',
        'balance_after',
        'created_at'
    ]
    list_filter = ['transaction_type', 'source', 'created_at']
    search_fields = ['user__username', 'reference']
    readonly_fields = ['created_at']


@admin.register(ItemReview)
class ItemReviewAdmin(admin.ModelAdmin):
    list_display = ['order', 'reviewer', 'reviewee', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'reviewee__username', 'comment']
    readonly_fields = ['created_at']


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'requester',
        'reason',
        'status',
        'created_at',
        'resolved_at'
    ]
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['order__order_id', 'requester__username', 'detailed_explanation']
    readonly_fields = ['created_at', 'resolved_at']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('order', 'requester', 'reason', 'detailed_explanation')
        }),
        ('Evidence', {
            'fields': ('evidence_image_1', 'evidence_image_2', 'evidence_image_3')
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'resolved_at')
        }),
    )


@admin.register(HostelListing)
class HostelListingAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'landlord',
        'location',
        'rent_per_month',
        'is_verified',
        'is_active',
        'views_count',
        'created_at'
    ]
    list_filter = ['is_verified', 'is_active', 'location', 'created_at']
    search_fields = ['name', 'address', 'description', 'landlord__username']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('landlord', 'name', 'description')
        }),
        ('Location', {
            'fields': ('location', 'address', 'latitude', 'longitude')
        }),
        ('Pricing & Contact', {
            'fields': ('rent_per_month', 'contact_phone')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('Images', {
            'fields': ('image_1', 'image_2', 'image_3')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_notes', 'is_active')
        }),
        ('Metrics', {
            'fields': ('views_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'amount', 'withdrawal_fee', 'net_amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'reference', 'transfer_code']
    readonly_fields = ['transfer_code', 'reference', 'wallet_balance_before', 'wallet_balance_after', 'created_at', 'completed_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'bank_account')
        }),
        ('Amount Details', {
            'fields': ('amount', 'withdrawal_fee', 'net_amount')
        }),
        ('Paystack Details', {
            'fields': ('transfer_code', 'reference', 'status', 'failure_reason')
        }),
        ('Wallet Balance', {
            'fields': ('wallet_balance_before', 'wallet_balance_after')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )