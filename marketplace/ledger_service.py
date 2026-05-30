from decimal import Decimal

from django.db import transaction

from accounts.models import Profile
from .models import (
    FinancialTransaction,
    PlatformFinancials,
    WalletTransaction,
)


class FinancialLedgerService:
    @staticmethod
    def get_financials():
        return PlatformFinancials.get_instance()

    @staticmethod
    def record_wallet_deposit(user, amount, reference):
        with transaction.atomic():
            profile = Profile.objects.select_for_update().get(user=user)

            existing_transaction = WalletTransaction.objects.select_for_update().filter(
                user=user,
                reference=reference,
                source='deposit',
            ).first()
            if existing_transaction:
                return {
                    'duplicate': True,
                    'amount': existing_transaction.amount,
                    'new_balance': profile.wallet_balance,
                }

            balance_before = profile.wallet_balance
            Profile.objects.filter(user=user).update(wallet_balance=profile.wallet_balance + amount)
            profile.refresh_from_db()

            WalletTransaction.objects.create(
                user=user,
                transaction_type='credit',
                amount=amount,
                source='deposit',
                reference=reference,
                balance_before=balance_before,
                balance_after=profile.wallet_balance,
            )

            financials = PlatformFinancials.get_instance()
            financials.user_funds_liability += amount
            financials.paystack_balance += amount
            financials.save()

            FinancialTransaction.objects.create(
                transaction_type='payment_received',
                user_liability_change=amount,
                platform_revenue_change=Decimal('0'),
                paystack_balance_change=amount,
                notes=f'Wallet deposit - User {user.id} (reference={reference})',
                user_liability_after=financials.user_funds_liability,
                platform_revenue_after=financials.platform_revenue,
                paystack_balance_after=financials.paystack_balance,
                created_by=user,
            )

            return {
                'duplicate': False,
                'amount': amount,
                'new_balance': profile.wallet_balance,
            }

    @staticmethod
    def record_order_payment(order, payment_method, created_by):
        with transaction.atomic():
            financials = PlatformFinancials.get_instance()
            financials.user_funds_liability += order.item_price
            financials.platform_revenue += order.service_fee

            paystack_delta = order.total_amount if payment_method == 'paystack' else Decimal('0')
            financials.paystack_balance += paystack_delta
            financials.save()

            FinancialTransaction.objects.create(
                transaction_type='payment_received',
                user_liability_change=order.item_price,
                platform_revenue_change=order.service_fee,
                paystack_balance_change=paystack_delta,
                related_order=order,
                notes=f'{payment_method.title()} payment - {order.order_id}',
                user_liability_after=financials.user_funds_liability,
                platform_revenue_after=financials.platform_revenue,
                paystack_balance_after=financials.paystack_balance,
                created_by=created_by,
            )

    @staticmethod
    def reverse_order_payment(order, created_by, note='Order cancelled'):
        with transaction.atomic():
            financials = PlatformFinancials.get_instance()
            financials.user_funds_liability -= order.item_price
            financials.platform_revenue -= order.service_fee

            paystack_delta = -order.total_amount if order.payment_method == 'paystack' else Decimal('0')
            financials.paystack_balance += paystack_delta
            financials.save()

            FinancialTransaction.objects.create(
                transaction_type='refund_issued',
                user_liability_change=-order.item_price,
                platform_revenue_change=-order.service_fee,
                paystack_balance_change=paystack_delta,
                related_order=order,
                notes=f'{note} - {order.order_id}',
                user_liability_after=financials.user_funds_liability,
                platform_revenue_after=financials.platform_revenue,
                paystack_balance_after=financials.paystack_balance,
                created_by=created_by,
            )

    @staticmethod
    def process_order_refund(order, created_by, source='refund'):
        with transaction.atomic():
            buyer_profile = Profile.objects.select_for_update().get(user=order.buyer)
            buyer_balance_before = buyer_profile.wallet_balance
            Profile.objects.filter(user=order.buyer).update(
                wallet_balance=buyer_profile.wallet_balance + order.total_amount
            )
            buyer_profile.refresh_from_db()

            WalletTransaction.objects.create(
                user=order.buyer,
                transaction_type='credit',
                amount=order.total_amount,
                source=source,
                related_order=order,
                balance_before=buyer_balance_before,
                balance_after=buyer_profile.wallet_balance,
            )

            seller_profile = None
            if order.funds_released_to_seller:
                seller_profile = Profile.objects.select_for_update().get(user=order.seller)
                seller_balance_before = seller_profile.wallet_balance
                Profile.objects.filter(user=order.seller).update(
                    wallet_balance=seller_profile.wallet_balance - order.item_price
                )
                seller_profile.refresh_from_db()

                WalletTransaction.objects.create(
                    user=order.seller,
                    transaction_type='debit',
                    amount=order.item_price,
                    source=source,
                    related_order=order,
                    balance_before=seller_balance_before,
                    balance_after=seller_profile.wallet_balance,
                )

            if order.funds_held or order.funds_released_to_seller:
                FinancialLedgerService.reverse_order_payment(
                    order=order,
                    created_by=created_by,
                    note='Refund approved',
                )

            return {
                'buyer_balance': buyer_profile.wallet_balance,
                'seller_balance': seller_profile.wallet_balance if seller_profile else None,
            }

    @staticmethod
    def record_withdrawal(user, amount, withdrawal_fee, net_amount, related_withdrawal, created_by):
        with transaction.atomic():
            financials = PlatformFinancials.get_instance()
            financials.user_funds_liability -= amount
            financials.platform_revenue += withdrawal_fee
            financials.paystack_balance -= net_amount
            financials.save()

            FinancialTransaction.objects.create(
                transaction_type='withdrawal_processed',
                user_liability_change=-amount,
                platform_revenue_change=withdrawal_fee,
                paystack_balance_change=-net_amount,
                related_withdrawal=related_withdrawal,
                notes=f'Withdrawal to user {user.id}',
                user_liability_after=financials.user_funds_liability,
                platform_revenue_after=financials.platform_revenue,
                paystack_balance_after=financials.paystack_balance,
                created_by=created_by,
            )

    @staticmethod
    def record_platform_withdrawal(amount, account_name, created_by):
        with transaction.atomic():
            financials = PlatformFinancials.get_instance()
            financials.platform_revenue -= amount
            financials.paystack_balance -= amount
            financials.save()

            FinancialTransaction.objects.create(
                transaction_type='platform_withdrawal',
                platform_revenue_change=-amount,
                paystack_balance_change=-amount,
                notes=f'Platform withdrawal to {account_name}',
                created_by=created_by,
                user_liability_after=financials.user_funds_liability,
                platform_revenue_after=financials.platform_revenue,
                paystack_balance_after=financials.paystack_balance,
            )
