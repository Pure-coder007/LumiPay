from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User
from .models import Wallet, TransactionHistory
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

            sender_user = sender_wallet.user
            receiver_user = User.objects.get(account_number=recipient_wallet.account_number)

            # 2. Record both transactions
            debit_txn = TransactionHistory.objects.create(
                wallet=sender_wallet,
                amount=amount,
                type="debit",
                sender=sender_user,
                receiver=receiver_user,
                balance_after_transaction=sender_wallet.balance
            )

            TransactionHistory.objects.create(
                wallet=recipient_wallet,
                amount=amount,
                type="credit",
                sender=sender_user,
                receiver=receiver_user,
                balance_after_transaction=sender_wallet.balance
            )
            # Update user balance
            sender_wallet.user.balance = sender_wallet.balance
            sender_wallet.user.save()
            recipient_wallet.user.balance = recipient_wallet.balance
            recipient_wallet.user.save()

            send_transaction_email.delay(
                sender_wallet.user.email,
                recipient_wallet.user.email,
                str(amount),
                debit_txn.transaction_id,
            )

        return debit_txn



# Get Transaction History
class TransactionHistorySerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()


    class Meta:
        model = TransactionHistory
        fields = [
            "transaction_id",
            "session_id",
            "amount",
            "type",
            "created_at",
            "sender_name",
            "receiver_name",
            "wallet_balance",
        ]

    def get_wallet_balance(self, obj):
        # Instead of current wallet balance, use stored balance after transaction
        return obj.balance_after_transaction

    def get_sender_name(self, obj):
        sender = obj.sender
        if not sender:
            return None
        # Prefer full name, else username or email
        return (
            f"{sender.first_name} {sender.last_name}".strip()
            or sender.username
            or sender.email
        )

    def get_receiver_name(self, obj):
        receiver = obj.receiver
        if not receiver:
            return None
        return (
            f"{receiver.first_name} {receiver.last_name}".strip()
            or receiver.username
            or receiver.email
        )



