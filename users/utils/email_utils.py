from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

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
    
    # Render HTML email
    html_message = render_to_string('emails/welcome_email.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
