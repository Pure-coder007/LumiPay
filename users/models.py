from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random, string, uuid
from django.contrib.auth.hashers import make_password, check_password


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must have a valid email")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.account_number = self.generate_account_number()
        user.save(using=self._db)
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
            account_number = "".join(random.choices(string.digits, k=10))
            if not User.objects.filter(account_number=account_number).exists():
                return account_number


class User(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    nin = models.CharField(max_length=128, blank=False, unique=True, null=False)
    bvn = models.CharField(max_length=128, blank=False, unique=True, null=False)
    phone_number = models.CharField(max_length=15, blank=False, unique=True)
    account_number = models.CharField(max_length=10, unique=True, blank=False)

    currency = models.CharField(
        max_length=5,
        choices=[("NGN", "Naira"), ("USD", "Dollar"), ("EUR", "Euro")],
        default="NGN",
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    pin = models.CharField(max_length=128, blank=True, null=True)

    # 🧾 Profile / KYC
    is_verified = models.BooleanField(default=False)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    # 🔐 Permissions / meta
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]
    objects = CustomUserManager()

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def save(self, *args, **kwargs):
        if self.pin and not self.pin.startswith("pbkdf2_"):
            self.pin = make_password(self.pin)
        super().save(*args, **kwargs)

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)

    def set_bvn(self, *args, **kwargs):
        if self.bvn and not self.bvn.startswith("pbkdf2_"):
            self.bvn = make_password(self.bvn)

    def set_nin(self, *args, **kwargs):
        if self.nin and not self.nin.startswith("pbkdf2_"):
            self.nin = make_password(self.nin)

    def check_bvn(self, raw_bvn):
        return check_password(raw_bvn, self.bvn)

    def check_nin(self, raw_nin):
        return check_password(raw_nin, self.nin)

    def check_bvn(self, raw_bvn):
        return check_password(raw_bvn, self.bvn)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)
