from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal

from .models import WalletTransaction
from .serializers import WalletTransactionSerializer
from .payment_service import paystack_service


class WalletPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet_balance(request):
    """
    Get current wallet balance
    
    GET /api/marketplace/wallet/balance/
    """
    profile = request.user.profile
    
    return Response({
        "balance": str(profile.wallet_balance),
        "currency": "NGN"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet_transactions(request):
    """
    Get wallet transaction history
    
    GET /api/marketplace/wallet/transactions/
    Query params:
    - transaction_type: credit|debit
    - source: sale|refund|deposit|purchase|withdrawal
    """
    transactions = WalletTransaction.objects.filter(user=request.user)
    
    # Apply filters
    transaction_type = request.query_params.get('transaction_type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    source = request.query_params.get('source')
    if source:
        transactions = transactions.filter(source=source)
    
    # Paginate
    paginator = WalletPagination()
    page = paginator.paginate_queryset(transactions, request)
    
    if page is not None:
        serializer = WalletTransactionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = WalletTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_funds_to_wallet(request):
    """
    Add funds to wallet via Paystack
    
    POST /api/marketplace/wallet/add-funds/
    Body: {
        "amount": "5000.00"
    }
    """
    amount_str = request.data.get('amount')
    
    if not amount_str:
        return Response(
            {"error": "Amount is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid amount"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Minimum deposit
    if amount < Decimal('100.00'):
        return Response(
            {"error": "Minimum deposit is ₦100"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate reference
    reference = f"WALLET_{request.user.id}_{int(timezone.now().timestamp())}"
    
    # Initialize Paystack payment
    from django.conf import settings
    result = paystack_service.initialize_payment(
        email=request.user.email,
        amount=amount * 100,  # Convert to kobo
        reference=reference,
        callback_url=f"{settings.FRONTEND_URL}/wallet/verify",
        metadata={
            "user_id": request.user.id,
            "purpose": "wallet_deposit"
        }
    )
    
    if result.get('status'):
        return Response({
            "authorization_url": result['data']['authorization_url'],
            "access_code": result['data']['access_code'],
            "reference": reference,
            "amount": str(amount)
        })
    else:
        return Response({
            "error": "Failed to initialize payment",
            "message": result.get('message')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_wallet_deposit(request):
    """
    Verify wallet deposit payment
    
    POST /api/marketplace/wallet/verify-deposit/
    Body: {
        "reference": "WALLET_123_1234567890"
    }
    """
    reference = request.data.get('reference')
    
    if not reference:
        return Response(
            {"error": "Reference is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify with Paystack
    result = paystack_service.verify_payment(reference)
    
    if result.get('status') and result['data']['status'] == 'success':
        amount = Decimal(result['data']['amount']) / 100  # Convert from kobo
        
        # Credit wallet
        with db_transaction.atomic():
            profile = request.user.profile
            balance_before = profile.wallet_balance
            profile.wallet_balance += amount
            profile.save()
            
            # Log transaction
            WalletTransaction.objects.create(
                user=request.user,
                transaction_type='credit',
                amount=amount,
                source='deposit',
                reference=reference,
                balance_before=balance_before,
                balance_after=profile.wallet_balance
            )
        
        return Response({
            "success": True,
            "message": "Wallet credited successfully",
            "amount": str(amount),
            "new_balance": str(profile.wallet_balance)
        })
    else:
        return Response({
            "success": False,
            "message": "Payment verification failed"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_withdrawal(request):
    """
    Request withdrawal from wallet to bank account
    
    POST /api/marketplace/wallet/withdraw/
    Body: {
        "amount": "10000.00",
        "account_number": "0123456789",
        "bank_code": "058"  // Paystack bank code
    }
    """
    # TODO: Implement withdrawal logic
    # This requires:
    # 1. Creating transfer recipient with Paystack
    # 2. Initiating transfer
    # 3. Deducting from wallet on success
    
    return Response({
        "message": "Withdrawal feature coming soon"
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_banks(request):
    """
    Get list of Nigerian banks for withdrawal
    
    GET /api/marketplace/wallet/banks/
    """
    result = paystack_service.list_banks()
    
    if result.get('status'):
        # Return only necessary fields
        banks = [
            {
                'name': bank['name'],
                'code': bank['code']
            }
            for bank in result['data']
        ]
        return Response(banks)
    else:
        return Response({
            "error": "Failed to fetch banks"
        }, status=status.HTTP_400_BAD_REQUEST)