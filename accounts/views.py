from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from .serializers import SendMoneySerializer, TransactionHistorySerializer
from .models import TransactionHistory


class SendMoneyView(APIView):
    permission_classes = [IsAuthenticated]
    # throttle_scope = "send_money"

    def post(self, request: Request):
        amount = request.data.get("amount")
        recipient = request.data.get("recipient")

        if not amount or not recipient:
            return Response(
                {"message": "Amount and recipient are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SendMoneySerializer(
            data=request.data, context={"request": request}
        )
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
                        "sender": str(
                            transaction.wallet.user.first_name
                            + " "
                            + transaction.wallet.user.last_name
                        ),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Transaction Failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum limit for page size

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request: Request):
        transactions = TransactionHistory.objects.filter(wallet__user=request.user).order_by('-created_at')
        
        # Set up pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(transactions, request)
        
        if page is not None:
            serializer = TransactionHistorySerializer(page, many=True)
            return paginator.get_paginated_response({
                "message": "Transaction history fetched successfully",
                "data": serializer.data,
                "pagination": {
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "count": paginator.page.paginator.count,
                    "page": paginator.page.number,
                    "pages": paginator.page.paginator.num_pages,
                }
            })
            
        serializer = TransactionHistorySerializer(transactions, many=True)
        return Response(
            {
                "message": "Transaction history fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
