from django.core.management.base import BaseCommand
from users.models import User
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from rest_framework.authtoken.models import Token


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(f'{Path(PROJECT_ROOT).parent}/.env.dev')


def check_users():
    """
    Проверка на наличие пользователей в базе.
    Если пользователи имеются - возвращаем 1, иначе 0
    @return: 0, 1
    """
    users = User.objects.all()
    try:
        print(users[0])
        return 1
    except Exception as error:
        print('An exception occurred: {}'.format(error))
        return 0


def generate_superuser():
    """
    Функция, создающая админа по параметрам
    """
    apartment_instance = User.objects.filter(username=os.environ.get("USER_NAME"))

    if apartment_instance:
        print(f"superuser already exists!")
        pass
    else:
        print('Generating admin user...')
        superuser = User.objects.create_superuser(
            email=os.environ.get("USER_EMAIL"),
            username=os.environ.get("USER_NAME"),
            password=os.environ.get("USER_PASSWORD"),
            role='AdminCRM'
        )

        superuser.save()
        superuser.is_active=True
        superuser.verified=True
        superuser.save()
        Token.objects.create(user=superuser)


def generate_user(params):
    """
    Функция, генерирующая пользователей на основе набора параметров и записывающая их в базу данных.
    @param params: набор параметров
    """

    user_instance = User.objects.filter(username=params['username'])

    if user_instance:
        print(f"{params['username']} already exists!")
        pass
    else:
        print(f"Generating {params['username']}...")
        user = User.objects.create_user(
            email=params['email'],
            username=params['username'],
            password=params['password'],
            role=params['role']
        )

        user.save()
        user.is_active=True
        user.verified=True
        user.save() 
        Token.objects.create(user=user)


class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_superuser()

        filepath = os.path.abspath(os.path.dirname(__file__))

        json_data = open(f'{filepath}/user_data.json')
        params_list = json.load(json_data)

        for element in params_list:
            generate_user(element)
