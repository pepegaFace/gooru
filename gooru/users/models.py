from pyexpat import model
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractUser, UnicodeUsernameValidator)
from django.utils.translation import gettext_lazy as _
from gooru.managers import SoftDeleteManager, SoftDeleteManagerDeleted
from gooru.validators import *
from django.dispatch import receiver
from django.utils import timezone, dateformat
import os.path
from django.core.files.storage import FileSystemStorage
from gooru.models import SoftDeleteAbstract, SoftDeleteUserAbstract
from rest_framework.exceptions import ValidationError as drf_ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from multiselectfield import MultiSelectField


username_validator = UnicodeUsernameValidator()


def avatar_directory_path(instance, filename):
    """
    Функция, генерирующая путь для загружаемой аватарки пользователя
    @param instance:
    @param filename: загружаемая аватарка
    @return:
    """
    return u'avatars/{0}'.format(filename)

def screenshot_directory_path(instance, filename):
    """
    Функция, генерирующая путь для загружаемого скрина пользователя
    @param instance:
    @param filename: загружаемый скриншот
    @return: строка
    """
    return u'screenshots/{0}'.format(filename)


class User(SoftDeleteUserAbstract):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        default=None,
        null=False,
        unique=True,
        help_text=_('Required'),
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required'),
        validators=[username_validator],
        default=None,
        null=False,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    password = models.CharField(
        _('password'),
        max_length=128,
        default=None,
        null=False,
    )

    # is_not_auth = 'Anonymous'
    is_manager = 'Manager'
    is_crm_admin = 'AdminCRM'
    is_default = 'DefaultUser'

    ROLE_CHOICES = (
        # (is_not_auth, 'Не авторинный')
        (is_default, "Пользователь"),
        (is_manager, "Менеджер"),
        (is_crm_admin, "Администратор"),
    )
    role = models.CharField(choices=ROLE_CHOICES, default=is_default, max_length=15)

    phone_number = models.CharField(_('Phone number'), validators=[phone_regex], max_length=17, help_text=_('Required'),
                                    default='+77777777777', blank=False, null=False)

    avatar = models.ImageField(_('Avatar'), upload_to=avatar_directory_path,
                               validators=[image_restriction],
                               blank=True, null=True, default='avatar.png'
                               )
    verified = models.BooleanField(_('Verified'), default=False)

    def get_absolute_url(self):
        return ""

    def __str__(self):
        return f'User {self.username}'


class UserManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True, related_name='user')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='manager')

    def __str__(self) -> str:
        return f"{self.user} – {self.manager}"

    class Meta:
        unique_together = ('user', 'manager',)


class Parsource(models.Model):
    objects = SoftDeleteManager()  # Expose non-deleted objects only
    objects_unfiltered = models.Manager()  # Expose ALL objects (used primarily in Admin panel)
    objects_deleted = SoftDeleteManagerDeleted() # Expose all DELETED objects (used primarily in for testing)


    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(_('Parser name'), max_length=30, help_text=_('Required'),       
                                    blank=False, null=False, default='my new parser')

    data_source = models.TextField(_('Data url'), max_length=1000, help_text=_('Required'),
                                    blank=False, null=False, default='yandex.ru')

    date = models.DateTimeField(null=True, blank=True)

    in_the_process = "Process"
    ready = "Ready"
    request_pending = "Pending"

    ROLE_CHOICES_PARS = (
        (in_the_process, "Открыто"),
        (ready, "Закрыто"),
        (request_pending, "Отложен"),
    )

    condition = models.CharField(choices=ROLE_CHOICES_PARS, default=in_the_process, max_length=18)

    find = models.CharField(max_length=17, help_text=_('Required'),
                                    default='Не найден')

    lost_time = models.TimeField(auto_now_add=True)

    description  = models.TextField(_('Основные требования'), null=False, blank=False)
    parse_fields = models.TextField(_('Необходимые поля'), null=False, blank=False)
    url_detail   = models.TextField(_('Url на страницу с деталями'), blank=True, null=True)
    screenshot = models.ImageField(_('Скриншот'), upload_to=screenshot_directory_path,
                                validators=[image_restriction],
                                blank=True, null=True)
    is_view = models.BooleanField(_('Просмотрено'), blank=True, default=False)
    inactive = models.BooleanField(_('Удалено'), blank=True, default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted_on = timezone.now()
        self.inactive = True
        self.save()

    def get_absolute_url(self):
        return f'parsource/{self.id}'

    def __str__(self) -> str:
        return f"Parsource {self.name}"


class Parser(models.Model):
    parsource = models.ForeignKey(Parsource, on_delete=models.SET_NULL, blank=True, null=True)
    url = models.URLField(
        max_length=450,
        verbose_name=_('URL ссылка'),
        unique=True
    )
    title = models.TextField(
        verbose_name=_('Заголовок'),
        max_length=450,
    )
    article = models.TextField(
        verbose_name=_('Текст статьи')
    )

    def get_absolute_url(self):
        return f"parser/{self.id}"

    def __str__(self) -> str:
        return f"Parser {self.title}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text=_('Required'))
    parser = models.ForeignKey(Parser, on_delete=models.CASCADE, help_text=_('Required'))

    def __str__(self):
        return f'Избранное пользователя: {self.user}'

    class Meta:
        unique_together = ('user', 'parser',)


class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text=_('Required'), 
                                blank=True, null=True)
                                
    name = models.CharField(_('Name'), help_text=_('Required'), max_length=150)

    phone_number = models.CharField(_('Phone number'), validators=[phone_regex], 
                                        max_length=17, help_text=_('Required'))

    email = models.EmailField(verbose_name='Email address', max_length=255, 
                                null=False, help_text=_('Required'))

    TOPIC_TYPES = (
        (1, "Вопрос по моим парсерам"),
        (2, "Вопрос к менеджеру"),
        (3, "Вопрос по оплате"),
        (4, "Вопрос по новому заказу"),
        (5, "Обращение в службу безопасности"),
        (6, "Предложение о сотрудничестве"),
        (7, "Сообщить об ошибке на сайте"),
        (8, "Другое")
    )

    parser = models.ForeignKey(Parser, on_delete=models.SET_NULL, null=True, blank=True)
    topic_type = models.PositiveSmallIntegerField(choices=TOPIC_TYPES, default=1)

    message = models.CharField(_('Message'), help_text=_('Required'), default=None, max_length=1500)
    
    ROLE_CHOICES_PARS = (
        (1, "В процессе"),
        (2, "Закрыт"),
        (3, "Отложен"),
    )

    status = models.PositiveSmallIntegerField(choices=ROLE_CHOICES_PARS, default=1)

    def get_absolute_url(self):
        return f'users/support/{self.id}'

    def __str__(self) -> str:
        return f"{self.user} – {self.name}"


