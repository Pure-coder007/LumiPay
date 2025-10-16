from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import serializers
from .models import User
from accounts.models import Wallet
from rest_framework.exceptions import ValidationError
from .utils.email_utils import send_welcome_email


class RegisterUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    account_number = serializers.CharField(max_length=10, read_only=True)
    password = serializers.CharField(write_only=True, max_length=20, min_length=8)
    confirm_password = serializers.CharField(
        write_only=True, max_length=20, min_length=8
    )
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)
    confirm_pin = serializers.CharField(write_only=True, min_length=4, max_length=6)
    nin = serializers.CharField(write_only=True, max_length=15)
    bvn = serializers.CharField(write_only=True, max_length=15)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "account_number",
            "password",
            "confirm_password",
            "pin",
            "confirm_pin",
            "nin",
            "bvn",
        ]

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise ValidationError("Email already exists")
        if User.objects.filter(phone_number=attrs["phone_number"]).exists():
            raise ValidationError("Phone number already exists")
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError("Passwords do not match")
        if len(attrs["phone_number"]) != 14 or not attrs["phone_number"].startswith(
            "+234"
        ):
            raise ValidationError(
                "Phone number must start with +234 and must be 14 characters long"
            )
        if attrs["pin"] != attrs["confirm_pin"]:
            raise ValidationError("PINs do not match")
        if len(attrs["pin"]) != 6:
            raise ValidationError("PIN must be 6 characters long")

        # NIN validation
        nin = attrs.get("nin")
        if not nin:
            raise ValidationError("NIN is required")
        if not nin.isnumeric():
            raise ValidationError("NIN must be numeric")
        if len(nin) != 15:
            raise ValidationError("NIN must be 15 characters long")

        # Check if NIN already exists by comparing hashes
        for user in User.objects.all():
            if user.check_nin(nin):
                raise ValidationError("NIN already exists")

        # BVN validation
        bvn = attrs.get("bvn")
        if not bvn:
            raise ValidationError("BVN is required")
        if not bvn.isnumeric():
            raise ValidationError("BVN must be numeric")
        if len(bvn) != 15:
            raise ValidationError("BVN must be 15 characters long")

        # Check if BVN already exists by comparing hashes
        for user in User.objects.all():
            if user.check_bvn(bvn):
                raise ValidationError("BVN already exists")

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_pin")
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        pin = validated_data.pop("pin")

        try:
            with transaction.atomic():
                user = User.objects.create(**validated_data)
                user.set_password(password)
                user.set_pin(pin)
                user.set_nin(validated_data["nin"])
                user.set_bvn(validated_data["bvn"])
                user.account_number = User.objects.generate_account_number()
                user.save()


                Wallet.objects.create(
                    user=user,
                    account_number=user.account_number,
                    balance=user.balance,
                    bvn=user.bvn,
                )
                
                # Send welcome email
                try:
                    send_welcome_email(user)
                except Exception as e:
                    # Log the error but don't fail the registration
                    import logging
                    logger = logging.getLogger(__name__)
                    error_msg = f"Failed to send welcome email to {user.email}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    # Print to console for better visibility in development
                    print(f"\n=== EMAIL ERROR ===\n{error_msg}\n==============\n")
                
                return user
        except Exception as e:
            print(validated_data)
            raise ValidationError(f"Registration failed: {str(e)}")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "account_number",
            "balance",
            "currency",
            "kyc_status",
            "is_verified",
            "is_active",
            "profile_picture",
            "date_joined",
            "updated_at",
        ]
        read_only_fields = [
            "email",
            "account_number",
            "balance",
            "currency",
            "date_joined",
            "updated_at",
        ]
