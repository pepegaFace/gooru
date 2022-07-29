from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate

from users.models import User, SupportTicket, UserManager, Notify
from users.views import SupportTicketViewSet, UserViewSet


class UserModelTest(TestCase):
    def setUp(self) -> None:
        User.objects.create(username='Manager1', role='Manager', password='Manager1', email='a@a.ru')
        User.objects.create(username='Manager2', role='Manager', password='Manager2', email='b@b.ru')

    def test_create_user(self):
        User.objects.create(username='user1', password='user1', email='c@c.ru')
        User.objects.create(username='user2', password='user2', email='d@d.ru')
        self.assertEqual(len(UserManager.objects.all().values('manager').distinct('manager')), 2)


class UserViewTest(TestCase):
    def setUp(self) -> None:
        self.manager1 = User.objects.create(username='Manager1', role='Manager', password='Manager1', email='a@a.ru')
        self.manager2 = User.objects.create(username='Manager2', role='Manager', password='Manager2', email='b@b.ru')
        self.user1    = User.objects.create(username='user1', password='user1', email='c@c.ru', phone_number='+99999999999')
        self.user2    = User.objects.create(username='user2', password='user2', email='d@d.ru')

    '''
    Получение данных о пользователе
    '''
    def test_retrieve_accept_auth(self):
        request = APIRequestFactory().get("user")
        view = UserViewSet.as_view({'get': 'retrieve'})
        force_authenticate(request, self.user1, "1234")
        response = view(request, pk=self.user1.pk)
        
        self.assertEqual(response.status_code, 200)
    
    '''
    Получение данных о пользователях
    При недостаточных прав
    '''
    def test_list_fail_auth(self):
        request = APIRequestFactory().get("user")
        view = UserViewSet.as_view({'get': 'list'})
        force_authenticate(request, self.user1, "1234")
        response = view(request)
        self.assertEqual(response.status_code, 403)

    '''
    Получение данных о пользователях
    При достаточных прав
    '''
    def test_list_accept_auth(self):
        request = APIRequestFactory().get("user")
        view = UserViewSet.as_view({'get': 'list'})
        force_authenticate(request, self.manager1, "1234")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    '''
    Изменение данных о пользователях
    При достаточных прав
    '''
    def test_update_accept(self):
        request = APIRequestFactory().patch('/user/', {'first_name': 'TEST', 'username': 'TEST'}, format='json')
        force_authenticate(request, self.user1)
        view = UserViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=self.user1.pk)
        
        self.user1.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.first_name, "TEST")
        self.assertNotEqual(self.user1.username, "TEST")

    '''
    Изменение данных о пользователях
    При недостаточных прав
    '''
    def test_update_fail(self):
        request = APIRequestFactory().patch('/user/', {'first_name': 'TEST', 'username': 'TEST'}, format='json')
        force_authenticate(request, self.user1)
        view = UserViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=self.user2.pk)
        
        self.user1.refresh_from_db()
        self.assertEqual(response.status_code, 404)


class TicketViewTest(TestCase):
    def setUp(self) -> None:
        self.admin    = User.objects.create(username='Admin', role=User.is_crm_admin, password='Admin', email='admin@admin.ru')
        self.manager1 = User.objects.create(username='Manager1', role=User.is_manager, password='Manager1', email='a@a.ru')
        self.manager2 = User.objects.create(username='Manager2', role=User.is_manager, password='Manager2', email='b@b.ru')
        self.user1    = User.objects.create(username='user1', password='user1', email='c@c.ru', phone_number='+99999999999')
        self.user2    = User.objects.create(username='user2', password='user2', email='d@d.ru')

    '''
    Проверка правильности создания токена (для авторизированного пользователя) и пост операций
    '''
    def test_create_support_ticket_auth_user(self):
        user = self.user1
        request = APIRequestFactory().post('/users/support/', 
                                        {'message': "TEST", 'topic_type': 1}, format='json')
        force_authenticate(request, user)
        view = SupportTicketViewSet.as_view({'post': 'create'})
        response = view(request)

        notify = Notify.objects.all().order_by('created').last()
        manager = UserManager.objects.get(user=user).manager

        self.assertEqual(response.status_code, 201)
        self.assertEqual(manager, notify.user)

    '''
    Проверка правильности создания токена (для не авторизированного пользователя) и пост операций
    '''
    def test_create_support_ticket_no_auth_user(self):    
        request = APIRequestFactory().post('/users/support/', {
                                            'name': "TEST",
                                            'phone_number': "+9999999999",
                                            'email': "test@test.ru",
                                            'message': "TEST", 
                                            'topic_type': 1
                                        }, format='json')

        view = SupportTicketViewSet.as_view({'post': 'create'})
        response = view(request)
        notify = Notify.objects.all().order_by('created').last()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.admin, notify.user)

