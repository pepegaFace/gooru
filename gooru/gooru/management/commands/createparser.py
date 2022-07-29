import os
from django.core.management.base import BaseCommand

from users.models import Parser, Parsource, User

from random import randint, choice

PARSOURCE_AMOUNT = 10
PARSER_AMOUNT = 7

class Command(BaseCommand):
    help = 'Generate parsers in database'

    def handle(self, *args, **kwargs):
        median = 20
        disp = 5
        seporators = [' ', '\n', ', ', '\t']
        username = os.environ.get("USER_NAME")
        user = User.objects.get(username=username)

        for parsource_id in range(1, PARSOURCE_AMOUNT+1):
            parsource_instance = Parsource.objects.filter(id=parsource_id)
            if parsource_instance:
                print(f"{parsource_id=} already exists!")
                continue
            else:
                print(f"generation {parsource_id=}...")

            parsource = Parsource(user=user,
                        name=f"parsource {parsource_id}",
                        data_source=f"http://parsource.com/{parsource_id}",
                        description=''.join([f"I need nanomachine, son " + choice(seporators)
                                        for _ in range(randint(median-disp, median+disp))]),
                        parse_fields=f"Field name\n"*randint(median-disp, median+disp),
                        url_detail=f"http://parsource.com/detail/{parsource_id}"
            )
            parsource.save()
            for parser_id in range(1, PARSER_AMOUNT+1):
                Parser(parsource=parsource,
                        url=f"http://parser.com/{parsource_id}/{parser_id}",
                        title=f"parser-title-{parsource_id}-{parser_id}",
                        article=''.join([f"Is is new nanomachine, son! " + choice(seporators)
                                        for _ in range(randint(median-disp, median+disp))])
                ).save()