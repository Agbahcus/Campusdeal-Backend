from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('auth/register/', views.register_user, name='register'),
    path('auth/verify-phone/', views.verify_phone, name='verify-phone'),
    path('auth/resend-code/', views.resend_verification_code, name='resend-code'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/request-password-reset/', views.request_password_reset, name='request-password-reset'),
    path('auth/confirm-password-reset/', views.confirm_password_reset, name='confirm-password-reset'),
    path('auth/refresh-token/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile
    path('users/me/', views.user_profile, name='my-profile'),
    path('users/<int:user_id>/profile/', views.get_user_profile, name='user-profile'),

    # Device tokens & Notifications
    path('device-token/', views.register_device_token, name='register-device-token'),
    path('notifications/', views.list_notifications, name='list-notifications'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark-all-read'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
]