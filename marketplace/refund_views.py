from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal

from .ledger_service import FinancialLedgerService
from .models import Order, RefundRequest, WalletTransaction
from marketplace.serializers import WalletTransactionSerializer
from rest_framework import serializers


class RefundRequestSerializer(serializers.ModelSerializer):
    """Serializer for refund requests"""
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    
    class Meta:
        model = RefundRequest
        fields = [
            'id',
            'order',
            'order_id',
            'requester',
            'requester_name',
            'reason',
            'detailed_explanation',
            'evidence_image_1',
            'evidence_image_2',
            'evidence_image_3',
            'status',
            'admin_notes',
            'created_at',
            'resolved_at'
        ]
        read_only_fields = ['id', 'requester', 'status', 'admin_notes', 'created_at', 'resolved_at']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_refund(request, order_id):
    """
    Request a refund for an order
    
    POST /api/marketplace/orders/{order_id}/request-refund/
    Body: {
        "reason": "not_as_described",
        "detailed_explanation": "Item condition was misrepresented...",
        "evidence_image_1": <file>,
        "evidence_image_2": <file> (optional),
        "evidence_image_3": <file> (optional)
    }
    """
    user = request.user
    order = get_object_or_404(Order, order_id=order_id)
    
    # Only buyer can request refund
    if user != order.buyer:
        return Response(
            {"error": "Only the buyer can request a refund"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check order is in valid state for refund
    if order.status not in ['completed', 'delivered']:
        return Response(
            {"error": "Refunds can only be requested for completed or delivered orders"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if refund already requested
    if hasattr(order, 'refund_request'):
        return Response(
            {"error": "Refund already requested for this order"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check refund deadline (e.g., 7 days after delivery)
    from datetime import timedelta
    if order.completed_at:
        deadline = order.completed_at + timedelta(days=7)
        if timezone.now() > deadline:
            return Response(
                {"error": "Refund request deadline has passed (7 days after completion)"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validate reason
    valid_reasons = ['not_as_described', 'damaged', 'wrong_item', 'seller_unresponsive', 'other']
    reason = request.data.get('reason')
    if reason not in valid_reasons:
        return Response(
            {"error": f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    detailed_explanation = request.data.get('detailed_explanation', '')
    if not detailed_explanation or len(detailed_explanation) < 20:
        return Response(
            {"error": "Please provide a detailed explanation (minimum 20 characters)"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create refund request
    refund = RefundRequest.objects.create(
        order=order,
        requester=user,
        reason=reason,
        detailed_explanation=detailed_explanation,
        evidence_image_1=request.FILES.get('evidence_image_1'),
        evidence_image_2=request.FILES.get('evidence_image_2'),
        evidence_image_3=request.FILES.get('evidence_image_3')
    )
    
    # Update order status
    order.status = 'refund_requested'
    order.save()
    
    # TODO: Notify admin and seller
    
    return Response(
        RefundRequestSerializer(refund).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_refund_request(request, order_id):
    """
    Get refund request for an order
    
    GET /api/marketplace/orders/{order_id}/refund-request/
    """
    order = get_object_or_404(Order, order_id=order_id)
    
    # Check user is buyer or seller
    if request.user not in [order.buyer, order.seller]:
        return Response(
            {"error": "You don't have access to this order"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        refund = order.refund_request
        serializer = RefundRequestSerializer(refund)
        return Response(serializer.data)
    except RefundRequest.DoesNotExist:
        return Response(
            {"message": "No refund request for this order"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_refund(request, refund_id):
    """
    Approve refund request (Admin only)
    
    POST /api/marketplace/refunds/{refund_id}/approve/
    Body: {
        "admin_notes": "Approved - clear evidence provided"
    }
    """
    # Check admin permission
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    if refund.status != 'pending':
        return Response(
            {"error": "This refund has already been processed"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    admin_notes = request.data.get('admin_notes', '')
    
    # Process refund
    with db_transaction.atomic():
        order = refund.order

        FinancialLedgerService.process_order_refund(
            order=order,
            created_by=request.user,
            source='refund',
        )
        
        # Update refund status
        refund.status = 'approved'
        refund.admin_notes = admin_notes
        refund.resolved_at = timezone.now()
        refund.save()
        
        # Update order
        order.status = 'refunded'
        order.save()
        
        # Reactivate item listing
        order.item.status = 'active'
        order.item.save()
    
    # TODO: Notify buyer and seller
    
    return Response({
        "success": True,
        "message": "Refund approved and processed",
        "refund": RefundRequestSerializer(refund).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_refund(request, refund_id):
    """
    Reject refund request (Admin only)
    
    POST /api/marketplace/refunds/{refund_id}/reject/
    Body: {
        "admin_notes": "Insufficient evidence - item was as described"
    }
    """
    # Check admin permission
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    if refund.status != 'pending':
        return Response(
            {"error": "This refund has already been processed"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    admin_notes = request.data.get('admin_notes', '')
    if not admin_notes:
        return Response(
            {"error": "Admin notes required for rejection"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update refund
    refund.status = 'rejected'
    refund.admin_notes = admin_notes
    refund.resolved_at = timezone.now()
    refund.save()
    
    # Update order back to completed
    order = refund.order
    order.status = 'completed'
    order.save()
    
    # TODO: Notify buyer
    
    return Response({
        "success": True,
        "message": "Refund rejected",
        "refund": RefundRequestSerializer(refund).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_refunds(request):
    """
    List all pending refunds (Admin only)
    
    GET /api/marketplace/refunds/pending/
    """
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refunds = RefundRequest.objects.filter(
        status='pending'
    ).select_related('order', 'requester').order_by('-created_at')
    
    serializer = RefundRequestSerializer(refunds, many=True)
    return Response(serializer.data)
