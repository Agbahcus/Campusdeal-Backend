"""
Sendchamp SMS Service
Handles phone verification and notifications via Sendchamp API
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SendchampService:
    """Service class for Sendchamp SMS API"""
    
    def __init__(self):
        self.access_key = (
            getattr(settings, 'SENDCHAMP_ACCESS_KEY', '')
            or getattr(settings, 'SENDCHAMP_PUBLIC_KEY', '')
            or getattr(settings, 'SENDCHAMP_SECRET_KEY', '')
        )
        self.sender_id = getattr(settings, 'SENDCHAMP_SENDER_ID', 'Sendchamp')
        self.base_url = getattr(settings, 'SENDCHAMP_BASE_URL', 'https://api.sendchamp.com/api/v1')

    @staticmethod
    def _normalize_phone_number(phone_number):
        normalized = str(phone_number).strip()
        if normalized.startswith('+'):
            normalized = normalized[1:]
        return normalized
    
    def send_sms(self, phone_number, message):
        """
        Send SMS via Sendchamp
        
        Args:
            phone_number: Recipient phone number (format: +234XXXXXXXXXX)
            message: SMS message content
            
        Returns:
            dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
        """
        if not self.access_key:
            return {
                'success': False,
                'error': 'Sendchamp credentials not configured (SENDCHAMP_ACCESS_KEY / SENDCHAMP_PUBLIC_KEY)',
            }

        url = f'{self.base_url}/sms/send'
        
        headers = {
            'Authorization': f'Bearer {self.access_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'to': self._normalize_phone_number(phone_number),
            'sender_name': self.sender_id,
            'message': message,
            'route': 'non_dnd'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"SMS sent successfully to {phone_number}")
            return {'success': True, 'data': data}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_verification_code(self, phone_number, code):
        """Send verification code"""
        message = f"Your CampusDeal verification code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone_number, message)
    
    def send_password_reset_code(self, phone_number, code):
        """Send password reset code"""
        message = f"Your CampusDeal password reset code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone_number, message)


# Singleton instance
sendchamp_service = SendchampService()
