from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from users.models import User


class TokenAuthMiddleware:
    """
    Bearer Token authorization middleware
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """Ищем в нем ключ Authorization со значением 'token KEY' """
        qs = parse_qs(scope['query_string'])
        if b'Authorization' in qs:
            try:
                token_name, token_key = qs[b'Authorization'][0].decode().split(' ')
                if token_name.lower() == 'token':
                    token = await sync_to_async(Token.objects.get)(key=token_key)
                    scope['user'] = await sync_to_async(User.objects.get)(id=token.user_id)
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return await self.inner(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
