"""
Payment service for Paystack integration.
Handles payment initialization, verification, transfers, and balance checks.
"""

from decimal import Decimal
import hashlib
import hmac

import requests
from django.conf import settings


class PaystackService:
    """Service class for Paystack API operations."""

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = 'https://api.paystack.co'

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }

    @staticmethod
    def _to_kobo(amount):
        return int(Decimal(str(amount)) * 100)

    @staticmethod
    def _normalize_result(response_json):
        if not isinstance(response_json, dict):
            return {
                'success': False,
                'error': 'Unexpected response format',
            }

        if response_json.get('status'):
            return {
                'success': True,
                'data': response_json.get('data', {}),
                'message': response_json.get('message', ''),
            }

        return {
            'success': False,
            'error': response_json.get('message', 'Request failed'),
            'data': response_json.get('data', {}),
        }

    def initialize_payment(self, email, amount, reference, callback_url, metadata=None):
        url = f'{self.base_url}/transaction/initialize'
        payload = {
            'email': email,
            'amount': int(amount),
            'reference': reference,
            'callback_url': callback_url,
        }
        if metadata:
            payload['metadata'] = metadata

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            return {
                'status': False,
                'message': f'Payment initialization failed: {exc}',
            }

    def verify_payment(self, reference):
        url = f'{self.base_url}/transaction/verify/{reference}'

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            return {
                'status': False,
                'message': f'Payment verification failed: {exc}',
            }

    def verify_webhook_signature(self, payload, signature):
        if not signature:
            return False

        hash_obj = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha512,
        )
        expected_signature = hash_obj.hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    def verify_account(self, account_number, bank_code):
        url = f'{self.base_url}/bank/resolve'
        params = {
            'account_number': account_number,
            'bank_code': bank_code,
        }

        try:
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            payload = response.json()
            return self._normalize_result(payload) | {
                'account_number': payload.get('data', {}).get('account_number'),
                'account_name': payload.get('data', {}).get('account_name'),
            }
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': str(exc)}

    def verify_account_number(self, account_number, bank_code):
        return self.verify_account(account_number, bank_code)

    def create_transfer_recipient(self, account_number, bank_code, account_name):
        url = f'{self.base_url}/transferrecipient'
        payload = {
            'type': 'nuban',
            'name': account_name,
            'account_number': account_number,
            'bank_code': bank_code,
            'currency': 'NGN',
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            normalized = self._normalize_result(response.json())
            if normalized['success']:
                normalized['recipient_code'] = normalized['data'].get('recipient_code')
            return normalized
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': str(exc)}

    def initiate_transfer(self, amount, recipient_code, reason, reference=None):
        url = f'{self.base_url}/transfer'
        payload = {
            'source': 'balance',
            'amount': self._to_kobo(amount),
            'recipient': recipient_code,
            'reason': reason,
        }
        if reference:
            payload['reference'] = reference

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            normalized = self._normalize_result(response.json())
            if normalized['success']:
                normalized['transfer_code'] = normalized['data'].get('transfer_code')
                normalized['reference'] = normalized['data'].get('reference')
                normalized['status'] = normalized['data'].get('status')
                normalized['amount'] = amount
            return normalized
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': str(exc)}

    def list_banks(self):
        url = f'{self.base_url}/bank'

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            return {
                'status': False,
                'message': f'Failed to fetch banks: {exc}',
            }

    def check_balance(self):
        url = f'{self.base_url}/balance'

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get('status'):
                balance = data.get('data', {}).get('balance', 0)
                return {'success': True, 'balance': Decimal(str(balance)) / 100, 'data': data.get('data', {})}
            return {'success': False, 'error': data.get('message', 'Failed to fetch balance')}
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': str(exc)}


# Singleton instance
paystack_service = PaystackService()
