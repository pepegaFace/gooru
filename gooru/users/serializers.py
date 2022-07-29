from random import choices
from unittest.util import _MAX_LENGTH
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers, fields
from .models import *


class MyUserSerializer(serializers.ModelSerializer):
    """
    Основной serializer для работы с пользователями.
    """
    class Meta:
        model=User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_superuser', 'avatar', 'phone_number', 'is_active')
        read_only_fields = ('username', 'email', 'role', 'is_superuser')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer для регистрации пользователей.
    """
    class Meta:
        model=User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password', )
        read_only_fields = ('username',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop("password", None)
        return response

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password')

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            validated_data['username'] = validated_data['email']
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop("password", None)
        return response

class UserSmallSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'role',)


class UserUploadAvatarSerializer(serializers.ModelSerializer):
    """
    Serializer для загрузки аватара пользователя.
    """

    class Meta(BaseUserRegistrationSerializer.Meta):
        model = User
        fields = ('avatar', )


class Test(BaseUserSerializer):
    """
    Serializer для тестирования данных пользователя.
    """
    class Meta(BaseUserSerializer.Meta):
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):
    """
    Serializer для работы с любимыми парсерами.
    """
    class Meta:
        model = Favorite
        fields = '__all__'


class SupportTicketSerializer(serializers.ModelSerializer):
    """
    Serializer для работы с записью тикетами в техподдержку.
    """
    user = UserSmallSerializer(read_only=True)
    class Meta:
        model = SupportTicket
        fields = '__all__'
        # exclude = ('user',)


class ParserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parser
        fields = '__all__'


class ParserToFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parser
        fields = '__all__'


class ParsourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parsource
        fields = '__all__'


class ParsourceUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parsource
        fields = ('user', 'name',  'data_source', 'description',
                  'parse_fields', 'url_detail')


class UserUploadScreenSerializer(serializers.ModelSerializer):
    """
    Serializer для загрузки скриншота пользователя.
    """

    class Meta:
        model = Parsource
        fields = ('screenshot', )


class SupportTicketUserSerializer(serializers.ModelSerializer):
    """
    Serializer для создания тикета пользователем
    """

    class Meta:
        model = SupportTicket
        fields = ['name', 'phone_number', 'email', 'message', 'topic_type', 'parser', 'user' ]


class NotifyUserSerializer(serializers.ModelSerializer):
    """
    Serializer для "прочтения" уведомления
    """

    class Meta:
        model = Notify
        fields = ['id', 'checked']


class NotifySerializer(serializers.ModelSerializer):
    """
    Serializer для создания уведомления
    """

    class Meta:
        model = Notify
        fields = '__all__'


class BriefSerializer(serializers.ModelSerializer):
    """
    Serializer для работы с брифами
    """

    fields_of_activity = fields.MultipleChoiceField(choices=Brief.FIELDS_OF_ACTIVITY)
    site_types = fields.MultipleChoiceField(choices=Brief.SITE_TYPES)
    additional_options = fields.MultipleChoiceField(choices=Brief.ADDITIONAL_OPTIONS)

    class Meta:
        model = Brief
        fields = '__all__'


class UserManagerSerializer(serializers.ModelSerializer):
    """
    Serializer для работы со связью пользователь – менеджер
    """

    class Meta:
        model = UserManager
        fields = '__all__'

class MultiActionSerializer(serializers.Serializer):
    MODEL_CHOICES = (
        ('parsource', 'parsource'),
        ('parser', 'parser'),
        ('favorites', 'favorites'),
        ('notify', 'notify'),
    )
    model = serializers.ChoiceField(choices=MODEL_CHOICES)
    ids = serializers.JSONField()


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'


class UserTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTariff
        fields = '__all__'


class UserTariffCreateSerializer(serializers.ModelSerializer):
    tariff = TariffSerializer()
    class Meta:
        model = UserTariff
        fields = ['user', 'tariff']


class UserCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'parser', 'comment']