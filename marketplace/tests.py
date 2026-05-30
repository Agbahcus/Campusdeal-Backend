from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from .models import (
    FinancialTransaction,
    ItemCategory,
    ItemListing,
    Order,
    PlatformFinancials,
    RefundRequest,
)


class MarketplaceFlowTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='+2348010000001',
            email='seller@example.com',
            password='StrongPass123',
        )
        self.buyer = User.objects.create_user(
            username='+2348010000002',
            email='buyer@example.com',
            password='StrongPass123',
        )
        Profile.objects.create(
            user=self.seller,
            phone_number='+2348010000001',
            primary_location='ilorin',
            phone_verified=True,
        )
        Profile.objects.create(
            user=self.buyer,
            phone_number='+2348010000002',
            primary_location='ilorin',
            phone_verified=True,
        )
        self.category = ItemCategory.objects.create(name='Books', icon='book')
        self.item = ItemListing.objects.create(
            seller=self.seller,
            title='Calculus Textbook',
            description='Good condition',
            category=self.category,
            condition='fairly_used',
            price=Decimal('10000.00'),
            location='ilorin',
            allow_pickup=True,
        )

    def _create_paid_paystack_order(self):
        self.client.force_authenticate(user=self.seller)
        order_response = self.client.post(
            reverse('marketplace:initiate-order'),
            {
                'item_id': self.item.id,
                'buyer_id': self.buyer.id,
                'delivery_method': 'pickup',
            },
            format='json',
        )
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(order_id=order_response.data['order_id'])
        order.paystack_reference = 'PAYSTACK-REF-1'
        order.save(update_fields=['paystack_reference'])
        return order

    @patch('marketplace.order_views.paystack_service.verify_payment')
    def test_paystack_payment_is_idempotent(self, mock_verify_payment):
        order = self._create_paid_paystack_order()
        mock_verify_payment.return_value = {
            'status': True,
            'data': {
                'status': 'success',
                'amount': int(order.total_amount * 100),
                'metadata': {'buyer_id': self.buyer.id},
            },
        }

        self.client.force_authenticate(user=self.buyer)
        first = self.client.post(
            reverse('marketplace:verify-payment'),
            {'reference': order.paystack_reference},
            format='json',
        )
        second = self.client.post(
            reverse('marketplace:verify-payment'),
            {'reference': order.paystack_reference},
            format='json',
        )

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(
            FinancialTransaction.objects.filter(
                related_order=order,
                transaction_type='payment_received',
            ).count(),
            1,
        )
        financials = PlatformFinancials.get_instance()
        self.assertEqual(financials.paystack_balance, order.total_amount)

    @patch('marketplace.order_views.paystack_service.verify_payment')
    def test_cancelled_paystack_order_reverses_ledger(self, mock_verify_payment):
        order = self._create_paid_paystack_order()
        mock_verify_payment.return_value = {
            'status': True,
            'data': {
                'status': 'success',
                'amount': int(order.total_amount * 100),
                'metadata': {'buyer_id': self.buyer.id},
            },
        }

        self.client.force_authenticate(user=self.buyer)
        verify_response = self.client.post(
            reverse('marketplace:verify-payment'),
            {'reference': order.paystack_reference},
            format='json',
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        cancel_response = self.client.post(
            reverse('marketplace:cancel-order', kwargs={'order_id': order.order_id}),
            format='json',
        )

        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        financials = PlatformFinancials.get_instance()
        self.assertEqual(financials.user_funds_liability, Decimal('0'))
        self.assertEqual(financials.platform_revenue, Decimal('0'))
        self.assertEqual(financials.paystack_balance, Decimal('0'))

    def test_only_seller_can_move_order_to_delivery_state(self):
        order = self._create_paid_paystack_order()
        order.status = 'paid'
        order.funds_held = True
        order.save(update_fields=['status', 'funds_held'])

        self.client.force_authenticate(user=self.buyer)
        blocked = self.client.patch(
            reverse('marketplace:update-order-status', kwargs={'order_id': order.order_id}),
            {'status': 'seller_preparing', 'notes': 'Packing'},
            format='json',
        )
        self.assertEqual(blocked.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.seller)
        allowed = self.client.patch(
            reverse('marketplace:update-order-status', kwargs={'order_id': order.order_id}),
            {'status': 'seller_preparing', 'notes': 'Packing'},
            format='json',
        )
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    @patch('marketplace.order_views.paystack_service.verify_payment')
    def test_refund_approval_updates_wallets_and_order_state(self, mock_verify_payment):
        order = self._create_paid_paystack_order()
        mock_verify_payment.return_value = {
            'status': True,
            'data': {
                'status': 'success',
                'amount': int(order.total_amount * 100),
                'metadata': {'buyer_id': self.buyer.id},
            },
        }

        self.client.force_authenticate(user=self.buyer)
        self.client.post(
            reverse('marketplace:verify-payment'),
            {'reference': order.paystack_reference},
            format='json',
        )

        order.status = 'completed'
        order.completed_at = None
        order.funds_released_to_seller = True
        order.save(update_fields=['status', 'completed_at', 'funds_released_to_seller'])

        seller_profile = self.seller.profile
        buyer_profile = self.buyer.profile
        seller_profile.wallet_balance = order.item_price
        buyer_profile.wallet_balance = Decimal('0.00')
        seller_profile.save(update_fields=['wallet_balance'])
        buyer_profile.save(update_fields=['wallet_balance'])

        refund_create = self.client.post(
            reverse('marketplace:request-refund', kwargs={'order_id': order.order_id}),
            {
                'reason': 'not_as_described',
                'detailed_explanation': 'The item was significantly different from the listing.',
            },
            format='json',
        )
        self.assertEqual(refund_create.status_code, status.HTTP_201_CREATED)

        refund = RefundRequest.objects.get(order=order)

        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123',
        )
        self.client.force_authenticate(user=admin)
        approve = self.client.post(
            reverse('marketplace:approve-refund', kwargs={'refund_id': refund.id}),
            {'admin_notes': 'Approved after review'},
            format='json',
        )

        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.buyer.profile.refresh_from_db()
        self.seller.profile.refresh_from_db()
        self.assertEqual(order.status, 'refunded')
        self.assertEqual(self.buyer.profile.wallet_balance, order.total_amount)
        self.assertEqual(self.seller.profile.wallet_balance, Decimal('0.00'))
