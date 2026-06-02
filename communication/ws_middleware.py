from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser, User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class JwtQueryAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            scope['user'] = await self._get_user(token)
        elif 'user' not in scope:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

    @staticmethod
    def _get_user_from_token(token):
        try:
            validated_token = AccessToken(token)
            user_id = validated_token.get('user_id')
            if not user_id:
                return AnonymousUser()
            return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist, Exception):
            return AnonymousUser()

    async def _get_user(self, token):
        from asgiref.sync import sync_to_async

        return await sync_to_async(self._get_user_from_token, thread_sensitive=True)(token)


def JwtAuthMiddlewareStack(inner):
    return JwtQueryAuthMiddleware(AuthMiddlewareStack(inner))
