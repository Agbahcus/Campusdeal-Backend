from django.urls import path
from . import views
from . import order_views
from . import wallet_views
from . import review_views
from . import refund_views
from . import hostel_views

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
    path('orders/initiate/', order_views.initiate_order, name='initiate-order'),
    path('orders/', order_views.list_orders, name='list-orders'),
    path('orders/<str:order_id>/', order_views.get_order, name='get-order'),
    path('orders/<str:order_id>/checkout/', order_views.checkout_order, name='checkout-order'),
    path('orders/<str:order_id>/update-status/', order_views.update_order_status, name='update-order-status'),
    path('orders/<str:order_id>/confirm-delivery/', order_views.confirm_delivery, name='confirm-delivery'),
    path('orders/<str:order_id>/status-history/', order_views.order_status_history, name='order-status-history'),
    path('orders/<str:order_id>/review/', review_views.get_order_review, name='order-review'),
    
    # Payments
    path('payments/verify/', order_views.verify_payment, name='verify-payment'),
    path('payments/webhook/', order_views.paystack_webhook, name='paystack-webhook'),
    
    # Wallet
    path('wallet/balance/', wallet_views.get_wallet_balance, name='wallet-balance'),
    path('wallet/transactions/', wallet_views.get_wallet_transactions, name='wallet-transactions'),
    path('wallet/add-funds/', wallet_views.add_funds_to_wallet, name='add-funds'),
    path('wallet/verify-deposit/', wallet_views.verify_wallet_deposit, name='verify-deposit'),
    path('wallet/withdraw/', wallet_views.request_withdrawal, name='withdraw'),
    path('wallet/banks/', wallet_views.list_banks, name='list-banks'),
    
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