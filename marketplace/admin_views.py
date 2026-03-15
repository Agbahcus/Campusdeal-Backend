from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db import transaction as db_transaction
from decimal import Decimal

from .models import PlatformFinancials, FinancialTransaction
from .payment_service import paystack_service


@api_view(['POST'])
@permission_classes([IsAdminUser])
def withdraw_platform_profit(request):
    """
    Admin only: Withdraw platform profit
    """
    try:
        amount = Decimal(str(request.data.get('amount')))
    except:
        return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

    bank_account_number = request.data.get('bank_account_number')
    bank_code = request.data.get('bank_code')

    if not bank_account_number or not bank_code:
        return Response({"error": "Bank details required"}, status=status.HTTP_400_BAD_REQUEST)

    financials = PlatformFinancials.get_instance()
    available = financials.available_for_platform_withdrawal()

    if amount > available:
        return Response({
            "error": "Insufficient available funds",
            "requested": str(amount),
            "available": str(available),
            "user_liability": str(financials.user_funds_liability),
            "paystack_balance": str(financials.paystack_balance),
            "warning": "Cannot withdraw user funds!"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify bank account
    verification = paystack_service.verify_account_number(bank_account_number, bank_code)

    if not verification['success']:
        return Response({"error": f"Bank verification failed: {verification['error']}"}, status=status.HTTP_400_BAD_REQUEST)

    # Create recipient
    recipient = paystack_service.create_transfer_recipient(bank_account_number=bank_account_number, bank_code=bank_code, account_name=verification['account_name'])

    if not recipient['success']:
        return Response({"error": f"Failed to create recipient: {recipient['error']}"}, status=status.HTTP_400_BAD_REQUEST)

    # Process transfer
    transfer = paystack_service.initiate_transfer(amount=amount, recipient_code=recipient['recipient_code'], reason="Platform profit withdrawal")

    if not transfer['success']:
        return Response({"error": f"Transfer failed: {transfer['error']}"}, status=status.HTTP_400_BAD_REQUEST)

    # Update financials
    with db_transaction.atomic():
        financials.platform_revenue -= amount
        financials.paystack_balance -= amount
        financials.save()

        FinancialTransaction.objects.create(
            transaction_type='platform_withdrawal',
            platform_revenue_change=-amount,
            paystack_balance_change=-amount,
            notes=f"Platform withdrawal to {verification['account_name']}",
            created_by=request.user,
            user_liability_after=financials.user_funds_liability,
            platform_revenue_after=financials.platform_revenue,
            paystack_balance_after=financials.paystack_balance
        )

    return Response({
        "message": "Platform withdrawal successful",
        "amount": str(amount),
        "recipient": verification['account_name'],
        "reference": transfer.get('reference'),
        "remaining_revenue": str(financials.platform_revenue),
        "remaining_available": str(financials.available_for_platform_withdrawal())
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def platform_financial_summary(request):
    """Get current financial position"""
    financials = PlatformFinancials.get_instance()

    return Response({
        "paystack_balance": str(financials.paystack_balance),
        "user_liability": str(financials.user_funds_liability),
        "platform_revenue": str(financials.platform_revenue),
        "available_for_withdrawal": str(financials.available_for_platform_withdrawal()),
        "reconciliation_status": financials.reconciliation_status(),
        "last_updated": financials.last_updated
    })
