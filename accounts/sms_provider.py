from django.conf import settings


def get_sms_service():
    provider = (getattr(settings, "SMS_PROVIDER", "") or "sendchamp").strip().lower()

    if provider == "smartsms":
        from .smartsms_service import smartsms_service

        return smartsms_service

    if provider == "termii":
        from .sms_service import termii_service

        return termii_service

    # Default/fallback
    from .sendchamp_service import sendchamp_service

    return sendchamp_service

