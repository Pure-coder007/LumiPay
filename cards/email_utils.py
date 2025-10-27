import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_card_creation_email(user, card):
    """
    Send an email to the user confirming their new card creation.
    
    Args:
        user: The user who created the card
        card: The Card object that was created
    """
    subject = "Your New LumiPay Card is Ready!"
    
    # Create email context
    context = {
        'user': user,
        'card': {
            'last_four': card.card_number[-4:],
            'card_type': card.get_card_type_display(),
            'expiry_date': card.card_expiry_date,
            'daily_limit': card.format_currency(card.daily_limit),
            'daily_spend': card.format_currency(card.daily_spend),
            'balance': card.format_currency(card.balance),
            'creation_fee': card.format_currency(getattr(settings, 'CARD_CREATION_FEE', 1000.00))
        },
        'support_email': settings.DEFAULT_FROM_EMAIL,
        'app_name': 'LumiPay'
    }
    
    try:
        # Render HTML email
        html_message = render_to_string('cards/emails/card_created.html', context)
        plain_message = strip_tags(html_message)
        
        logger.info(f"Sending card creation email to {user.email}")
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Card creation email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send card creation email to {user.email}: {str(e)}")
        # Don't raise the exception to prevent card creation from failing
        # due to email issues
        return False
