from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random, string, uuid


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must have a valid email')

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user = self.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


    def generate_account_number(self):
        while True:
            account_number = ''.join(random.choices(string.digits, k=10))
            if not User.objects.filter(account_number=account_number).exists():
                return account_number



class User(AbstractUser):
    username=None
    id=models.UUIDField(primary_key=True, default=uuid.uuid10, editable=False)
    first_name=models.CharField(max_length=50, blank=False)
    last_name=models.CharField(max_length=50, blank=False)
    email=models.EmailField(unique=True, blank=False)
    phone_number=models.CharField(max_length=15, blank=False)
    account_number=models.CharField(max_length=10, unique=True, blank=False)
    is_verified=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    kyc_status=models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    is_superuser=models.BooleanField(default=False)
    last_login=models.DateTimeField(auto_now=True)
    profile_picture=models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_joined=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    objects = CustomUserManager()

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

