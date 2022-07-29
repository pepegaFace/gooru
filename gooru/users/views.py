from requests import request
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import generics, status, views, viewsets, mixins
from rest_framework.response import Response
from gooru.permissions import *
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from .paginators import StandartResultsSetPagination
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
import csv, json
import django_excel as excel
from datetime import datetime
from rest_framework import filters
from gooru import settings
from .utils import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


def get_table_fields_by_id(index, table):
    """
    Получение данных полей rows из таблицы table по index
    SQL запрос: SELECT * FROM "users_table" WHERE "users_table"."id" = index
    @param table: таблица в базе данных
    @param index: идентификатор
    @return: значения из всех столбцов
    """
    query = table.objects.filter(
        id=index)
    result = []
    if query.values():
        result = query.values()[0]
    return result


class UserViewSet(mixins.RetrieveModelMixin, 
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin, 
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    CRUD для user
    Пользователь имеет доступ создать уч. запись и менять её
    Менеджер имеет доступ удалять, получать запись по pk и получать список уч. записей
    """

    queryset = User.objects.all()
    pagination_class = StandartResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = UserRegistrationSerializer
        elif self.action in ('update', 'partial_update'):
            self.serializer_class = UserUpdateSerializer
        else:
            self.serializer_class = MyUserSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (AllowAny, )
        elif self.action in ('update', 'partial_update', 'retrieve', 'destroy'):
            self.permission_classes = (IsSelf, )
        else:
            self.permission_classes = (IsManager, )
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset.none()
        elif self.request.user.role == User.is_default:
            return self.queryset.filter(pk=self.request.user.pk)
        else:
            return self.queryset


class UploadAvatarViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    parser_classes = (MultiPartParser, )
    permission_classes = (IsSelf, )
    serializer_class = UserUploadAvatarSerializer
    queryset = User.objects.all()

    def perform_update(self, serializer):
        serializer.save()

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)


class SupportTicketViewSet(mixins.RetrieveModelMixin, 
                            mixins.ListModelMixin, 
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.CreateModelMixin, 
                            viewsets.GenericViewSet):

    """
    ViewSet для работы с моделью 'SupportTicket'
    search^   Тип обращения, сообщение, статус
    """
    filter_backends = (filters.SearchFilter,)
    queryset = SupportTicket.objects.all()
    pagination_class = StandartResultsSetPagination
    search_fields = ('topic_type', 'message', 'status')

    def create(self, request, *args, **kwargs):
        data = request.data
        if request.user.is_authenticated:
            data['user'] = request.user.id
            data['phone_number'] = request.user.phone_number
            data['email'] = request.user.email
            data['name'] = request.user.username
        else:
            data['user'] = ""
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset.none()
        elif user.role == User.is_default:
            return self.queryset.filter(user=user.id).order_by('status')
        elif user.role == User.is_manager:
            users = UserManager.objects.filter(manager_id=user.id).values('user')
            return self.queryset.filter(user_id__in=users).order_by('status')
        else:
            return self.queryset.order_by('status')

    def get_permissions(self):
        custom_match = {
            'create': AllowAny,
            'list': IsSelf,
            'retrieve': IsSelf,
            'update': IsManager,
            'partial_update': IsManager,
            'destroy': IsManager,
        }
        self.permission_classes = (custom_match.get(self.action, IsManager), )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = SupportTicketUserSerializer
        else:
            self.serializer_class = SupportTicketSerializer

        return super().get_serializer_class()

class FavoritesViewSet(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):

    """
    ViewSet для работы с моделью 'Favorite'
    """

    serializer_class = FavoritesSerializer
    queryset = Favorite.objects.all()
    pagination_class = StandartResultsSetPagination

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, 
                        status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user.id)

    def get_permissions(self):
        custom_match = {
            'create': IsSelf,
            'list': IsSelf,
            'retrieve': IsSelf,
            'update': IsSelf,
            'partial_update': IsSelf,
            'destroy': IsSelf,
        }
        self.permission_classes = (custom_match.get(self.action, IsManager),)
        return super().get_permissions()

    def get_serializer_class(self):
        self.serializer_class = FavoritesSerializer
        return self.serializer_class


class ParserViewSet(mixins.ListModelMixin, 
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    Viewset для парсеров в парсоурсах
    """
    serializer_class = ParserSerializer
    queryset = Parser.objects.all()

    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('parsource', 'parsource__data_source', 
                        'parsource__name', 'parsource__condition')
    search_fields = ('title', 'article', 'url')

    pagination_class = StandartResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.role == User.is_default:
            return self.queryset.filter(parsource__user=user)
        else:
            return self.queryset

    def get_permissions(self):
        if self.action in ('retrieve', 'list', 'update', 'destroy'):
            self.permission_classes = (IsSelf, )
        else:
            self.permission_classes = (IsManager, )

        return super().get_permissions()


class NotifyViewSet(mixins.ListModelMixin, 
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):

    queryset = Notify.objects.all()
    permission_classes = (IsSelf, )
    pagination_class = StandartResultsSetPagination

    def perform_update(self, serializer):
        serializer.save(checked=True, date_checked=datetime.now())

    def get_queryset(self):
        return self.queryset.filter(Q(user=self.request.user)&Q(checked=False))

    def get_serializer_class(self):
        if self.action == ('update', 'retrieve', 'list') and (self.request.user.is_anonymous or self.request.user.role == User.is_default):
            self.serializer_class = NotifyUserSerializer
        else:
            self.serializer_class = NotifySerializer

        return self.serializer_class


class ParsourceViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):

    queryset = Parsource.objects.all()
    pagination_class = StandartResultsSetPagination
    serializer_class = ParsourceSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('user__id', 'name', 
                        'data_source', 'condition', 
                        'is_view')

    def get_queryset(self):
        user = self.request.user
        if user.role == User.is_default:
            return self.queryset.filter(user_id=user.id)
        else:
            return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, 
                        status=status.HTTP_201_CREATED, headers=headers)

    def get_permissions(self):
        match_case = {
            'retrieve': IsSelf,
            'list': IsSelf,
            'create': IsSelf,
            'update': IsSelf,
            'partial_update': IsSelf,
            'destroy': IsSelf,
        }

        self.permission_classes = (match_case.get(self.action, IsManager), )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.user.role == User.is_default and self.action in ('create', 'update'):
            self.serializer_class = ParsourceUserSerializer
        else:
            self.serializer_class = ParsourceSerializer
        return self.serializer_class


class UploadScreenShotViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    parser_classes = (MultiPartParser, )
    permission_classes = (IsSelf, )
    serializer_class = UserUploadScreenSerializer
    queryset = Parsource.objects.all()

    def perform_update(self, serializer):
        serializer.save()

    def get_queryset(self):
        return Parsource.objects.filter(user=self.request.user)


class DownloadParserViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    ViewSet возвращающий файл в ответ
    """

    queryset = Parser.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('parsource', 'parsource__data_source', 
                        'parsource__name', 'parsource__condition')
    
    def list(self, request, type):
        data = self.filter_queryset(self.get_queryset())
        data = ParserToFileSerializer(data, many=True).data
        
        for item in data:
            item['parsource'] = Parsource.objects.get(id=item['parsource']).name \
                                    if item['parsource'] is not None else 'Empty'

        response = None
        if type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="export.csv"'
            writer = csv.DictWriter(response, fieldnames=['article', 'title', 'id', 'parsource', 'url'])
            writer.writeheader()
            writer.writerows(data)
        elif type == 'json':
            response = HttpResponse(content_type='text/json')
            response['Content-Disposition'] = 'attachment; filename="export.json"'
            json.dump(data, response)
        elif type == 'xls':
            sheet = excel.pe.Sheet([[item['id'], item['parsource'], item['url'], item['title'], item['article']]
                                        for item in data], 
                                    colnames=['id', 'parsource', 'url', 'article', 'title',])
            response = excel.make_response(sheet, 'xlsx', file_name='export')
        else:
            response = Response({'message':'Invalid type'}, status=status.HTTP_404_NOT_FOUND)
        return response

    def get_queryset(self):
        user = self.request.user
        if user.role == User.is_default:
            return self.queryset.filter(parsource__user=user)
        else:
            return self.queryset

    def get_permissions(self):
        self.permission_classes = (IsSelf, )
        return super().get_permissions()


class BriefViewSet(mixins.CreateModelMixin, 
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    queryset = Brief.objects.all()
    serializer_class = BriefSerializer
    pagination_class = StandartResultsSetPagination

    def get_permissions(self):
        if self.action in ('create',):
            self.permission_classes = (AllowAny, )
        else:
            self.permission_classes = (IsManager, )
        return super().get_permissions()


class UserManagerViewSet(mixins.CreateModelMixin, 
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    
    queryset = UserManager.objects.all()
    permission_classes = (IsManager, )
    serializer_class = UserManagerSerializer
    pagination_class = StandartResultsSetPagination


class MultiActionViewSet(viewsets.ViewSet):
    subjects = {
        'parsource': Parsource,
        'parser': Parser,
        'favorites': Favorite,
        # 'supportticket': SupportTicket,
        'notify': Notify,
        'users': User
    }

    permission_classes = (IsSelf,)
    serializer_class = MultiActionSerializer
    
    @action(detail=False, methods=['delete'])
    def delete(self, request):
        data = self.request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        
        user_id = self.request.user.id
        self.queryset = self.subjects[data['model']].objects.filter(
            Q(user_id=user_id)&Q(id__in=data['ids'])).delete()
        return Response({'msg': 'Removed!'}, status=200)


class UserTariffViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):

    queryset = UserTariff.objects.all()
    permission_classes = (AllowAny, )

    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action == 'create' :
            self.serializer_class = UserTariffCreateSerializer
        else:
            self.serializer_class = UserTariffSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('list', ):
            self.permission_classes = (AllowAny, )
        else:
            self.permission_classes = (IsManager, )
        return super().get_permissions()


class TariffViewSet(mixins.CreateModelMixin, 
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    
    queryset = Tariff.objects.all()

    permission_classes = (AllowAny, )

    serializer_class = TariffSerializer

    def get_permissions(self):
        actions = {
            'retrieve': IsSelf,
            'list': AllowAny,
            'create': IsManager,
            'update': IsManager,
            'partial_update': IsManager,
            'destroy': IsManager,
        }
        self.permission_classes = (actions.get(self.action, IsManager), )
        return super().get_permissions()

class UserVerifyViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=('get', ), detail=False)
    def email(self, request, uid=None, token=None):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.verified = True
            user.save()

        return HttpResponseRedirect(redirect_to='https://compas-goo.ru/#/login')


class UserComment(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    queryset = Comment.objects.all()
    permission_classes = (IsSelf,)
    serializer_class = UserCommentSerializer

    pagination_class = None