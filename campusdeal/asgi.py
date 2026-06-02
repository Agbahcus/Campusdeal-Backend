"""
ASGI config for campusdeal project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from communication.routing import websocket_urlpatterns
from communication.ws_middleware import JwtAuthMiddlewareStack
from communication.ws_origin import AllowedWebSocketOriginMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusdeal.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedWebSocketOriginMiddleware(
        JwtAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
