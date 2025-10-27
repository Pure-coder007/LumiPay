from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.core.mail import send_mail
import uuid
import random
import string
from datetime import datetime, timedelta
from users.models import User
from accounts.models import Wallet, TransactionHistory
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

# Create your models here.


def generate_card_number(card_type):
    """Generate a valid card number based on card type"""
    # IIN (Issuer Identification Number) ranges for different card types
    iin_ranges = {
        'visa': '4',
        'master card': ['51', '52', '53', '54', '55'],
        'american express': ['34', '37'],
        'verve': ['5061', '5062', '6500', '6504', '6505', '6507', '6509', '5078', '5079', '6504', '6506', '6507', '6508', '6509', '5041', '5063', '5067', '5090', '5091', '5092', '5093', '5094', '5095', '5096', '5097', '5098', '5099', '6500', '6501', '6502', '6503', '6504', '6505', '6506', '6507', '6508', '6509', '5063', '5067', '5090', '5091', '5092', '5093', '5094', '5095', '5096', '5097', '5098', '5099']
    }
    
    # Get the appropriate IIN based on card type
    card_type_lower = card_type.lower()
    if card_type_lower in iin_ranges:
        iin = random.choice(iin_ranges[card_type_lower]) if isinstance(iin_ranges[card_type_lower], list) else iin_ranges[card_type_lower]
    else:
        iin = '4'  # Default to Visa if card type not found
    
    # Generate the remaining digits (excluding the last check digit)
    remaining_length = 15 - len(iin)
    card_number = iin + ''.join(random.choices('0123456789', k=remaining_length))
    
    # Calculate Luhn check digit
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    check_digit = (10 - (luhn_checksum(card_number + '0') % 10)) % 10
    return card_number + str(check_digit)

class Card(models.Model):
    CARD_TYPES = [
        ('visa', 'Visa'),
        ('verve', 'Verve'),
        ('master card', 'Master Card'),
        ('american express', 'American Express')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=16, unique=True, editable=False)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES, default="master card")
    card_expiry_date = models.CharField(max_length=5, editable=False)
    cvv = models.CharField(max_length=3, editable=False)
    pin_hash = models.CharField(max_length=128, help_text="Hashed card PIN")
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(null=True, blank=True)
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=500000.00)
    daily_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_reset = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_card_display()} - {self.masked_card_number} - {self.user.get_full_name() or self.user.email}"
        
    @staticmethod
    def format_currency(amount):
        """Format currency with Naira symbol and proper formatting"""
        from decimal import Decimal
        try:
            # Convert to Decimal first to handle both string and numeric inputs
            amount = Decimal(str(amount))
            return f"₦{amount:,.2f}"
        except (ValueError, TypeError):
            return f"₦0.00"

    @property
    def masked_card_number(self):
        """Return masked card number for display"""
        if self.card_number:
            return f"**** **** **** {self.card_number[-4:]}"
        return ""

    @property
    def expiry_month(self):
        """Get the expiry month"""
        if self.card_expiry_date and len(self.card_expiry_date) == 5:
            return self.card_expiry_date[:2]
        return ""

    @property
    def expiry_year(self):
        """Get the expiry year"""
        if self.card_expiry_date and len(self.card_expiry_date) == 5:
            return self.card_expiry_date[3:]
        return ""

    def set_pin(self, raw_pin):
        """Set the hashed PIN"""
        if len(str(raw_pin)) != 4 or not str(raw_pin).isdigit():
            raise ValueError("PIN must be a 4-digit number")
        self.pin_hash = make_password(str(raw_pin))

    def check_pin(self, raw_pin):
        """Verify the provided PIN"""
        if not self.pin_hash:
            return False
        return check_password(str(raw_pin), self.pin_hash)

    def is_expired(self):
        """Check if the card is expired"""
        if not self.card_expiry_date:
            return True
            
        try:
            month = int(self.card_expiry_date[:2])
            year = int('20' + self.card_expiry_date[3:])  # Assuming 2-digit year
            expiry_date = datetime(year, month, 1)  # Set to first day of expiry month
            return expiry_date < datetime.now()
        except (ValueError, IndexError):
            return True

    def reset_daily_spend(self):
        """Reset the daily spend if it's a new day"""
        today = timezone.now().date()
        if self.last_reset != today:
            self.daily_spend = 0.00
            self.last_reset = today
            self.save(update_fields=['daily_spend', 'last_reset'])

    def has_sufficient_funds(self, amount):
        """Check if the card has sufficient funds and within daily limit"""
        self.reset_daily_spend()
        has_funds = self.balance >= amount
        within_daily_limit = (self.daily_spend + amount) <= self.daily_limit
        return has_funds and within_daily_limit and not self.is_expired()

    @classmethod
    def create_card(cls, user, card_type='master card', pin=None):
        """
        Create a new card with secure details, charge the user's wallet
        for the card creation fee, and send a confirmation email.
        
        Args:
            user: The user creating the card
            card_type: Type of card to create (must be unique per user)
            pin: 4-digit PIN for the card
            
        Returns:
            Card: The newly created card
            
        Raises:
            ValidationError: If user already has this card type or other validation fails
        """
        if not pin or len(str(pin)) != 4 or not str(pin).isdigit():
            raise ValidationError(_("A valid 4-digit PIN is required"))

        # Check if user already has this type of card
        if user.cards.filter(card_type=card_type, is_active=True).exists():
            raise ValidationError(_(f"You already have an active {card_type} card"))

        # Check if user already has too many active cards
        max_cards = 3  # Maximum number of cards per user
        if user.cards.filter(is_active=True).count() >= max_cards:
            raise ValidationError(_(f"Maximum limit of {max_cards} active cards reached"))

        # Get the card creation fee from settings and convert to Decimal
        from django.conf import settings
        from decimal import Decimal
        card_creation_fee = Decimal(str(getattr(settings, 'CARD_CREATION_FEE', 1000.00)))

        with transaction.atomic():
            # Get the user's wallet and lock it for update
            wallet = Wallet.objects.select_for_update().get(user=user)
            
            # Check if user has sufficient balance
            if wallet.balance < card_creation_fee:
                raise ValidationError({
                    'error': _('Insufficient balance for card creation fee'),
                    'required_amount': card_creation_fee,
                    'current_balance': wallet.balance
                })
            
            # Generate card details
            card = cls(
                user=user,
                card_type=card_type,
                card_number=generate_card_number(card_type),
                cvv=''.join(random.choices('0123456789', k=3)),
            )
            
            # Set expiry date (4 years from now)
            expiry_date = (timezone.now() + timedelta(days=365*4)).strftime('%m/%y')
            card.card_expiry_date = expiry_date
            
            # Set the PIN
            card.set_pin(pin)
            
            # Set initial balance (wallet balance minus fee)
            wallet.balance -= card_creation_fee
            wallet.save()
            
            # Create transaction record for the card creation fee
            TransactionHistory.objects.create(
                wallet=wallet,
                amount=card_creation_fee,
                type='debit',
                narration=f'Card creation fee for new {card_type} card',
                balance_after_transaction=wallet.balance
            )
            
            # Set card balance (initial balance from wallet after fee deduction)
            card.balance = wallet.balance
            card.save()
            
            # Send email notification (in a try-except to prevent card creation from failing)
            try:
                from .email_utils import send_card_creation_email
                send_card_creation_email(user, card)
            except Exception as e:
                logger.error(f"Failed to send card creation email to {user.email}: {str(e)}")
            
            return card
