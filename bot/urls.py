from django.urls import path, include

from .views import webhook_handler

urlpatterns = [
    # path('webhook/', webhook_handler, name='bot_webhook'),
]
