"""
SMS Service for Termii Integration
Handles phone verification and notifications
"""
import requests
from django.conf import settings


class TermiiService:
    """Service class for Termii SMS API"""
    
    def __init__(self):
        self.api_key = settings.TERMII_API_KEY
        self.sender_id = settings.TERMII_SENDER_ID
        self.base_url = 'https://api.ng.termii.com/api'
    
    def send_sms(self, phone_number, message):
        """Send SMS via Termii"""
        url = f'{self.base_url}/sms/send'
        
        payload = {
            'to': phone_number,
            'from': self.sender_id,
            'sms': message,
            'type': 'plain',
            'channel': 'generic',
            'api_key': self.api_key
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
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
termii_service = TermiiService()
