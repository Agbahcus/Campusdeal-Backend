from django.db import transaction

from .content_moderator import moderator
from .models import Message, ModeratedMessageLog
from .realtime import broadcast_chat_message, broadcast_chat_read


def process_chat_message(chat, sender, message_text, emit_events=True):
    scan_result = moderator.scan_message(message_text)

    with transaction.atomic():
        if scan_result['is_clean']:
            message = Message.objects.create(
                chat=chat,
                sender=sender,
                text=message_text,
            )
            chat.last_message = message_text[:100]
            chat.save(update_fields=['last_message', 'last_message_time'])

            if emit_events:
                broadcast_chat_message(chat, message)

            return {
                'success': True,
                'message': message,
                'warning': None,
                'flags': [],
            }

        profile = sender.profile
        profile.chat_strikes += 1
        current_strike = profile.chat_strikes

        ModeratedMessageLog.objects.create(
            original_sender=sender,
            chat=chat,
            original_text=message_text,
            detected_flags=', '.join(scan_result['flags']),
            action_taken='deleted',
            strike_number=current_strike,
        )

        warning_text = scan_result['warning_message']
        strike_message = moderator.get_strike_message(current_strike)

        if current_strike >= 3:
            profile.is_suspended = True
            profile.suspension_reason = '3 chat policy violations - sharing contact information'

        profile.save()

        system_message = Message.objects.create(
            chat=chat,
            sender=sender,
            text=f'{warning_text}\n\n{strike_message}',
            is_system_warning=True,
            is_flagged=True,
            flagged_for='POLICY',
            is_deleted_by_system=True,
        )

        chat.last_message = warning_text[:100]
        chat.save(update_fields=['last_message', 'last_message_time'])

        if emit_events:
            broadcast_chat_message(chat, system_message, event_type='chat.warning')

        return {
            'success': False,
            'message': None,
            'warning': warning_text,
            'flags': scan_result['flags'],
            'strike_number': current_strike,
            'strikes_remaining': max(0, 3 - current_strike),
            'account_suspended': current_strike >= 3,
        }


def mark_chat_messages_read(chat, user, emit_events=True):
    updated = chat.messages.filter(
        is_read=False
    ).exclude(
        sender=user
    ).update(is_read=True)

    if emit_events:
        broadcast_chat_read(chat, user.id, updated)

    return updated
