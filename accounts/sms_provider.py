from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_sms_service():
    provider = (getattr(settings, "SMS_PROVIDER", "") or "sendchamp").strip().lower()

    if provider in {"sendchamp", "sendchamp_sms"}:
        from .sendchamp_service import sendchamp_service

        return sendchamp_service

    if provider == "smartsms":
        from .smartsms_service import smartsms_service

        return smartsms_service

    if provider == "termii":
        from .sms_service import termii_service

        return termii_service

    logger.warning("Unknown SMS_PROVIDER=%s, falling back to Sendchamp", provider)
    from .sendchamp_service import sendchamp_service

    return sendchamp_service
