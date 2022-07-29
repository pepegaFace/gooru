"""gooru URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from email.mime import base
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import *
from users.yasg_urls import urlpatterns as yasg_urls_users
import users.views as users_views
import chats.views as chats_views
from django.conf import settings
from django.conf.urls.static import static
from gooru.payment import YookassaPayment, YandexNotifi
router = DefaultRouter()

"""USERS ViewSets"""
router.register(r'usersfavorite', users_views.FavoritesViewSet, basename='Favorites')
router.register(r'users/support', users_views.SupportTicketViewSet, basename='Support')
router.register(r'user/verify/(?P<uid>\w+)/(?P<token>[\w\d$-./]+)', users_views.UserVerifyViewSet, basename='user verify')
router.register(r'user', users_views.UserViewSet, basename='User')
router.register(r'user/upload', users_views.UploadAvatarViewSet, basename='User')

router.register(r'parser/download/(?P<type>\w+)', users_views.DownloadParserViewSet, basename='Parser Download')
router.register(r'parser', users_views.ParserViewSet, basename='Parser')

router.register(r'parsource', users_views.ParsourceViewSet, basename='Parsource')
router.register(r'parsource/uploadscreen', users_views.UploadScreenShotViewSet, basename='Parsource Screen Shot')

router.register(r'notify', users_views.NotifyViewSet, basename='Notify')

router.register(r'brief', users_views.BriefViewSet, basename='Brief')
router.register(r'tariff', users_views.TariffViewSet, basename='Tariff')
router.register(r'usertariff', users_views.UserTariffViewSet, basename='User Tariff')

router.register(r'usermanager', users_views.UserManagerViewSet, basename='User Manager')

router.register(r'multiaction', users_views.MultiActionViewSet, basename='Multi Update Or Delete')

"""CHATS ViewSets"""
router.register(r'supportchat', chats_views.MessageViewSet, basename='Support Chat')

"""Comments"""
router.register(r'comment', users_views.UserComment, basename='User Comment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('/', include('djoser.urls.jwt')),
    # Gooru.payment
    re_path(r'^api/pay/(?P<type_id>\d+)/', YookassaPayment.as_view(), name="pay_views"),
    re_path(r'^api/notifi/', YandexNotifi.as_view(), name="pay_notifi"),
    # USERS routes
]


urlpatterns += yasg_urls_users

urlpatterns += router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
