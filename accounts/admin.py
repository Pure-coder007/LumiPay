from django.contrib import admin
from .models import Wallet, TransactionHistory

# Register your models here.
admin.site.register(Wallet)
admin.site.register(TransactionHistory)
