from django.contrib import admin
from .models import *


@admin.register(User)
class AdmUser(admin.ModelAdmin):
    list_display = ('id', 'email', 'username')
    filter_horizontal = ('groups', 'user_permissions')

    def get_queryset(self, request):
        return self.model.objects_unfiltered.all()


@admin.register(Favorite)
class AdmFavorites(admin.ModelAdmin):
    list_display = ('id', 'user', 'parser')


@admin.register(SupportTicket)
class AdmSupport(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'topic_type', 'message')


@admin.register(Parsource)
class AdmParsource(admin.ModelAdmin):
    list_display = ('id', 'data_source', 'date', 'condition', 'find', 'lost_time')


@admin.register(Parser)
class AdmParser(admin.ModelAdmin):
    list_display = ('id', 'url', 'title', 'article')


@admin.register(Notify)
class AdmNotify(admin.ModelAdmin):
    list_display = ('id', 'created', 'checked', 'date_checked', 'message', 'url')


@admin.register(UserManager)
class AdmUserManager(admin.ModelAdmin):
    list_display = ('id', 'user', 'manager')


@admin.register(Brief)
class AdmBrief(admin.ModelAdmin):
    list_display = ('id', 'client_status', 
                    'client_status_self_option', 
                    'fields_of_activity', 
                    'fields_of_activity_self_option', 
                    'site_types', 'additional_options', 
                    'number_of_position_min', 
                    'number_of_position_max', 'source_amount', 
                    'name')

@admin.register(TokenUid)
class AdmUserManager(admin.ModelAdmin):
    list_display = ('id', 'token', 'uid')

@admin.register(Tariff)
class AdmUserManager(admin.ModelAdmin):
    list_display = ('id', 'name', 'cost')

@admin.register(UserTariff)
class AdmUserManager(admin.ModelAdmin):
    list_display = ('id', 'user', 'tariff', 'status', 'is_active', 'payment_id', 'finish_date')

@admin.register(Comment)
class AdmComment(admin.ModelAdmin):
    list_display = ('id', 'parser', 'created', 'updated', 'comment')
    list_filter = ('created', 'updated')
