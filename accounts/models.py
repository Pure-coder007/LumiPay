from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random, string, uuid
from users.models import User
import random, string
from django.contrib.auth.hashers import make_password, check_password


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, unique=True, blank=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=100000.00)
    bvn = models.CharField(max_length=128, blank=False, unique=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.account_number}"


def random_transaction_id():
    while True:
        transaction_id = "".join(random.choices(string.digits, k=12))
        if not TransactionHistory.objects.filter(transaction_id=transaction_id).exists():
            return transaction_id


def random_session_id():
    while True:
        session_id = "".join(random.choices(string.digits, k=12))
        if not TransactionHistory.objects.filter(session_id=session_id).exists():
            return session_id


class TransactionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=[("credit", "Credit"), ("debit", "Debit")])
    transaction_id = models.CharField(max_length=12, unique=True, blank=False, default=random_transaction_id)
    session_id = models.CharField(max_length=12, unique=True, blank=False, default=random_session_id)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.wallet} - {self.amount}"