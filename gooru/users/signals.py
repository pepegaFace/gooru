from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from rest_framework.exceptions import APIException
from collections import Counter
from gooru import settings
from pysendpulse.pysendpulse import PySendPulse

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from .utils import account_activation_token, email_generator

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str



def find_free_manager():
    '''Возвращает самого свободного менеджера'''
    
    # получаем всех менеджеров
    managers:list[tuple[int]] = User.objects.filter(role=User.is_manager).values_list('id')
    # получаем занятость менеджеров, отсеиваем не активных пользователей
    query_managers:list[tuple[int]] = UserManager.objects.filter(user__is_active=True).values_list('manager')    
    # получаем свободных менеджеров
    free_managers:list[tuple[int]] = list(set(managers) - set(query_managers))
    # проверяем наличие менеджеров в бд
    if not free_managers and not query_managers:
        raise APIException("Not found Managers!!!")
    elif free_managers:
        # берем id первого попавшегося
        manager_id:int = free_managers[0][0]
    else:
        # делаем словарь, где ключ – id, значение – количество обслуживаемых клиентов
        manager_amount:dict[int, int] = Counter(map(lambda x: x[0],  query_managers))
        manager_id:int = min(manager_amount, key=manager_amount.get)
    
    return User.objects.get(id=manager_id)


@receiver(post_save, sender=Parser)
def create_notify_parser(sender, instance:Parser, created:bool, **kwargs):
    '''
    Создаем уведомление при изменении парсера
    '''
    if created:
        name = instance.title[:20] + '...' if len(instance.title) > 20 else ''
        message=f"Парсер {name} добавлен!"
    else:
        name = instance.title[:20] + '...' if len(instance.title) > 20 else ''
        message=f"Парсер {name} изменен!"

    manager = UserManager.objects.get(user_id=instance.parsource.user.id).manager
    Notify.objects.create(
        user=instance.parsource.user,
        message=message,
        url=instance.get_absolute_url()
    )
    Notify.objects.create(
        user=manager,
        message=message,
        url=instance.get_absolute_url()
    )

@receiver(post_save, sender=Parsource)
def create_notify_parsource(sender, instance:Parsource, created:bool, **kwargs):
    '''
    Создаем уведомление при изменении источника парсинга
    '''
    ROLE_CHOICES_PARS = dict((
        ('Process', "Открыто"),
        ('Ready', "Закрыто"),
        ('Pending', "Отложен")
    ))

    if not created:
        name = instance.name[:20] + ('...' if len(instance.name) > 20 else '')
        message=f"Источник {name} изменен! Текущий статус: {ROLE_CHOICES_PARS[instance.condition]}"
    else:
        name = instance.name[:20] + ('...' if len(instance.name) > 20 else '')
        message=f"Источник {name} создан!"

    if instance.user:
        Notify.objects.create(
            user=instance.user,
            message=message,
            url=instance.get_absolute_url()
        )


@receiver(post_save, sender=SupportTicket)
def create_notify_ticket(sender, instance:SupportTicket, created:bool, **kwargs):
    '''
    Создаем уведомление при изменении тикета для пользователя
    и создаем уведомление при создании тикета для менеджера
    '''
    ROLE_CHOICES_PARS = dict((
        (1, "В процессе"),
        (2, "Закрыт"),
        (3, "Отложен"),
    ))

    name = instance.name[:20] + '...' if len(instance.name) > 20 else ''
    user = instance.user
    if user is not None:
        manager = UserManager.objects.get(user_id=user.id).manager
    else:
        manager = User.objects.filter(role=User.is_crm_admin).first()

    if not created:
        user_message = f"Запрос {name} изменен! Текущий статус: {ROLE_CHOICES_PARS[instance.status]}"
        manager_message = f"Запрос {name} изменен! Текущий статус: {ROLE_CHOICES_PARS[instance.status]}"
    else:
        user_message = f"Создан тикет {name}. Тип обращения: {instance.topic_type}"
        manager_message = f"Создан тикет {name}. Тип обращения: {instance.topic_type}"

    Notify.objects.create(
        user=manager,
        message=manager_message,
        url=instance.get_absolute_url()
    )
    if user is not None:
        Notify.objects.create(
            user=user,
            message=user_message,
            url=instance.get_absolute_url()
        )


# @receiver(post_save, sender=Notify)
# def remove_notyfy(sender, instance:Notify, created:bool, **kwargs):
#     '''
#     Удаляем уведомление после прочтения
#     '''
#     if not created and instance.checked:
#         instance.delete()


@receiver(post_save, sender=User)
def create_referense_user_manager(sender, instance:User, created:bool, **kwargs):
    '''
    Назначаем новому пользователю менеджера
    Менеджером менеджера является администратор
    '''
    if created and instance.role == User.is_default:
        manager = find_free_manager()
    elif created and instance.role == User.is_manager:
        manager = User.objects.filter(role=User.is_crm_admin).first()
    else:
        return

    UserManager.objects.create(user=instance, manager=manager)
    Notify.objects.create(
        user=manager,
        message=f"Добавлен новый пользователь! email пользователя: {instance.email}",
        url=instance.get_absolute_url()
    )


@receiver(post_save, sender=User)
def create_user_send_message_verify(sender, instance: User, created: bool, **kwargs):
    if not created:
        return 

    user = instance
    user.is_active = False
    user.save()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    SPApiProxy = PySendPulse(settings.SENDPUlSE_REST_API_ID,
                            settings.SENDPUlSE_REST_API_SECRET, 'memcached')
    
    response = SPApiProxy.smtp_send_mail(email_generator("Активация аккаунта compas-goo.ru",
f"""You're receiving this email because you need to finish activation process on compas-goo.ru.

Please go to the following page to activate account:

{settings.HOSTNAME}/user/verify/{uid}/{token}/email""", user))

    print('create_user_send_message_verify', response)

@receiver(post_save, sender=Notify)
def create_notify(sender, instance:Notify, created:bool, **kwargs):
    SPApiProxy = PySendPulse(settings.SENDPUlSE_REST_API_ID,
                            settings.SENDPUlSE_REST_API_SECRET, 'memcached')
    response = SPApiProxy.smtp_send_mail(email_generator("Новое событие в Gooru", 
                                            instance.message + "\nПерейти к событию: " + "compas-goo.ru/"+instance.url, 
                                            instance.user))

    print('create_notify', instance.user.email, response)