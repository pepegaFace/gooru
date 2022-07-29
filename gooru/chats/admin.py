from django.contrib import admin
from .models import Message


@admin.register(Message)
class AdmMessage(admin.ModelAdmin):
    list_display = ('id', 'sender', 'ticket', 'text', 'created_at')
