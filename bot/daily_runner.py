import time
import datetime

from django.conf import settings
from .models import Entity, Observation

class DailyRunner:
    def run(func, args):
        while True:
            current_datetime = datetime.datetime.now()
            target_time = current_datetime.replace(hour=settings.DAILY_TIME[0], minute=settings.DAILY_TIME[1], second=0)

            if current_datetime >= target_time:
                func(*args)

                next_day = current_datetime + datetime.timedelta(days=1)
                next_target_time = next_day.replace(hour=settings.DAILY_TIME[0], minute=settings.DAILY_TIME[1], second=0)
                time_to_sleep = (next_target_time - current_datetime).total_seconds()
                time.sleep(time_to_sleep)
            else:
                time_to_sleep = (target_time - current_datetime).total_seconds()
                time.sleep(time_to_sleep)
