"""
SmartSMS (smartsms.ng) SMS Service
Handles phone verification and notifications via SmartSMS JSON API
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SmartSMSService:
    """
    Service class for SmartSMS Nigeria JSON API.

    Expected settings:
      - SMARTSMS_USERNAME (usually your login email)
      - SMARTSMS_API_KEY
      - SMARTSMS_SENDER_ID
      - SMARTSMS_BASE_URL (default: https://www.smartsms.ng/api)
      - SMARTSMS_DNDSENDER (optional, default: 0)
    """

    def __init__(self):
        self.username = getattr(settings, "SMARTSMS_USERNAME", "")
        self.api_key = getattr(settings, "SMARTSMS_API_KEY", "")
        self.sender_id = getattr(settings, "SMARTSMS_SENDER_ID", "CampusDeal")
        self.base_url = getattr(settings, "SMARTSMS_BASE_URL", "https://www.smartsms.ng/api").rstrip("/")
        self.dndsender = int(getattr(settings, "SMARTSMS_DNDSENDER", 0) or 0)

    @staticmethod
    def _normalize_msisdn(phone_number: str) -> str:
        if not phone_number:
            return ""
        normalized = str(phone_number).strip().replace(" ", "")
        if normalized.startswith("+"):
            normalized = normalized[1:]
        return normalized

    def send_sms(self, phone_number, message):
        """
        Send SMS via SmartSMS

        Args:
            phone_number: Recipient phone number (format: +234XXXXXXXXXX or 234XXXXXXXXXX)
            message: SMS message content

        Returns:
            dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
        """
        if not self.username or not self.api_key:
            return {"success": False, "error": "SmartSMS credentials not configured (SMARTSMS_USERNAME/SMARTSMS_API_KEY)"}

        msisdn = self._normalize_msisdn(phone_number)
        if not msisdn:
            return {"success": False, "error": "Invalid phone number"}

        url = f"{self.base_url}/sendsms.json"

        payload = {
            "username": self.username,
            "apikey": self.api_key,
            "sender": self.sender_id,
            "messagetext": message,
            "flash": 0,
            "recipients": msisdn,
        }
        if self.dndsender in (0, 1):
            payload["dndsender"] = self.dndsender

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # SmartSMS commonly returns status strings like "SUCCESS"/"INSUFFICIENT_CREDIT"
            status_value = str(data.get("status") or data.get("Status") or "").upper()
            if status_value and status_value not in ("SUCCESS", "OK"):
                return {"success": False, "error": status_value, "data": data}

            logger.info("SMS sent via SmartSMS to %s", msisdn)
            return {"success": True, "data": data}

        except requests.exceptions.RequestException as e:
            logger.error("Failed to send SMS via SmartSMS to %s: %s", msisdn, str(e))
            return {"success": False, "error": str(e)}

    def send_verification_code(self, phone_number, code):
        message = f"Your CampusDeal verification code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone_number, message)

    def send_password_reset_code(self, phone_number, code):
        message = f"Your CampusDeal password reset code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone_number, message)


smartsms_service = SmartSMSService()

