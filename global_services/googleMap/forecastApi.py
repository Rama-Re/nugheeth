import requests
from global_services.firebase.notifications import send_fcm_notification
from users.models import User


def fetch_weather_and_notify():
    # إحداثيات المدينة المنورة
    LAT = 24.470901
    LON = 39.612236

    API_KEY = 'AIzaSyDkPh8vuUbdAuQCSf971rWxQ_uTxvi2pqc'

    url = "https://weather.googleapis.com/v1/currentConditions:lookup"

    params = {
        "key": API_KEY,
        "location.latitude": LAT,
        "location.longitude": LON
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        weather_type = data["weatherCondition"]["type"]
        temperature = data["temperature"]["degrees"]

        title = "Weather in Medina"
        body = f"Current weather: {weather_type}, Temperature: {temperature}°C"

        recipients = User.objects.filter(account_type='pilgrim').exclude(fcm_token=None)
        tokens = [user.fcm_token for user in recipients if user.fcm_token]
        send_fcm_notification(
            tokens=tokens,
            title=title,
            body=body
        )
        print(title, body)

    except Exception as e:
        print("خطأ أثناء جلب الطقس أو إرسال الإشعار:", e)
