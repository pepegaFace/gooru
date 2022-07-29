
from django.http import HttpResponse, HttpResponseRedirect
from requests import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from yookassa import Configuration, Payment

import users.models
from gooru.permissions import IsSelf

import json
from django.http import HttpResponse
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory
from yookassa.domain.common import SecurityHelper
from users.models import Tariff, User, UserTariff, AbstractUser

Configuration.account_id = '922094'
Configuration.secret_key = 'live_SJAEZfFBYw4E2DDd2bIAwZoZOdl6eZ4d7LUJdCZYTRs'


class YookassaPayment(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, type_id):

        #user = getattr(request, 'user', None)
        user = User.objects.get(id=1)

        print (user)

        tariff = Tariff.objects.get(id=type_id)
        payment = Payment.create({
            "amount": {
                "value": tariff.cost,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://localhost:8003"
                },
            "receipt": {
                "customer": {
                    "full_name": user.first_name,
                    "email": user.email,
                    "phone": user.phone_number,

                },
                "items": [
                    {
                        "description": "Подписка compas-goo.ru",
                        "quantity": "1.00",
                        "amount": {
                            "value": tariff.cost,
                            "currency": "RUB"
                        },
                        "vat_code": "1",
                    },
                         ]
                        },
            "capture": True,
            "description": tariff.name
        })

        UserTariff.objects.create(tariff=tariff, user=user, payment_id=payment.id)
        return HttpResponseRedirect(payment.confirmation.confirmation_url)


class YandexNotifi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        print()
        print()
        print(data)
        print()
        print()
        subscription = UserTariff.objects.get(payment_id=data['object']['id'])
        subscription.status = data['event']
        subscription.is_active = subscription.status == 'payment.succeeded'
        subscription.save()

        # basic = Group.objects.get(name='basic')
        # subscription.user.groups.add(basic)
        # subscription.save()

        return Response(status=200)


    def my_webhook_handler(request):

        # Извлечение JSON объекта из тела запроса
        event_json = json.loads(request.body)
        try:
            # Создание объекта класса уведомлений в зависимости от события
            notification_object = WebhookNotificationFactory().create(event_json)
            response_object = notification_object.object
            if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                some_data = {
                    'paymentId': response_object.id,
                    'paymentStatus': response_object.status,
                }

            elif notification_object.event == WebhookNotificationEventType.PAYMENT_WAITING_FOR_CAPTURE:
                some_data = {
                    'paymentId': response_object.id,
                    'paymentStatus': response_object.status,
                }

            elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
                some_data = {
                    'paymentId': response_object.id,
                    'paymentStatus': response_object.status,
                }

            elif notification_object.event == WebhookNotificationEventType.REFUND_SUCCEEDED:
                some_data = {
                    'refundId': response_object.id,
                    'refundStatus': response_object.status,
                    'paymentId': response_object.payment_id,
                }

            elif notification_object.event == WebhookNotificationEventType.DEAL_CLOSED:
                some_data = {
                    'dealId': response_object.id,
                    'dealStatus': response_object.status,
                }

            elif notification_object.event == WebhookNotificationEventType.PAYOUT_SUCCEEDED:
                some_data = {
                    'payoutId': response_object.id,
                    'payoutStatus': response_object.status,
                    'dealId': response_object.deal.id,
                }

            elif notification_object.event == WebhookNotificationEventType.PAYOUT_CANCELED:
                some_data = {
                    'payoutId': response_object.id,
                    'payoutStatus': response_object.status,
                    'dealId': response_object.deal.id,
                }

            else:
                # Обработка ошибок
                return HttpResponse(status=400)  # Сообщаем кассе об ошибке

            # Специфичная логика
            # ...
            Configuration.configure('922094', 'live_SJAEZfFBYw4E2DDd2bIAwZoZOdl6eZ4d7LUJdCZYTRs')
            # Получим актуальную информацию о платеже
            payment_info = Payment.find_one(some_data['paymentId'])
            if payment_info:
                payment_status = payment_info.status

            else:

                return HttpResponse(status=400)  # Сообщаем кассе об ошибке

        except Exception:
            # Обработка ошибок
            return HttpResponse(status=400)  # Сообщаем кассе об ошибке

        return HttpResponse(status=200)  # Сообщаем кассе, что все хорошо



# import uuid
#
#
#
#
# payment = Payment.create({
#     "amount": {
#         "value": "100.00",
#         "currency": "RUB"
#     },
#     "confirmation": {
#         "type": "redirect",
#         "return_url": "https://www.merchant-website.com/return_url"
#     },
#     "capture": True,
#     "description": "Заказ №1"
# }, uuid.uuid4())