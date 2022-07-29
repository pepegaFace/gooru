import json
import os
from django.core.management.base import BaseCommand

from users.models import Tariff

from random import randint, choice

PARSOURCE_AMOUNT = 10
PARSER_AMOUNT = 7


def generate_tariff(params):
    tariff_instance = Tariff.objects.filter(id=params['id'])

    if tariff_instance:
        print(f"tariff #{params['id']} already exists!")
        pass
    else:
        print(f"Generating {params['id']}...")
        tariff = Tariff.objects.create(
            name=params['name'],
            cost=params['cost'],
            description="Empty"
        )

        tariff.save()

class Command(BaseCommand):
    help = 'Generate parsers in database'

    def handle(self, *args, **kwargs):
        filepath = os.path.abspath(os.path.dirname(__file__))

        json_data = open(f'{filepath}/subs.json')
        params_list = json.load(json_data)

        for element in params_list:
            generate_tariff(element)
