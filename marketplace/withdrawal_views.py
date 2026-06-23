from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import UnsupportedMediaType
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.db.models import Sum, F
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from rest_framework import serializers

from .models import Withdrawal, WalletTransaction
from accounts.models import Profile, BankAccount
from .payment_service import paystack_service
from .ledger_service import FinancialLedgerService
from .background_jobs import (
    refresh_financial_reconciliation_snapshot,
    run_after_commit,
    send_finance_alert,
    send_user_sms_notification,
)
from .idempotency import build_reference, get_request_id

MIN_WITHDRAWAL = Decimal('1000.00')
MAX_WITHDRAWAL_PER_DAY = Decimal('500000.00')
WITHDRAWAL_FEE = Decimal('25.00')


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'account_number', 'account_name', 'bank_name', 'bank_code', 'is_primary', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class WithdrawalSerializer(serializers.ModelSerializer):
    bank_account_details = BankAccountSerializer(source='bank_account', read_only=True)
    
    class Meta:
        model = Withdrawal
        fields = ['id', 'amount', 'withdrawal_fee', 'net_amount', 'bank_account', 'bank_account_details', 'status', 'failure_reason', 'reference', 'created_at', 'completed_at']
        read_only_fields = ['id', 'withdrawal_fee', 'net_amount', 'status', 'failure_reason', 'reference', 'created_at', 'completed_at']


class WithdrawalRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    bank_account_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_bank_account(request):
    account_number = request.data.get('account_number', '').strip()
    bank_code = request.data.get('bank_code', '').strip()
    
    if not account_number or not bank_code:
        return Response({"error": "Account number and bank code required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not account_number.isdigit() or len(account_number) != 10:
        return Response({"error": "Invalid account number. Must be 10 digits"}, status=status.HTTP_400_BAD_REQUEST)
    
    result = paystack_service.verify_account_number(account_number, bank_code)
    
    if not result['success']:
        return Response({"error": result['error']}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"account_number": result['account_number'], "account_name": result['account_name'], "message": "Account verified successfully"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_bank_account(request):
    user = request.user
    account_number = request.data.get('account_number', '').strip()
    bank_code = request.data.get('bank_code', '').strip()
    bank_name = request.data.get('bank_name', '').strip()
    
    if not all([account_number, bank_code, bank_name]):
        return Response({"error": "All fields required: account_number, bank_code, bank_name"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not account_number.isdigit() or len(account_number) != 10:
        return Response({"error": "Invalid account number. Must be 10 digits"}, status=status.HTTP_400_BAD_REQUEST)
    
    verification = paystack_service.verify_account_number(account_number, bank_code)
    
    if not verification['success']:
        return Response({"error": f"Account verification failed: {verification['error']}"}, status=status.HTTP_400_BAD_REQUEST)
    
    account_name = verification['account_name']
    
    if BankAccount.objects.filter(user=user, account_number=account_number, bank_code=bank_code).exists():
        return Response({"error": "This bank account is already linked to your profile"}, status=status.HTTP_400_BAD_REQUEST)
    
    recipient_result = paystack_service.create_transfer_recipient(account_number=account_number, bank_code=bank_code, account_name=account_name)
    
    if not recipient_result['success']:
        return Response({"error": f"Failed to register bank account: {recipient_result['error']}"}, status=status.HTTP_400_BAD_REQUEST)
    
    is_primary = not BankAccount.objects.filter(user=user).exists()
    
    set_as_primary = request.data.get('set_as_primary')
    if str(set_as_primary).lower() in {'true', '1', 'yes', 'on'} or is_primary:
        BankAccount.objects.filter(user=user).update(is_primary=False)
        is_primary = True
    
    bank_account = BankAccount.objects.create(user=user, account_number=account_number, account_name=account_name, bank_name=bank_name, bank_code=bank_code, recipient_code=recipient_result['recipient_code'], is_verified=True, is_primary=is_primary)
    
    return Response({"message": "Bank account added successfully", "bank_account": BankAccountSerializer(bank_account).data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_bank_accounts(request):
    accounts = BankAccount.objects.filter(user=request.user).order_by('-is_primary', '-created_at')
    return Response(BankAccountSerializer(accounts, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_primary_bank_account(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id, user=request.user)
    BankAccount.objects.filter(user=request.user).update(is_primary=False)
    account.is_primary = True
    account.save()
    return Response({"message": "Primary bank account updated", "bank_account": BankAccountSerializer(account).data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_bank_account(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id, user=request.user)
    account_count = BankAccount.objects.filter(user=request.user).count()
    account.delete()
    
    if account.is_primary and account_count > 1:
        first_remaining = BankAccount.objects.filter(user=request.user).first()
        if first_remaining:
            first_remaining.is_primary = True
            first_remaining.save()
    
    return Response({"message": "Bank account removed successfully"})


def _get_request_payload(request):
    try:
        return request.data
    except UnsupportedMediaType:
        underlying = getattr(request, '_request', request)
        return getattr(underlying, 'POST', {})
    except AttributeError:
        return getattr(request, 'POST', {})


def _withdraw_funds_impl(request):
    # internal implementation expects a DRF Request-like object with `.data` and `.user`
    request_user = getattr(request, 'user', None)
    underlying_request = getattr(request, '_request', None)
    if not (hasattr(request_user, 'is_authenticated') and request_user.is_authenticated):
        if underlying_request is not None:
            fallback_user = getattr(underlying_request, 'user', None)
            if hasattr(fallback_user, 'is_authenticated') and fallback_user.is_authenticated:
                request_user = fallback_user
    user = request_user
    payload = _get_request_payload(request)

    serializer = WithdrawalRequestSerializer(data=payload)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    amount = serializer.validated_data['amount']
    bank_account_id = serializer.validated_data.get('bank_account_id')

    if amount <= 0:
        return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

    if amount < MIN_WITHDRAWAL:
        return Response({"error": f"Minimum withdrawal amount is ₦{MIN_WITHDRAWAL}"}, status=status.HTTP_400_BAD_REQUEST)

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_withdrawals_total = Withdrawal.objects.filter(user=user, created_at__gte=today_start, status__in=['success', 'processing', 'pending']).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    if today_withdrawals_total + amount > MAX_WITHDRAWAL_PER_DAY:
        return Response({"error": f"Daily withdrawal limit exceeded", "daily_limit": str(MAX_WITHDRAWAL_PER_DAY), "withdrawn_today": str(today_withdrawals_total), "available_today": str(MAX_WITHDRAWAL_PER_DAY - today_withdrawals_total)}, status=status.HTTP_400_BAD_REQUEST)

    bank_account = None
    if bank_account_id:
        bank_account = BankAccount.objects.filter(id=bank_account_id, user=user, is_verified=True).first()
        if not bank_account:
            return Response({"error": "Selected bank account is not available or verified"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        bank_account = BankAccount.objects.filter(user=user, is_primary=True, is_verified=True).first()
        if not bank_account:
            return Response({"error": "No bank account found. Please add a bank account first"}, status=status.HTTP_400_BAD_REQUEST)

    net_amount = amount - WITHDRAWAL_FEE

    if net_amount <= 0:
        return Response({"error": f"Amount too small. Minimum after ₦{WITHDRAWAL_FEE} fee is ₦{MIN_WITHDRAWAL}"}, status=status.HTTP_400_BAD_REQUEST)

    profile = user.profile
    if profile.wallet_balance < amount:
        return Response({"error": "Insufficient wallet balance", "your_balance": str(profile.wallet_balance), "required": str(amount)}, status=status.HTTP_400_BAD_REQUEST)

    request_id = get_request_id(request, fallback=f'withdraw-{user.id}-{amount}-{bank_account_id or "primary"}')
    reference = build_reference('WD', user.id, amount, bank_account_id or 'primary', request_id)

    existing_withdrawal = Withdrawal.objects.filter(reference=reference).select_related('bank_account').first()
    if existing_withdrawal:
        return Response({
            "message": "Withdrawal already processed",
            "withdrawal": WithdrawalSerializer(existing_withdrawal).data,
        }, status=status.HTTP_200_OK)

    try:
        with db_transaction.atomic():
            profile = Profile.objects.select_for_update().get(user=user)

            if profile.wallet_balance < amount:
                return Response({"error": "Insufficient wallet balance"}, status=status.HTTP_400_BAD_REQUEST)

            balance_before = profile.wallet_balance
            Profile.objects.filter(user=user).update(wallet_balance=F('wallet_balance') - amount)
            profile.refresh_from_db()
            balance_after = profile.wallet_balance

            # Create withdrawal record with status='pending' first
            withdrawal = Withdrawal.objects.create(
                user=user,
                bank_account=bank_account,
                amount=amount,
                withdrawal_fee=WITHDRAWAL_FEE,
                net_amount=net_amount,
                transfer_code=None,
                reference=reference,
                status='pending',
                wallet_balance_before=balance_before,
                wallet_balance_after=balance_after,
            )

            WalletTransaction.objects.create(
                user=user,
                transaction_type='debit',
                amount=amount,
                source='withdrawal',
                balance_before=balance_before,
                balance_after=balance_after,
                reference=reference,
            )

            FinancialLedgerService.record_withdrawal(
                user=user,
                amount=amount,
                withdrawal_fee=WITHDRAWAL_FEE,
                net_amount=net_amount,
                related_withdrawal=withdrawal,
                created_by=user,
            )
    except Exception as e:
        send_finance_alert(
            subject='CampusDeal withdrawal preparation failed',
            message=f"User {user.id} | amount={amount} | error={str(e)}",
        )
        return Response({"error": f"Withdrawal processing error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Initiate Paystack transfer outside of database transaction
    try:
        transfer_result = paystack_service.initiate_transfer(
            amount=net_amount,
            recipient_code=bank_account.recipient_code,
            reason=f"CampusDeal withdrawal - {user.get_full_name() or user.username}"
        )
    except Exception as e:
        transfer_result = {'success': False, 'error': str(e)}

    if transfer_result.get('success'):
        with db_transaction.atomic():
            withdrawal.status = 'processing'
            withdrawal.transfer_code = transfer_result['transfer_code']
            withdrawal.save(update_fields=['status', 'transfer_code'])

        run_after_commit(
            'withdrawal-notify',
            send_user_sms_notification,
            user,
            f"CampusDeal withdrawal of ₦{amount} has been initiated successfully. Reference: {reference}.",
        )
        run_after_commit(
            'withdrawal-reconcile',
            refresh_financial_reconciliation_snapshot,
            f'withdrawal {reference}',
        )
    else:
        error_msg = transfer_result.get('error', 'Unknown Paystack error')
        try:
            with db_transaction.atomic():
                profile = Profile.objects.select_for_update().get(user=user)
                balance_before = profile.wallet_balance
                Profile.objects.filter(user=user).update(wallet_balance=F('wallet_balance') + amount)
                profile.refresh_from_db()
                balance_after = profile.wallet_balance

                withdrawal.status = 'failed'
                withdrawal.failure_reason = error_msg
                withdrawal.save(update_fields=['status', 'failure_reason'])

                WalletTransaction.objects.create(
                    user=user,
                    transaction_type='credit',
                    amount=amount,
                    source='refund',
                    balance_before=balance_before,
                    balance_after=balance_after,
                    reference=f"REV-{reference}",
                )

                FinancialLedgerService.record_failed_withdrawal(
                    user=user,
                    amount=amount,
                    withdrawal_fee=WITHDRAWAL_FEE,
                    net_amount=net_amount,
                    related_withdrawal=withdrawal,
                    created_by=user,
                    reason=error_msg,
                )
        except Exception as e:
            send_finance_alert(
                subject='CampusDeal withdrawal rollback critical error',
                message=f"CRITICAL: Failed to reverse failed withdrawal for User {user.id} | amount={amount} | error={str(e)}",
            )
            return Response({"error": f"Withdrawal failed and recovery failed: {error_msg}. Platform notified."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        send_finance_alert(
            subject='CampusDeal withdrawal transfer failed',
            message=f"User {user.id} | amount={amount} | bank={bank_account.bank_name} | error={error_msg}",
        )
        return Response({"error": f"Transfer failed: {error_msg}"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Withdrawal initiated successfully", "withdrawal": WithdrawalSerializer(withdrawal).data, "details": {"total_amount": str(amount), "withdrawal_fee": str(WITHDRAWAL_FEE), "net_amount": str(net_amount), "bank_account": f"{bank_account.account_name} - {bank_account.account_number}", "estimated_time": "Instant to 24 hours (most banks are instant)"}}, status=status.HTTP_201_CREATED)


# Decorated API view that expects a Django HttpRequest (normal routing)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def _withdraw_funds_api(request, *args, **kwargs):
    return _withdraw_funds_impl(request)


def withdraw_funds(request, *args, **kwargs):
    from rest_framework.request import Request as DRFRequest
    if isinstance(request, DRFRequest) and hasattr(request, '_request'):
        # unwrap to Django HttpRequest for DRF dispatch
        return _withdraw_funds_api(request._request, *args, **kwargs)
    else:
        return _withdraw_funds_api(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def withdrawal_history(request):
    queryset = Withdrawal.objects.filter(user=request.user)
    total_count = queryset.count()
    withdrawals = queryset.select_related('bank_account').order_by('-created_at')[:50]
    return Response({"count": total_count, "withdrawals": WithdrawalSerializer(withdrawals, many=True).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_withdrawal_fees(request):
    return Response({"withdrawal_fee": str(WITHDRAWAL_FEE), "minimum_withdrawal": str(MIN_WITHDRAWAL), "maximum_per_day": str(MAX_WITHDRAWAL_PER_DAY), "currency": "NGN", "note": "Withdrawal fee is deducted from your wallet balance"})
