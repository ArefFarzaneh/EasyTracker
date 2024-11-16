from django import forms
from .models import Transaction, Wallet, Category 
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date,timedelta


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('type','amount','category','date','repeating','note','wallet_name',)
        widgets={
            'date': forms.DateInput(attrs={
             'min': date.today()-timedelta(days=2)  }),
        }
        labels={
        }
        error_messages = {
            'amount':{'required':_('Please fill the amount field.'),'min_value':_('The amount must be positive')},
            'type':{'required':_('Please fill the type field.')},
            'date':{'required':_('Please fill the date field.')},
            'category':{'required':_('Please fill the category field.')},
            'wallet_name':{'required':_('Please fill the wallet name field.')}
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['wallet_name'].queryset = Wallet.objects.filter(user=user)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if cleaned_data['type'] == 'expense' and cleaned_data['amount'] > cleaned_data['wallet_name'].initial_balance:
    #         raise ValidationError('Insufficient balance in wallet')
    #     return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount is not None and amount < 0:
            self.add_error('amount', _('Amount must be positive.'))


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('name','initial_balance','exclude_from_total',)
        widgets={
        }

        labels={
        }

        error_messages = {
            'name':{'required':_('Please fill the name field.')},
            'initial_balance':{'required':_('Please fill the initial balance field.')},
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
        widgets={
            
        }

        labels={
            
        }