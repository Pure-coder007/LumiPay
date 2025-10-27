from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.humanize.templatetags.humanize import intcomma
from weasyprint import HTML
from datetime import datetime
from django.template.loader import render_to_string
from accounts.models import TransactionHistory
from users.models import User
from .serializers import SendMoneySerializer, TransactionHistorySerializer, TopUpWalletSerializer
from .models import TransactionHistory
# from rest_framework.authentication import SessionAuthentication, TokenAuthentication



class SendMoneyView(APIView):
    permission_classes = [IsAuthenticated]
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
        if not serializer.is_valid():
            return Response(
                {"message": "Validation error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction = serializer.save()
            return Response(
                {
                    "message": "Transaction Successful",
                    "data": {
                        "session_id": transaction.session_id,
                        "amount": str(transaction.amount),
                        "type": transaction.type,
                        "sender": f"{transaction.wallet.user.first_name or ''} {transaction.wallet.user.last_name or ''}".strip(),
                        "recipient": f"{transaction.receiver.first_name or ''} {transaction.receiver.last_name or ''}".strip(),
                        "narration": transaction.narration or "",
                        "created_at": transaction.created_at,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3  # Number of items per page
    page_size_query_param = 'page_size'
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


class DownloadStatementView(APIView):
    # authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = TransactionHistory.objects.filter(wallet__user=user).order_by('-created_at')

        # Render the statement template
        html_string = render_to_string(
            'accounts/statement.html',  # Make sure this template exists
            {
                'user': user,
                'transactions': transactions,
                'date': datetime.now(),
            }
        )

        # Generate PDF from HTML
        pdf_file = HTML(string=html_string).write_pdf()

        # Return PDF as response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="statement_{user.account_number}.pdf"'
        return response


class TopUpWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TopUpWalletSerializer(data=request.data)
        if serializer.is_valid():
            wallet = serializer.save()
            response = {
                "message": "Wallet topped up successfully",
                "data": {
                    "account_number": wallet.account_number,
                    "new_balance": f"₦{wallet.balance:,.2f}",
                    "currency": "NGN"
                }
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "Validation error",
                "data": serializer.errors,
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
