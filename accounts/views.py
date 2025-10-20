from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.request import Request
from .serializers import SendMoneySerializer


class SendMoneyView(APIView):
    permission_classes = [IsAuthenticated]
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = "send_money"

    def post(self, request: Request):
        amount = request.data.get("amount")
        recipient = request.data.get("recipient")

        if not amount or not recipient:
            return Response(
                {"message": "Amount and recipient are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SendMoneySerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            transaction = serializer.save()
            return Response(
                {
                    "message": "Transaction Successful",
                    "data": {
                        "transaction_id": transaction.transaction_id,
                        "session_id": transaction.session_id,
                        "amount": str(transaction.amount),
                        "type": transaction.type,
                        "sender": str(transaction.wallet.user.first_name + " " + transaction.wallet.user.last_name),
                    },
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Transaction Failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
