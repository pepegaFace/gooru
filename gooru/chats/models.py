from django.db import models
from users.models import User, SupportTicket


class Message(models.Model):
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    ticket = models.ForeignKey(SupportTicket, related_name='ticket', on_delete=models.CASCADE)
    status = models.BooleanField('Status', default=False)