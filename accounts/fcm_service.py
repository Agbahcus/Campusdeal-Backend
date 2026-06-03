"""
Firebase Cloud Messaging (FCM) push notification service
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

FCM_URL = 'https://fcm.googleapis.com/fcm/send'


def _get_server_key():
    return getattr(settings, 'FCM_SERVER_KEY', '')


def send_push_notification(token, title, body, data=None):
    """
    Send a push notification to a single device token.
    Returns {'success': True} or {'success': False, 'error': str}
    """
    server_key = _get_server_key()
    if not server_key:
        logger.warning('FCM_SERVER_KEY not configured — skipping push notification')
        return {'success': False, 'error': 'FCM not configured'}

    payload = {
        'to': token,
        'notification': {
            'title': title,
            'body': body,
            'sound': 'default',
        },
        'data': data or {},
        'priority': 'high',
    }

    try:
        response = requests.post(
            FCM_URL,
            json=payload,
            headers={
                'Authorization': f'key={server_key}',
                'Content-Type': 'application/json',
            },
            timeout=10,
        )
        result = response.json()
        if result.get('success') == 1:
            return {'success': True}
        logger.warning('FCM send failed: %s', result)
        return {'success': False, 'error': str(result)}
    except Exception as exc:
        logger.warning('FCM exception: %s', exc)
        return {'success': False, 'error': str(exc)}


def notify_user(user, title, body, notification_type='general', related_id='', data=None):
    """
    Send push notification to all active device tokens for a user
    and save a Notification record.
    """
    from .models import DeviceToken, Notification

    # Save to notification center
    Notification.objects.create(
        user=user,
        title=title,
        body=body,
        notification_type=notification_type,
        related_id=str(related_id),
    )

    # Send to all active device tokens
    if not _get_server_key():
        return

    tokens = DeviceToken.objects.filter(user=user, is_active=True).values_list('token', flat=True)
    fcm_data = data or {}
    fcm_data.update({'type': notification_type, 'related_id': str(related_id)})

    for token in tokens:
        result = send_push_notification(token, title, body, fcm_data)
        if not result['success']:
            # Deactivate invalid tokens
            if 'InvalidRegistration' in str(result.get('error', '')) or \
               'NotRegistered' in str(result.get('error', '')):
                DeviceToken.objects.filter(token=token).update(is_active=False)
