from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("send_money/", views.SendMoneyView.as_view(), name="send_money"),
    path(
        "transaction_history/",
        views.TransactionHistoryView.as_view(),
        name="transaction_history",
    ),
    path(
        "statement/", views.DownloadStatementView.as_view(), name="download_statement"
    ),
    path("top_up/", views.TopUpWalletView.as_view(), name="top_up_wallet")
]
