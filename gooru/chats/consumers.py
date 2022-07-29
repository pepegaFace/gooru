import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from users.models import SupportTicket, User, UserManager
from chats.serializers import UserSmallSerializerWebSocket
from chats.models import Message


class Consumer(AsyncWebsocketConsumer):
    async def read_message(self):
        unread_messages = await sync_to_async(Message.objects.filter)(ticket=self.ticket, status=False)
        messages = await sync_to_async(unread_messages.exclude)(sender_id=self.user.id)
        await sync_to_async(messages.update)(status=True)

    async def connect(self):
        '''
        Создание вебсокета. Названием комнаты служит SupportTicket.id
        '''

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = str(self.room_name)
        self.user = self.scope.get('user')
        if self.user is None or not self.user.is_authenticated:
            return await self.disconnect(400)

        ticket_id = self.room_group_name
        try:
            if self.user.role == User.is_default:
                self.ticket = await sync_to_async(SupportTicket.objects.get)(Q(id=ticket_id)&Q(user_id=self.user.id))
            elif self.user.role == User.is_manager:
                # Получаем всех клиентов которые связаны с менеджером,
                # далее из полученного queryset берем столбец с клиентами
                users = await sync_to_async((await sync_to_async(UserManager.objects.filter)(manager_id=self.user.id)).values)('user')
                self.ticket = await sync_to_async(SupportTicket.objects.get)(Q(id=ticket_id)&Q(user__in=users))
            else:
                self.ticket = await sync_to_async(SupportTicket.objects.get)(id=ticket_id)
        except SupportTicket.DoesNotExist:
            return await self.disconnect(400)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.read_message()
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.read_message()
        return await self.close(close_code)

    async def receive(self, text_data):
        '''
        Получение письма из вебсокета
        '''
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return await self.disconnect(401)

        if 'message' not in text_data_json:
            return await self.disconnect(400)

        message = text_data_json['message']
        newMessage = Message(sender=self.user, 
                            ticket=self.ticket, 
                            text=message)

        await sync_to_async(newMessage.save)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': newMessage.id,
                'text': newMessage.text,
                'created_at': str(newMessage.created_at),
                'sender' : UserSmallSerializerWebSocket(self.user).data
            }
        )

    async def chat_message(self, event):
        '''
        Отправка письма в вебсокет со стороны сервера
        '''

        await self.send(text_data=json.dumps(event))
