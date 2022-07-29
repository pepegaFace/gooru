from django.db.models import QuerySet, Count
from .models import Message
from users.models import User, UserManager, Notify
from collections import defaultdict
from datetime import datetime, timezone


def message_notify():
    unread_messages: QuerySet[Message] = Message.objects.filter(status=False)
    email_messages = defaultdict(int) # {sender: amount_messanges}
    for message in unread_messages:
        if message.sender == message.ticket.user:
            sender = UserManager.objects.get(user_id=message.sender.id).manager
        else:
            sender = message.ticket.user

        email_messages[sender] += 1
    
    for user, amount in email_messages.items():
        Notify.objects.create(
            user=user,
            message=f"У вас есть не прочитанные сообщения ({amount})",
            url="",
        )


def manager_no_read_message():
    """
    Отправка уведомления администратору о непрочитанном сообщении менеджера
    """
    unread_messages:QuerySet[Message] = Message.objects.filter(status=False, sender__role=User.is_default)
    email_messages = defaultdict(int) # {sender: amount_messanges}
    current_date = datetime.now(timezone.utc)
    for message in unread_messages:
        if (current_date - message.created_at).days > 1:
            manager = UserManager.objects.get(user_id=message.sender.id).manager
            email_messages[manager] += 1

    admin = User.objects.filter(role=User.is_crm_admin).first()
    for manager, amount in email_messages.items():
        Notify.objects.create(
            user=admin,
            message=f"У менеджера {manager.email} есть непрочитанные сообщения ({amount})",
            url="",
        )