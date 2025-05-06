from datetime import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from global_services.googleMap import forecastApi


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(forecastApi.fetch_weather_and_notify, 'interval', minutes=60)
    scheduler.start()
