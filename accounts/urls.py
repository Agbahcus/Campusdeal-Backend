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
    path('auth/refresh-token/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile
    path('users/me/', views.user_profile, name='my-profile'),
    path('users/<int:user_id>/profile/', views.get_user_profile, name='user-profile'),
]