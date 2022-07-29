from venv import create
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *
from users.models import Notify, UserManager, User
from gooru import settings


@receiver(post_save, sender=Message)
def new_message(sender, instance:Message, created:bool, **kwargs):
    if created and instance.sender.role == User.is_default:
        manager = UserManager.objects.get(user_id=instance.sender.id).manager
        Notify.objects.create(
            user=manager,
            message="Вам пришло новое сообщение",
            url=instance.ticket.get_absolute_url()
        )
    elif created and instance.ticket.user:
        Notify.objects.create(
            user=instance.ticket.user,
            message="Вам пришло новое сообщение",
            url=instance.ticket.get_absolute_url()
        )