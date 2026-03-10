from django.contrib import admin
from .models import Profile, BankAccount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'phone_number', 
        'user_type', 
        'primary_location', 
        'phone_verified',
        'wallet_balance',
        'rating',
        'chat_strikes',
        'is_suspended'
    ]
    list_filter = [
        'user_type', 
        'primary_location', 
        'phone_verified', 
        'is_suspended'
    ]
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'user_type', 'phone_number', 'phone_verified')
        }),
        ('Location', {
            'fields': ('primary_location',)
        }),
        ('Profile', {
            'fields': ('profile_picture', 'university', 'bio')
        }),
        ('Wallet & Reputation', {
            'fields': ('wallet_balance', 'rating', 'total_ratings')
        }),
        ('Moderation', {
            'fields': ('chat_strikes', 'is_suspended', 'suspension_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_name', 'account_number', 'bank_name', 'is_primary', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'is_primary', 'bank_name']
    search_fields = ['user__username', 'account_name', 'account_number']
    readonly_fields = ['created_at', 'updated_at', 'recipient_code']