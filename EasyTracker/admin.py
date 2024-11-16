from django.contrib import admin
from .models import Category, Wallet, Transaction
from django.utils.translation import get_language


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'category', 'date', 'jalali_date')  # Add jalali_date here


admin.site.register(Category)
admin.site.register(Wallet)
admin.site.register(Transaction,TransactionAdmin)

