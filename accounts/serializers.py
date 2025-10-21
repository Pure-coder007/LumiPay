from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Wallet, TransactionHistory
from lumipay.tasks import send_transaction_email


class SendMoneySerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    recipient = serializers.CharField(max_length=10)  # account number of recipient

    class Meta:
        model = TransactionHistory
        fields = [
            "amount",
            "recipient",
            "transaction_id",
            "session_id",
            "type",
            "created_at",
        ]
        read_only_fields = ["transaction_id", "session_id", "created_at", "type"]

    def validate(self, data):
        request = self.context.get("request")
        sender = request.user
        recipient_account = data.get("recipient")
        amount = data.get("amount")

        # 1. Get sender’s wallet
        try:
            sender_wallet = Wallet.objects.get(user=sender)
        except Wallet.DoesNotExist:
            raise ValidationError("Sender wallet not found.")

        # 2. Get recipient’s wallet
        try:
            recipient_wallet = Wallet.objects.get(account_number=recipient_account)
        except Wallet.DoesNotExist:
            raise ValidationError("Recipient wallet not found.")

        # 3. Self-transfer check
        if sender_wallet == recipient_wallet:
            raise ValidationError("You cannot send money to yourself.")

        # 4. Balance check
        if sender_wallet.balance < amount:
            raise ValidationError("Insufficient funds.")

        # attach to validated data
        data["sender_wallet"] = sender_wallet
        data["recipient_wallet"] = recipient_wallet
        return data

    def create(self, validated_data):
        sender_wallet = validated_data["sender_wallet"]
        recipient_wallet = validated_data["recipient_wallet"]
        amount = validated_data["amount"]

        with transaction.atomic():
            # 1. Update balances
            sender_wallet.balance -= amount
            sender_wallet.save()
            recipient_wallet.balance += amount
            recipient_wallet.save()

            # 2. Record both transactions
            debit_txn = TransactionHistory.objects.create(
                wallet=sender_wallet,
                amount=amount,
                type="debit",
            )

            TransactionHistory.objects.create(
                wallet=recipient_wallet,
                amount=amount,
                type="credit",
            )
            send_transaction_email.delay(
                sender_wallet.user.email,
                recipient_wallet.user.email,
                str(amount),
                debit_txn.transaction_id,
            )

        return debit_txn
