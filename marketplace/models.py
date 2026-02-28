from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class ItemCategory(models.Model):
    """Product categories"""
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon identifier for frontend
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Item Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ItemListing(models.Model):
    """Items for sale in the marketplace"""
    
    # Basic Info
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='items_for_sale'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        ItemCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='items'
    )
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('fairly_used', 'Fairly Used'),
        ('used', 'Used'),
    ]
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    is_negotiable = models.BooleanField(default=False)
    
    # Location
    LOCATION_CHOICES = [
        ('ilorin', 'Ilorin'),
        ('malete', 'Malete'),
        ('offa', 'Offa'),
    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    
    # Delivery Options (seller chooses which are available)
    allow_campusdeal_delivery = models.BooleanField(default=False)
    allow_seller_delivery = models.BooleanField(default=False)
    allow_pickup = models.BooleanField(default=True)  # Default option
    
    # Media
    image_1 = models.ImageField(upload_to='item_images/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='item_images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='item_images/', blank=True, null=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Sale'),
        ('sold', 'Sold'),
        ('removed', 'Removed'),
    ]
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    
    # Metrics
    views_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'location', '-created_at']),
            models.Index(fields=['seller', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - ₦{self.price}"
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Order(models.Model):
    """Tracks marketplace transactions with escrow"""
    
    # Unique identifier for tracking
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Core Relationships
    item = models.ForeignKey(
        ItemListing, 
        on_delete=models.PROTECT, 
        related_name='orders'
    )
    buyer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='purchases'
    )
    seller = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='sales'
    )
    
    # Delivery Choice
    DELIVERY_METHOD_CHOICES = [
        ('campusdeal', 'CampusDeal Delivery'),
        ('seller', 'Seller Delivery'),
        ('pickup', 'Pickup at Location'),
    ]
    delivery_method = models.CharField(
        max_length=15, 
        choices=DELIVERY_METHOD_CHOICES
    )
    
    # Delivery Details (for campusdeal and seller delivery)
    delivery_address = models.TextField(blank=True)
    delivery_phone = models.CharField(max_length=15, blank=True)
    waybill_number = models.CharField(
        max_length=50, 
        blank=True, 
        unique=True, 
        null=True
    )
    
    # Financials (all in Naira)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 2.5% platform fee
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Tracking
    paystack_reference = models.CharField(max_length=100, blank=True, unique=True)
    paystack_access_code = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=20, blank=True)  # 'wallet' or 'paystack'
    
    # Order Status
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('payment_pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('seller_preparing', 'Seller Preparing'),
        ('with_courier', 'With Courier'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refund_requested', 'Refund Requested'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='initiated'
    )
    
    # Escrow Management
    funds_held = models.BooleanField(default=False)  # True when payment received
    funds_released_to_seller = models.BooleanField(default=False)
    payout_reference = models.CharField(max_length=100, blank=True)  # Paystack transfer ref
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate unique order ID
            self.order_id = f"CD{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.item.title}"


class OrderStatusHistory(models.Model):
    """Track order status changes for audit trail"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='status_history'
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Order Status Histories"
    
    def __str__(self):
        return f"{self.order.order_id}: {self.from_status} → {self.to_status}"


class WalletTransaction(models.Model):
    """Track all wallet movements"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='wallet_transactions'
    )
    
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    transaction_type = models.CharField(
        max_length=10, 
        choices=TRANSACTION_TYPE_CHOICES
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    SOURCE_CHOICES = [
        ('sale', 'Sale Proceeds'),
        ('refund', 'Refund'),
        ('deposit', 'Manual Deposit'),
        ('purchase', 'Purchase Deduction'),
        ('withdrawal', 'Withdrawal'),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    
    related_order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    reference = models.CharField(max_length=100, blank=True)
    
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ₦{self.amount}"


class ItemReview(models.Model):
    """Reviews left after order completion"""
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='review'
    )
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_given'
    )
    reviewee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_received'
    )
    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['reviewee', '-created_at']),
        ]
    
    def __str__(self):
        return f"Review for {self.reviewee.username} - {self.rating}★"


class RefundRequest(models.Model):
    """Refund requests for completed orders"""
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='refund_request'
    )
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    
    REASON_CHOICES = [
        ('not_as_described', 'Item Not as Described'),
        ('damaged', 'Damaged on Delivery'),
        ('wrong_item', 'Wrong Item Received'),
        ('seller_unresponsive', 'Seller Unresponsive'),
        ('other', 'Other'),
    ]
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    detailed_explanation = models.TextField()
    
    # Evidence
    evidence_image_1 = models.ImageField(
        upload_to='refund_evidence/', 
        blank=True, 
        null=True
    )
    evidence_image_2 = models.ImageField(
        upload_to='refund_evidence/', 
        blank=True, 
        null=True
    )
    evidence_image_3 = models.ImageField(
        upload_to='refund_evidence/', 
        blank=True, 
        null=True
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Refund Processed'),
    ]
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Refund Request - {self.order.order_id} - {self.status}"


class HostelListing(models.Model):
    """Hostel listings for students"""
    
    landlord = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hostel_listings'
    )
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField()
    
    LOCATION_CHOICES = [
        ('ilorin', 'Ilorin'),
        ('malete', 'Malete'),
        ('offa', 'Offa'),
    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    rent_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    amenities = models.JSONField(default=list)
    contact_phone = models.CharField(max_length=20)
    
    image_1 = models.ImageField(upload_to='hostel_images/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='hostel_images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='hostel_images/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)
    
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_verified', 'is_active', 'location', '-created_at']),
            models.Index(fields=['landlord', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ₦{self.rent_per_month}/month"
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])