import requests
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
SERVICE_ACCOUNT_FILE = 'global_services/firebase/'


def send_fcm_notification(tokens, title, body):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    credentials.refresh(Request())
    access_token = credentials.token

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; UTF-8',
    }

    # إعداد الرسالة التي سيتم إرسالها
    message = {
        'message': {
            'notification': {
                'title': title,
                'body': body
            },
            'tokens': tokens,  # إرسال إلى مجموعة من الـ tokens
            'android': {
                'priority': 'high'
            },
            'apns': {
                'headers': {
                    'apns-priority': '10'
                }
            }
        }
    }

    # إرسال الإشعار إلى Firebase Cloud Messaging (FCM)
    response = requests.post(
        'https://fcm.googleapis.com/v1/projects/nugheeth/messages:send',
        headers=headers,
        data=json.dumps(message)
    )

    return response.json()


