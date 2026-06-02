import re

from django.conf import settings


class AllowedWebSocketOriginMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if not self._is_allowed(scope):
            await send({'type': 'websocket.close', 'code': 4403})
            return

        return await self.inner(scope, receive, send)

    def _is_allowed(self, scope):
        headers = dict(scope.get('headers', []))
        origin = headers.get(b'origin', b'').decode('utf-8')

        if settings.DEBUG:
            return True

        if not origin:
            return False

        if origin in getattr(settings, 'CORS_ALLOWED_ORIGINS', []):
            return True

        for pattern in getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', []):
            if re.match(pattern, origin):
                return True

        return False
