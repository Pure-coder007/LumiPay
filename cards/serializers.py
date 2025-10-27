from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from .models import Card
from decimal import Decimal


class CurrencyField(serializers.Field):
    """Custom field to format decimal values as currency strings"""
    def to_representation(self, value):
        if value is None:
            return None
        try:
            # Format as Naira with 2 decimal places and thousand separators
            return f'₦{Decimal(str(value)):,.2f}'
        except (ValueError, TypeError):
            return '₦0.00'

    def to_internal_value(self, data):
        # Convert currency string back to decimal if needed
        if isinstance(data, str) and data.startswith('₦'):
            data = data[1:].replace(',', '')
        try:
            return Decimal(str(data))
        except (ValueError, TypeError):
            raise serializers.ValidationError("A valid number is required")


class CardSerializer(serializers.ModelSerializer):
    """Serializer for card details"""
    daily_limit = CurrencyField()
    daily_spend = CurrencyField()
    balance = CurrencyField()
    expiry_date = serializers.SerializerMethodField()
    masked_card_number = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Card
        fields = [
            'id', 'card_type', 'masked_card_number', 'card_expiry_date', 'expiry_date',
            'is_active', 'created_at', 'daily_limit', 'daily_spend',
            'balance', 'is_expired', 'last_used'
        ]
        read_only_fields = fields
    
    def get_expiry_date(self, obj):
        return obj.card_expiry_date
    
    def get_masked_card_number(self, obj):
        return obj.masked_card_number
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class CreateCard(serializers.ModelSerializer):
    pin = serializers.CharField(
        write_only=True,
        required=True,
        validators=[
            MinLengthValidator(4, message="PIN must be exactly 4 digits"),
            RegexValidator(
                regex='^\d{4}$',
                message='PIN must be a 4-digit number',
                code='invalid_pin_format'
            )
        ]
    )
    confirm_pin = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Card
        fields = ['card_type', 'pin', 'confirm_pin']
        extra_kwargs = {
            'card_type': {'required': True}
        }
    
    def validate(self, attrs):
        # Check if PIN and confirm PIN match
        if attrs['pin'] != attrs['confirm_pin']:
            raise ValidationError({"confirm_pin": "PINs do not match"})
        
        # Remove confirm_pin from the data as it's not a model field
        attrs.pop('confirm_pin', None)
        
        return attrs
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError("Authentication required")
        
        # Create the card using the model's create_card method
        try:
            card = Card.create_card(
                user=request.user,
                card_type=validated_data.get('card_type', 'master card'),
                pin=validated_data.get('pin')
            )
            return card
        except Exception as e:
            raise ValidationError(str(e))
    
    def to_representation(self, instance):
        # Use the CardSerializer for consistent formatting
        return CardSerializer(instance, context=self.context).to_representation(instance)