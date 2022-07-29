from rest_framework import serializers, fields
from djoser.serializers import UserSerializer as BaseUserSerializer

import gooru.settings as settings
from users.serializers import UserSmallSerializer
from .models import *

class UserSmallSerializerWebSocket(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'role')
    
    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['avatar'] = settings.HOSTNAME + data['avatar']
        return data

class MessageSerializer(serializers.ModelSerializer):
    '''
    Serializer для работы с сообщениями
    '''
    sender = UserSmallSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'text', 'created_at', 'sender', 'ticket')