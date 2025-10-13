from django.db import transaction
from rest_framework import serializers
from .models import User
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class RegisterUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    account_number = serializers.CharField(max_length=10, read_only=True)
    password = serializers.CharField(write_only=True, max_length=20, min_length=8)
    confirm_password = serializers.CharField(write_only=True, max_length=20, min_length=8)
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)
    confirm_pin = serializers.CharField(write_only=True, min_length=4, max_length=6)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'account_number',
            'password', 'confirm_password', 'pin', 'confirm_pin'
        ]

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise ValidationError("Email already exists")
        if User.objects.filter(phone_number=attrs['phone_number']).exists():
            raise ValidationError("Phone number already exists")
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError("Passwords do not match")
        if len(attrs['phone_number']) != 14 or not attrs['phone_number'].startswith('+234'):
            raise ValidationError("Phone number must start with +234 and must be 14 characters long")
        if attrs['pin'] != attrs['confirm_pin']:
            raise ValidationError("PINs do not match")
        if len(attrs['pin']) != 6:
            raise ValidationError("PIN must be 6 characters long")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_pin')
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        pin = validated_data.pop('pin')

        try:
            with transaction.atomic():
                user = User.objects.create(**validated_data)
                user.set_password(password)
                user.set_pin(pin)
                user.account_number = User.objects.generate_account_number()
                user.save()
                return user
        except Exception as e:
            # Optional: log or raise a clear error
            raise ValidationError(f"Registration failed: {str(e)}")





# class LoginUserSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)
#
#     # Fields returned in response
#     token = serializers.CharField(read_only=True)
#     first_name = serializers.CharField(read_only=True)
#     last_name = serializers.CharField(read_only=True)
#     phone_number = serializers.CharField(read_only=True)
#     account_number = serializers.CharField(read_only=True)
#     balance = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
#     kyc_verified = serializers.BooleanField(read_only=True)
#
#     def validate(self, attrs):
#         email = attrs.get("email")
#         password = attrs.get("password")
#
#         # Authenticate using email and password
#         user = authenticate(email=email, password=password)
#         if not user:
#             raise AuthenticationFailed("Invalid email or password")
#
#         # Create or retrieve auth token
#         token, _ = Token.objects.get_or_create(user=user)
#
#         return {
#             "token": token.key,
#             "email": user.email,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "phone_number": user.phone_number,
#             "account_number": user.account_number,
#             "balance": user.balance,
#             "kyc_verified": getattr(user, "kyc_verified", False),
#         }