import logging
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from accounts.models import Profile
from accounts.sms_provider import get_sms_service

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix='campusdeal-bg')


def enqueue_background_task(task_name, func, *args, **kwargs):
    def _wrapped():
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - background safeguards
            logger.exception("Background task failed: %s", task_name)
            return exc

    return _EXECUTOR.submit(_wrapped)


def run_after_commit(task_name, func, *args, **kwargs):
    transaction.on_commit(lambda: enqueue_background_task(task_name, func, *args, **kwargs))


def send_sms_notification(phone_number, message):
    sms_service = get_sms_service()
    return sms_service.send_sms(phone_number, message)


def send_user_sms_notification(user, message):
    phone_number = getattr(getattr(user, 'profile', None), 'phone_number', None)
    if not phone_number:
        logger.warning("Cannot send SMS notification: missing phone number for user %s", getattr(user, 'id', None))
        return {'success': False, 'error': 'Missing phone number'}

    return send_sms_notification(phone_number, message)


def send_finance_alert(subject, message):
    recipients = getattr(settings, 'FINANCE_ALERT_EMAILS', [])
    if recipients:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=recipients,
            fail_silently=True,
        )
    logger.warning("FINANCE ALERT: %s | %s", subject, message)


def refresh_financial_reconciliation_snapshot(reason='scheduled'):
    from .models import PlatformFinancials
    from .payment_service import paystack_service

    result = paystack_service.check_balance()
    if not result.get('success'):
        send_finance_alert(
            subject='CampusDeal Paystack balance check failed',
            message=f"Reason: {reason}\nError: {result.get('error')}",
        )
        return {'success': False, 'error': result.get('error')}

    financials = PlatformFinancials.get_instance()
    observed_balance = result['balance']
    expected_status = financials.reconciliation_status()

    financials.paystack_balance = observed_balance
    financials.save(update_fields=['paystack_balance', 'last_updated'])

    if expected_status != 'BALANCED ✅':
        send_finance_alert(
            subject='CampusDeal reconciliation mismatch',
            message=(
                f"Reason: {reason}\n"
                f"Status before refresh: {expected_status}\n"
                f"Observed Paystack balance: {observed_balance}\n"
                f"User liability: {financials.user_funds_liability}\n"
                f"Platform revenue: {financials.platform_revenue}"
            ),
        )

    return {'success': True, 'balance': observed_balance, 'status': expected_status}
