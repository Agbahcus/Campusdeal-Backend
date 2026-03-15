"""
FINANCIAL TRACKING MODELS
Separates user funds from platform revenue
CRITICAL for business accounting and compliance
"""
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


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