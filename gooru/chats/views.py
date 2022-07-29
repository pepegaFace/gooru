import json
from django.core import serializers
from django.shortcuts import render
from chats.models import Message
#from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, views, viewsets, mixins
from django.db.models import Q
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, AllowAny

from chats.serializers import MessageSerializer
from gooru.permissions import IsSelf
from django_filters.rest_framework import DjangoFilterBackend

from users.models import UserManager, User


class MessageViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    '''
    ViewSet для работы с сообщениями
    '''
    queryset = Message.objects.all()
    permission_classes = (IsSelf,)
    serializer_class = MessageSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('ticket__id', 'sender__id')
    pagination_class = None
    
    def get_queryset(self):
        current_user = self.request.user
        if current_user.role == User.is_default:
            return self.queryset.filter(ticket__user_id=current_user.id).order_by('created_at')
        elif current_user.role == User.is_manager:
            users = UserManager.objects.filter(manager_id=current_user.id).values('user')
            return self.queryset.filter(ticket__user_id__in=users).order_by('created_at')
        else:
            return self.queryset