from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_transaction_email(sender_email, recipient_email, amount, transaction_id):
    subject = "Transaction Alert 💸"
    message = (
        f"Hi there!\n\n"
        f"A transfer of ₦{amount} was made successfully.\n"
        f"Transaction ID: {transaction_id}\n\n"
        f"If this wasn’t you, please contact support immediately."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [sender_email, recipient_email],
        fail_silently=False,
    )

    return f"Email sent to {sender_email} and {recipient_email}"
