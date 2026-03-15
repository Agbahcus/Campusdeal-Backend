from django.core.management.base import BaseCommand
from decimal import Decimal

from marketplace.models import PlatformFinancials, FinancialTransaction
from marketplace.payment_service import paystack_service


class Command(BaseCommand):
    help = 'Reconcile platform financials with Paystack'

    def handle(self, *args, **options):
        financials = PlatformFinancials.get_instance()

        # Get actual Paystack balance
        balance_check = paystack_service.check_balance()

        if not balance_check.get('success'):
            self.stdout.write(self.style.ERROR(f"Cannot check Paystack balance: {balance_check.get('error')}"))
            return

        actual_balance = Decimal(str(balance_check.get('balance')))
        recorded_balance = financials.paystack_balance

        difference = actual_balance - recorded_balance

        self.stdout.write('=' * 60)
        self.stdout.write('FINANCIAL RECONCILIATION REPORT')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Paystack Actual:     ₦{actual_balance:,.2f}')
        self.stdout.write(f'Recorded Balance:    ₦{recorded_balance:,.2f}')
        self.stdout.write(f'Difference:          ₦{difference:,.2f}')
        self.stdout.write('-' * 60)
        self.stdout.write(f'User Liability:      ₦{financials.user_funds_liability:,.2f}')
        self.stdout.write(f'Platform Revenue:    ₦{financials.platform_revenue:,.2f}')
        self.stdout.write(f'Available to Withdraw: ₦{financials.available_for_platform_withdrawal():,.2f}')
        self.stdout.write('-' * 60)
        self.stdout.write(f'Status: {financials.reconciliation_status()}')
        self.stdout.write('=' * 60)

        if abs(difference) > Decimal('1.00'):
            self.stdout.write(self.style.WARNING(f'\n⚠️  RECONCILIATION MISMATCH: ₦{difference:,.2f}'))
            self.stdout.write('This needs investigation!')

            if input('\nAdjust recorded balance? (yes/no): ').lower() == 'yes':
                financials.paystack_balance = actual_balance
                financials.save()

                FinancialTransaction.objects.create(
                    transaction_type='reconciliation',
                    paystack_balance_change=difference,
                    notes=f'Reconciliation adjustment: ₦{difference}',
                    user_liability_after=financials.user_funds_liability,
                    platform_revenue_after=financials.platform_revenue,
                    paystack_balance_after=financials.paystack_balance
                )

                self.stdout.write(self.style.SUCCESS('✅ Balance adjusted'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Books are balanced!'))
