from django.db import models
from django.conf import settings
import uuid, random, string


def random_transaction_id():
    while True:
        transaction_id = "".join(random.choices(string.digits, k=12))
        if not TransactionHistory.objects.filter(
            transaction_id=transaction_id
        ).exists():
            return transaction_id


def random_session_id():
    while True:
        session_id = "".join(random.choices(string.digits, k=12))
        if not TransactionHistory.objects.filter(session_id=session_id).exists():
            return session_id


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=100000.00)
    bvn = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.account_number}"


class TransactionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=10, choices=[("credit", "Credit"), ("debit", "Debit")]
    )
    transaction_id = models.CharField(
        max_length=12, unique=True, default=random_transaction_id
    )
    session_id = models.CharField(max_length=12, unique=True, default=random_session_id)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="sent_transactions",
        on_delete=models.SET_NULL,
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="received_transactions",
        on_delete=models.SET_NULL,
    )
    narration = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance_after_transaction = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.wallet.user.email} - {self.amount} ({self.type})"
