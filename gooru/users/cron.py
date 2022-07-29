from collections import defaultdict
from pysendpulse.pysendpulse import PySendPulse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from gooru import settings
from .utils import account_activation_token
from .models import Notify, User, Parsource, UserManager
from .utils import email_generator

def unread_parsource():
    unread_parsources = Parsource.objects.filter(is_view=False)
    email_messages = defaultdict(int) # {sender: amount_messanges}
    
    for parsource in unread_parsources:
        manager = UserManager.objects.get(user_id=parsource.user.id).manager
        email_messages[manager] += 1

    for manager, amount in email_messages.items():
        Notify.objects.create(
            user=manager,
            message=f"У вас есть не просмотренные парсеры ({amount})",
            url="",
        )


def verify_notify():
    inactive_users = User.objects_unfiltered.filter(is_active=False, verified=False)
    for user in inactive_users:        
        SPApiProxy = PySendPulse(settings.SENDPUlSE_REST_API_ID,
                            settings.SENDPUlSE_REST_API_SECRET, 'memcached')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        response = SPApiProxy.smtp_send_mail(email_generator("Account activation on compas-goo.ru", 
f"""You're receiving this email because you need to finish activation process on compas-goo.ru.

Please go to the following page to activate account:

{settings.HOSTNAME}/user/verify/{uid}/{token}/email""", user))

        print('create_user_send_message_verify', user.email, response)