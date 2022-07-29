from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from datetime import datetime, date, timezone, timedelta
from django.core.validators import RegexValidator
import os


def validate_nonzero(value):
    """
    Проверка значения на 0
    @param value: Проверяемое значение
    """
    if value == 0:
        raise ValidationError(
            _(f'Value {value} is not allowed'),
            params={'value': value},
        )


def validate_notnull(value):
    """
    Проверка значения на Null
    @param value: Проверяемое значение
    """
    if not value:
        raise ValidationError(
            _(f'Null values are not allowed!'),
            params={'value': value},
        )


def image_restriction(image):
    """
    Проверка размера загружаемого изображения
    @param image: загружаемое изображение
    """
    image_width, image_height = get_image_dimensions(image)
    if image_width >= 4096 or image_height >= 4096:
        raise ValidationError('Image width or height cant be more than 4096px')
    validate_image_file_extension(image)

def date_validator(chosen_date):
    """
    Проверка даты на то, что она не меньше текущей.
    @param chosen_date: Проверяемое значение
    """

    if chosen_date <= date.today():
        raise ValidationError(
            # _(f"'Chosen date: {chosen_date}' < 'Current date: {date.today()}'!"),
            _(f"'Chosen date: {chosen_date.strftime('%Y-%m-%d')}' <= 'Current date'!"),
            params={'chosen date': chosen_date.strftime('%Y-%m-%d')},
        )


def time_validator(chosen_time):
    """
    Проверка времени на то, что оно не меньше текущего.
    @param chosen_time: Проверяемое значение
    """

    """Компенсируем разницу во времени"""
    offset = timedelta(hours=3)

    chosen_time = datetime.strptime(chosen_time, '%H:%M').time()
    current_time = datetime.now() + offset

    if chosen_time < current_time.time():
        raise ValidationError(
            _(f"'Chosen time: {chosen_time}' < 'Current time: {current_time.time()}'!"),
            params={'chosen time': chosen_time},
        )
    


def validate_positive_nonzero(value):
    """
    Проверка, что value > 0
    @param value: Проверяемое значение
    """
    if float(value) <= 0:
        raise ValidationError(
            _(f'Value must be positive!'),
            params={'value': value},
        )


def validate_image_file_extension(value):
    """
    Валидатор, для расширения загружаемых файлов.
    Проверяет, что загружаемый файл - киртинка, в одном из разрешенных форматов (valid_extensions)
    @param value:
    """
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Phone number must be entered in the format: '+999999999'. "
                                     "Up to 15 digits allowed.")