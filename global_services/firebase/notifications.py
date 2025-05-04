import requests
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
SERVICE_ACCOUNT_FILE = 'global_services/firebase/nugheeth-firebase-adminsdk-fbsvc-bdba8e7a69.json'


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

    # سجل الردود لكل توكن
    results = []

    for token in tokens:
        message = {
            'message': {
                'token': token,
                'notification': {
                    'title': title,
                    'body': body
                },
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

        response = requests.post(
            'https://fcm.googleapis.com/v1/projects/nugheeth/messages:send',
            headers=headers,
            data=json.dumps(message)
        )

        results.append({
            'token': token,
            'status_code': response.status_code,
            'response': response.json() if response.status_code != 204 else "No Content"
        })

    return results



