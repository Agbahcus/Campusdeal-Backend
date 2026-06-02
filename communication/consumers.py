from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async

from .models import Chat
from .realtime import chat_group_name, serialize_message
from .services import process_chat_message, mark_chat_messages_read


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope.get('user', AnonymousUser())

        if not self.user or self.user.is_anonymous:
            await self.close(code=4401)
            return

        self.chat = await self._get_chat()
        if not self.chat:
            await self.close(code=4404)
            return

        if not await self._is_participant():
            await self.close(code=4403)
            return

        self.group_name = chat_group_name(self.chat.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_json({
            'type': 'chat.connected',
            'chat_id': self.chat.id,
            'messages': await self._get_recent_messages(),
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action') or content.get('type')

        if action == 'send_message':
            await self._handle_send_message(content)
        elif action == 'mark_read':
            await self._handle_mark_read()
        elif action == 'typing':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.typing',
                    'payload': {
                        'chat_id': self.chat.id,
                        'user_id': self.user.id,
                    },
                },
            )

    async def _handle_send_message(self, content):
        text = (content.get('text') or '').strip()
        if not text:
            await self.send_json({'type': 'error', 'error': 'Message cannot be empty'})
            return

        result = await sync_to_async(process_chat_message, thread_sensitive=True)(
            self.chat,
            self.user,
            text,
            True,
        )

        if result['success']:
            await self.send_json({
                'type': 'message.sent',
                'message': serialize_message(result['message']),
            })
            return

        await self.send_json({
            'type': 'message.blocked',
            'error': 'Message blocked',
            'warning': result['warning'],
            'strike_number': result['strike_number'],
            'strikes_remaining': result['strikes_remaining'],
            'account_suspended': result['account_suspended'],
            'flags': result['flags'],
        })

    async def _handle_mark_read(self):
        updated = await sync_to_async(mark_chat_messages_read, thread_sensitive=True)(
            self.chat,
            self.user,
            True,
        )
        await self.send_json({
            'type': 'messages.read',
            'chat_id': self.chat.id,
            'messages_marked_read': updated,
        })

    async def chat_message(self, event):
        await self.send_json({
            'type': 'chat.message',
            **event['payload'],
        })

    async def chat_warning(self, event):
        await self.send_json({
            'type': 'chat.warning',
            **event['payload'],
        })

    async def chat_read(self, event):
        await self.send_json({
            'type': 'chat.read',
            **event['payload'],
        })

    async def chat_typing(self, event):
        await self.send_json({
            'type': 'chat.typing',
            **event['payload'],
        })

    async def _get_chat(self):
        return await sync_to_async(get_object_or_404, thread_sensitive=True)(Chat, id=self.chat_id)

    async def _is_participant(self):
        return await sync_to_async(
            lambda: self.user in [self.chat.participant_1, self.chat.participant_2],
            thread_sensitive=True,
        )()

    async def _get_recent_messages(self):
        messages = await sync_to_async(
            lambda: list(self.chat.messages.select_related('sender', 'sender__profile').order_by('-created_at')[:50][::-1]),
            thread_sensitive=True,
        )()
        return [serialize_message(message) for message in messages]
