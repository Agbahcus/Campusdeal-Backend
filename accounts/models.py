from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    """Extended user profile with CampusDeal-specific fields"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('landlord', 'Landlord'),
    ]
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='student'
    )
    
    # Contact & Verification
    phone_number = PhoneNumberField(unique=True, region='NG')
    phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)
    
    # Location
    LOCATION_CHOICES = [
        ('ilorin', 'Ilorin'),
        ('malete', 'Malete'),
        ('offa', 'Offa'),
    ]
    primary_location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    
    # Profile
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True
    )
    university = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    
    # Wallet & Reputation
    wallet_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=5.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Moderation
    chat_strikes = models.PositiveSmallIntegerField(default=0)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['primary_location']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.phone_number}"
    
    def update_rating(self, new_rating):
        """Update user's average rating"""
        total = (self.rating * self.total_ratings) + new_rating
        self.total_ratings += 1
        self.rating = total / self.total_ratings
        self.save()