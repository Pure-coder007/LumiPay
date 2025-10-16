import logging
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import smtplib
import socket

logger = logging.getLogger(__name__)

def send_welcome_email(user):
    """
    Send a welcome email to a newly registered user.
    """
    subject = 'Welcome to LumiPay!'
    
    # Create email context
    context = {
        'user': user,
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }
    
    try:
        # Render HTML email
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        logger.info(f"Attempting to send welcome email to {user.email}")
        
        # Test SMTP connection first
        try:
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
                if settings.EMAIL_USE_TLS:
                    server.starttls()
                if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP connection error: {str(e)}")
            raise Exception(f"SMTP connection failed: {str(e)}")
        except socket.error as e:
            logger.error(f"Socket error when connecting to SMTP server: {str(e)}")
            raise Exception(f"Could not connect to SMTP server: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during SMTP setup: {str(e)}")
            raise Exception(f"Email setup error: {str(e)}")
        
        # If SMTP test passes, send the actual email
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent welcome email to {user.email}")
        
    except BadHeaderError:
        logger.error("Invalid header found in email")
        raise Exception("Invalid header found in email")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        raise Exception(f"Failed to send welcome email: {str(e)}")
