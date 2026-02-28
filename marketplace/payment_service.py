"""
Payment service for Paystack integration
Handles payment initialization, verification, and transfers
"""
import requests
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import hmac
import hashlib


class PaystackService:
    """Service class for Paystack API operations"""
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = 'https://api.paystack.co'
    
    def _get_headers(self):
        """Get headers for Paystack API requests"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_payment(self, email, amount, reference, callback_url, metadata=None):
        """
        Initialize a Paystack transaction
        
        Args:
            email: Customer email
            amount: Amount in kobo (Naira * 100)
            reference: Unique transaction reference
            callback_url: URL to redirect after payment
            metadata: Additional data to attach to transaction
        
        Returns:
            dict: Response from Paystack API
        """
        url = f'{self.base_url}/transaction/initialize'
        
        payload = {
            'email': email,
            'amount': int(amount),  # Must be in kobo
            'reference': reference,
            'callback_url': callback_url,
        }
        
        if metadata:
            payload['metadata'] = metadata
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Payment initialization failed: {str(e)}'
            }
    
    def verify_payment(self, reference):
        """
        Verify a payment transaction
        
        Args:
            reference: Transaction reference to verify
        
        Returns:
            dict: Verification response from Paystack
        """
        url = f'{self.base_url}/transaction/verify/{reference}'
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Payment verification failed: {str(e)}'
            }
    
    def verify_webhook_signature(self, payload, signature):
        """
        Verify Paystack webhook signature
        
        Args:
            payload: Raw request body
            signature: X-Paystack-Signature header value
        
        Returns:
            bool: True if signature is valid
        """
        hash_obj = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha512
        )
        expected_signature = hash_obj.hexdigest()
        return expected_signature == signature
    
    def create_transfer_recipient(self, account_number, bank_code, name):
        """
        Create a transfer recipient for payouts
        
        Args:
            account_number: Recipient bank account number
            bank_code: Recipient bank code
            name: Recipient account name
        
        Returns:
            dict: Response with recipient code
        """
        url = f'{self.base_url}/transferrecipient'
        
        payload = {
            'type': 'nuban',
            'name': name,
            'account_number': account_number,
            'bank_code': bank_code,
            'currency': 'NGN'
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Recipient creation failed: {str(e)}'
            }
    
    def initiate_transfer(self, amount, recipient_code, reason, reference):
        """
        Initiate a transfer (payout to seller)
        
        Args:
            amount: Amount in kobo
            recipient_code: Paystack recipient code
            reason: Transfer reason/description
            reference: Unique transfer reference
        
        Returns:
            dict: Transfer response
        """
        url = f'{self.base_url}/transfer'
        
        payload = {
            'source': 'balance',
            'amount': int(amount),
            'recipient': recipient_code,
            'reason': reason,
            'reference': reference
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Transfer failed: {str(e)}'
            }
    
    def list_banks(self):
        """
        Get list of Nigerian banks
        
        Returns:
            dict: List of banks with codes
        """
        url = f'{self.base_url}/bank'
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Failed to fetch banks: {str(e)}'
            }
    
    def verify_account(self, account_number, bank_code):
        """
        Verify a bank account number
        
        Args:
            account_number: Account number to verify
            bank_code: Bank code
        
        Returns:
            dict: Account verification response with account name
        """
        url = f'{self.base_url}/bank/resolve'
        
        params = {
            'account_number': account_number,
            'bank_code': bank_code
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Account verification failed: {str(e)}'
            }


# Singleton instance
paystack_service = PaystackService()