from django.core.mail import send_mail
from django.conf import settings

from .models import VerificationCode
import random


def send_verification_email(subject, message, recipient_email):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False
        )
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


def create_and_send_verification(user, purpose, subject, message_template):
    code = str(random.randint(100000, 999999))
    VerificationCode.objects.create(user=user, code=code, purpose=purpose)

    message = message_template.format(code=code)

    send_verification_email(subject, message, user.email)
