import datetime
import os

import django
import requests

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PalmaCrm.settings"
)

django.setup()

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from src.core.models import BotMessage

User = get_user_model()


def send_notifications():
    notifications = BotMessage.objects.filter(is_sent=False).order_by('created_at')
    for notification in notifications:
        payload = {
            'chat_id': settings.CHAT_ID,
            'text': notification.text,
            'parse_mode': 'Html'
        }
        requests.post(
            url=f'{settings.TG_API_URL}{settings.BOT_TOKEN}/sendMessage', json=payload
        )
    notifications.update(is_sent=True)


def main():
    send_notifications()


main()
