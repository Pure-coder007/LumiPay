from rest_framework import serializers
from .models import User
import random
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token


class RegisterUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    account_number = serializers.CharField(max_length=10, read_only=True)
    password = serializers.CharField(write_only=True, max_length=20, min_length=8)
    confirm_password = serializers.CharField(write_only=True, max_length=20, min_length=8)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'account_number', 'password', 'confirm_password']


    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise ValidationError("Email already exists")
        if User.objects.filter(phone_number=attrs['phone_number']).exists():
            raise ValidationError("Phone number already exists")
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError("Passwords do not match")
        if len(attrs['phone_number']) != 15 or not attrs['phone_number'].startswith('+234'):
            raise ValidationError("Phone number must start with +234 and must be 15 characters long")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user