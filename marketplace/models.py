from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
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
        ('lagos', 'Lagos'),
        ('abuja', 'Abuja'),
        ('ibadan', 'Ibadan'),
        ('kano', 'Kano'),
        ('port-harcourt', 'Port Harcourt'),
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
        ('lagos', 'Lagos'),
        ('abuja', 'Abuja'),
        ('ibadan', 'Ibadan'),
        ('kano', 'Kano'),
        ('port-harcourt', 'Port Harcourt'),
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


class Offer(models.Model):
    """Buyer sends an offer to a seller for a negotiable item"""
    item = models.ForeignKey(ItemListing, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers_made')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    message = models.TextField(blank=True, max_length=300)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(
        max_length=15,
        choices=[('campusdeal', 'CampusDeal'), ('seller', 'Seller'), ('pickup', 'Pickup')],
        default='pickup'
    )

    # Set when seller accepts - links to the created order
    order = models.OneToOneField(
        'Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='offer'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item', 'status']),
            models.Index(fields=['buyer', '-created_at']),
        ]

    def __str__(self):
        return f"Offer by {self.buyer.username} on {self.item.title} - ₦{self.proposed_price}"


class Withdrawal(models.Model):
    """Withdrawal requests and history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    bank_account = models.ForeignKey('accounts.BankAccount', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    withdrawal_fee = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transfer_code = models.CharField(max_length=100, unique=True, blank=True)
    reference = models.CharField(max_length=100, unique=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(blank=True)
    wallet_balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reference']),
        ]
    
    def __str__(self):
        return f"Withdrawal {self.reference} - ₦{self.amount} - {self.status}"


class PlatformFinancials(models.Model):
    """
    Track platform financial position - SINGLETON MODEL
    Only one record exists to track overall financial state
    
    CRITICAL: Separates user funds (liability) from platform revenue
    """
    
    # What we owe to users (seller funds held in escrow/wallets)
    user_funds_liability = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        help_text="Total amount owed to sellers in escrow/wallets"
    )
    
    # Platform revenue (service fees, withdrawal fees)
    platform_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Platform profit from fees"
    )
    
    # Actual Paystack balance (for reconciliation)
    paystack_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Actual balance in Paystack account"
    )
    
    # Tracking
    last_reconciliation = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Platform Financials"
        verbose_name_plural = "Platform Financials"
    
    def __str__(self):
        return f"Platform Financials (Updated: {self.last_updated})"
    
    def available_for_platform_withdrawal(self):
        """Amount platform can safely withdraw without touching user funds"""
        return self.paystack_balance - self.user_funds_liability
    
    def reconciliation_status(self):
        """Check if books balance"""
        expected = self.user_funds_liability + self.platform_revenue
        actual = self.paystack_balance
        difference = actual - expected
        
        if abs(difference) < Decimal('1.00'):  # Allow ₦1 rounding
            return "BALANCED ✅"
        elif difference > 0:
            return f"SURPLUS: ₦{difference} (investigate)"
        else:
            return f"DEFICIT: ₦{abs(difference)} (CRITICAL!)"
    
    def save(self, *args, **kwargs):
        # Ensure singleton - only one record exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class FinancialTransaction(models.Model):
    """
    Audit trail for all money movements
    NEVER DELETE - Required for compliance and debugging
    """
    TRANSACTION_TYPES = [
        ('payment_received', 'Payment Received'),
        ('withdrawal_processed', 'Withdrawal Processed'),
        ('service_fee_earned', 'Service Fee Earned'),
        ('withdrawal_fee_earned', 'Withdrawal Fee Earned'),
        ('refund_issued', 'Refund Issued'),
        ('platform_withdrawal', 'Platform Withdrawal'),
        ('reconciliation', 'Reconciliation Adjustment'),
    ]
    
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    
    # Amount changes (+ increase, - decrease)
    user_liability_change = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        help_text="Change in what we owe users (+ increase, - decrease)"
    )
    platform_revenue_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Change in platform profit (+ increase, - decrease)"
    )
    paystack_balance_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Change in Paystack balance (+ increase, - decrease)"
    )
    
    # Context - what caused this transaction
    related_order = models.ForeignKey(
        'Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    related_withdrawal = models.ForeignKey(
        'Withdrawal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Balances after this transaction (for audit trail)
    user_liability_after = models.DecimalField(max_digits=12, decimal_places=2)
    platform_revenue_after = models.DecimalField(max_digits=12, decimal_places=2)
    paystack_balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - ₦{self.paystack_balance_change} ({self.created_at})"
