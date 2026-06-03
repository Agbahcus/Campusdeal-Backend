from django.urls import path
from . import views
from . import order_views
from . import wallet_views
from . import review_views
from . import refund_views
from . import hostel_views
from . import withdrawal_views
from . import admin_views
from django.conf import settings
from . import setup_views  # TEMPORARY - DELETE AFTER SETUP

app_name = 'marketplace'

urlpatterns = [
    # Categories
    path('categories/', views.list_categories, name='list-categories'),
    path('categories/create/', views.create_category, name='create-category'),
    
    # Listings - Browse & Search
    path('listings/', views.browse_listings, name='browse-listings'),
    path('listings/create/', views.create_listing, name='create-listing'),
    path('listings/<int:listing_id>/', views.get_listing, name='get-listing'),
    path('listings/<int:listing_id>/update/', views.update_listing, name='update-listing'),
    path('listings/<int:listing_id>/delete/', views.delete_listing, name='delete-listing'),
    
    # User Listings
    path('my-listings/', views.my_listings, name='my-listings'),
    path('users/<int:user_id>/listings/', views.user_listings, name='user-listings'),
    
    # Orders
    path('orders/buy/', order_views.buyer_order, name='buyer-order'),
    path('orders/initiate/', order_views.initiate_order, name='initiate-order'),
    path('orders/', order_views.list_orders, name='list-orders'),
    path('orders/<str:order_id>/', order_views.get_order, name='get-order'),
    path('orders/<str:order_id>/checkout/', order_views.checkout_order, name='checkout-order'),
    path('orders/<str:order_id>/update-status/', order_views.update_order_status, name='update-order-status'),
    path('orders/<str:order_id>/confirm-delivery/', order_views.confirm_delivery, name='confirm-delivery'),
    path('orders/<str:order_id>/cancel/', order_views.cancel_order, name='cancel-order'),
    path('orders/<str:order_id>/status-history/', order_views.order_status_history, name='order-status-history'),
    path('orders/<str:order_id>/review/', review_views.get_order_review, name='order-review'),
    
    # Payments
    path('payments/verify/', order_views.verify_payment, name='verify-payment'),
    path('payments/webhook/', order_views.paystack_webhook, name='paystack-webhook'),
    # Admin financials
    path('admin/financials/', admin_views.platform_financial_summary, name='platform-financials'),
    path('admin/withdraw-profit/', admin_views.withdraw_platform_profit, name='withdraw-platform-profit'),
    
    # Wallet
    path('wallet/balance/', wallet_views.get_wallet_balance, name='wallet-balance'),
    path('wallet/transactions/', wallet_views.get_wallet_transactions, name='wallet-transactions'),
    path('wallet/add-funds/', wallet_views.add_funds_to_wallet, name='add-funds'),
    path('wallet/verify-deposit/', wallet_views.verify_wallet_deposit, name='verify-deposit'),
    path('wallet/banks/', wallet_views.list_banks, name='list-banks'),
    
    # Withdrawals
    path('wallet/verify-account/', withdrawal_views.verify_bank_account, name='verify-account'),
    path('wallet/add-bank-account/', withdrawal_views.add_bank_account, name='add-bank-account'),
    path('wallet/bank-accounts/', withdrawal_views.list_bank_accounts, name='list-bank-accounts'),
    path('wallet/bank-accounts/<int:account_id>/set-primary/', withdrawal_views.set_primary_bank_account, name='set-primary-account'),
    path('wallet/bank-accounts/<int:account_id>/', withdrawal_views.delete_bank_account, name='delete-bank-account'),
    path('wallet/withdraw/', withdrawal_views.withdraw_funds, name='withdraw-funds'),
    path('wallet/withdrawals/', withdrawal_views.withdrawal_history, name='withdrawal-history'),
    path('wallet/withdrawal-fees/', withdrawal_views.get_withdrawal_fees, name='withdrawal-fees'),
    
    # Reviews
    path('reviews/', review_views.create_review, name='create-review'),
    path('users/<int:user_id>/reviews/', review_views.get_user_reviews, name='user-reviews'),
    
    # Refunds
    path('orders/<str:order_id>/request-refund/', refund_views.request_refund, name='request-refund'),
    path('orders/<str:order_id>/refund-request/', refund_views.get_refund_request, name='get-refund-request'),
    path('refunds/<int:refund_id>/approve/', refund_views.approve_refund, name='approve-refund'),
    path('refunds/<int:refund_id>/reject/', refund_views.reject_refund, name='reject-refund'),
    path('refunds/pending/', refund_views.list_pending_refunds, name='pending-refunds'),
    # Hostels - Public (Students)
    path('hostels/', hostel_views.browse_hostels, name='browse-hostels'),
    path('hostels/<int:hostel_id>/', hostel_views.get_hostel, name='get-hostel'),
    
    # Hostels - Landlord
    path('hostels/create/', hostel_views.create_hostel, name='create-hostel'),
    path('hostels/my-listings/', hostel_views.my_hostels, name='my-hostels'),
    path('hostels/<int:hostel_id>/update/', hostel_views.update_hostel, name='update-hostel'),
    path('hostels/<int:hostel_id>/delete/', hostel_views.delete_hostel, name='delete-hostel'),
    
    # Hostels - Admin
    path('hostels/admin/pending/', hostel_views.pending_hostels, name='pending-hostels'),
    path('hostels/admin/all/', hostel_views.all_hostels_admin, name='all-hostels-admin'),
    path('hostels/<int:hostel_id>/verify/', hostel_views.verify_hostel, name='verify-hostel'),
    path('hostels/admin/stats/', hostel_views.hostel_stats, name='hostel-stats'),
    
]

if settings.DEBUG:
    urlpatterns.append(
        path('setup/', setup_views.initial_setup, name='initial-setup')
    )