class Notify(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text=_('Required'),)
    created = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(verbose_name="Просмотрено", default=False)
    date_checked = models.DateTimeField(verbose_name="Время просмотра", null=True, blank=True)
    message = models.CharField("Текст уведомления", max_length=200, help_text=_('Required'))
    url = models.URLField("Ссылка на событие", max_length=100, help_text=_('Required'), 
                            null=False, blank=False)


class Brief(models.Model):
    CLIENT_STATUS = (
        (1, "Физическое лицо"),
        (2, "Самозанятый"),
        (3, "Индивидуальный предприниматель"),
        (4, "Общество с ограниченной ответственностью"),
        (5, "Свой вариант")
    )

    FIELDS_OF_ACTIVITY = (
        (1, "Информационные системы"),
        (2, "Маркетинг, реклама"),
        (3, "Торговля"),
        (4, "Обучение, преподавание"),
        (5, "Свой вариант")
    )

    SITE_TYPES = (
        (1, "Интернет-магазин"),
        (2, "Маркетплейс"),
        (3, "Доска объявлений"),
        (4, "Новостной сайт"),
        (5, "Социальная сеть"),
        (5, "Свой вариант")
    )

    ADDITIONAL_OPTIONS = (
        (1, "Парсинг с авторизацией"),
        (2, "Разбивка всех характеристик в отдельный столбец"),
        (3, "Дополнительные столбцы данных"),
        (4, "Настроить файл экспорта в вашу CMS"),
        (5, "Вариативные товары"),
        (6, "Скачивание до 5 изображений одного товара")
    )

    SOURCE_AMOUNT = (
        (1, "От 1 до 3 сайтов, до 5 страниц"),
        (2, "От 1 до 10 сайтов, до 15 страниц"),
        (3, "От 1 до 10 сайтов, до 15 страниц, с выгрузкой в соцсети"),
        (4, "Свыше 10 сайтов, свыше 15 страниц, особые условия"),
    )
    
    client_status = models.SmallIntegerField(choices=CLIENT_STATUS, null=False, blank=False)
    client_status_self_option = models.TextField(null=True, blank=True, default='')

    fields_of_activity = MultiSelectField(choices=FIELDS_OF_ACTIVITY)
    fields_of_activity_self_option = models.TextField(null=True, blank=True, default='')
    
    site_types = MultiSelectField(choices=SITE_TYPES)
    site_types_self_option = models.TextField(null=True, blank=True, default='')

    additional_options = MultiSelectField(choices=ADDITIONAL_OPTIONS)

    number_of_position_min = models.IntegerField(validators=[
                    MaxValueValidator(100000),
                    MinValueValidator(100)
                ],
                null=False,
                blank=False
    )

    number_of_position_max = models.IntegerField(validators=[
                    MaxValueValidator(100000),
                    MinValueValidator(100)
                ],
                null=False,
                blank=False
    )

    source_amount = models.SmallIntegerField(choices=SOURCE_AMOUNT, null=False, blank=False)

    name = models.CharField(max_length=50, null=False, blank=False)


class TokenUid(models.Model):
    token = models.CharField('Token', max_length=350)
    uid = models.CharField('Uid', max_length=10)


class Tariff(models.Model):
    cost = models.PositiveIntegerField(_('Cost'), help_text=_('Required'), null=False, blank=False)
    name = models.CharField(_('Name'), max_length=200, help_text=_('Required'), null=False, blank=False)
    description = models.CharField(_('Discription'), max_length=300, help_text=_('Required'), null=False, blank=False)
    
    def __str__(self) -> str:
        return f"{self.name}"

class UserTariff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usertariff')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, related_name='tariff')
    created = models.DateField(_('Created'), auto_now_add=True)
    finish_date = models.DateField(_('Finish date'), default=datetime.datetime.now() + datetime.timedelta(days=30))
    STATUS_CHOICES = (
        ('payment.succeeded', 'Succeeded'),
        ('payment.waiting_for_capture', 'Waiting for payment'),
        ('payment.canceled', 'Canceled'),
        ('refund.succeeded', 'Refund succeeded'),
    )
    status = models.CharField(_("Status"), default='payment.waiting_for_capture', max_length=50, null=False, blank=False)
    is_active = models.BooleanField(_('Active'), default=False)
    payment_id = models.CharField(_("Payment"), max_length=150, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.tariff} – {self.tariff}"

class Comment(models.Model):
    parser = models.ForeignKey(Parser, related_name='comments', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    comment = models.CharField(_("Comment"), max_length=300, null=False, blank=True)
    def __str__(self):
        return 'Создан коммент {} on {}'.format(self.parser, self.created)