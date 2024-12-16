from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import jdatetime
from django_jalali.db import models as jmodels



class Category(models.Model):
    name = models.CharField(max_length=50,verbose_name=_("Category Name"))
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='categories')

    def save(self,*args,**kwargs):
        if Category.objects.filter(
                name=self.name,
                user=self.user,
            ).exists():
                raise ValidationError(_('Category already exists!'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Categories'

class Wallet(models.Model):
    name = models.CharField(max_length=50,verbose_name=_("Name"))
    initial_balance = models.FloatField(default=0,verbose_name=_("Initial balance"))
    income = models.FloatField(default=0,null=True,blank=True)
    expense = models.FloatField(default=0,null=True,blank=True)
    exclude_from_total = models.BooleanField(verbose_name=_("Exclude from total"))
    user = models.ForeignKey(User,on_delete = models.CASCADE,related_name='wallets')
    created_at = models.DateTimeField(auto_now_add=True)
    balance = models.FloatField()

    def __str__(self):
        return f'{self.name}'
    
    def save(self,*args,**kwargs):
        self.balance = self.initial_balance + self.income - self.expense
        if self.pk: 
            existing_wallet = Wallet.objects.filter(
                name=self.name,
                user=self.user
            ).exclude(pk=self.pk).first()
            if existing_wallet:
                raise ValidationError(_('Wallet already exists!'))
        else:
            if Wallet.objects.filter(
                name=self.name,
                user=self.user
            ).exists():
                raise ValidationError(_('Wallet already exists!'))

        super().save(*args, **kwargs)

    def get_balance(self):
        return self.initial_balance + self.income - self.expense

    

class Transaction(models.Model):

    TRANSACTION_TYPE_CHOICES = (
         ('',_('Transaction Type')),
        (_('income'), _('Income')),
        (_('expense'), _('Expense')),
    )

    TRANSACTION_REPEATING_CHOICES = (
        ('', _('Repeating')),
        (_('daily'), _('Daily')),
        (_('weekly'), _('Weekly')),
        (_('monthly'), _('Monthly')),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='transactions')
    type = models.CharField(max_length=7,choices=TRANSACTION_TYPE_CHOICES,verbose_name=_("Type"))
    amount = models.FloatField(verbose_name=_("Amount"))
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='transactions',verbose_name=_("Category"))
    date = models.DateField(verbose_name=_("Date"))
    repeating = models.CharField(max_length=20,choices=TRANSACTION_REPEATING_CHOICES,null=True,blank=True,verbose_name=_("Repeating"))
    note = models.CharField(max_length=200,null=True,blank=True,verbose_name=_("Note"))
    wallet_name = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name='transactions',verbose_name=_("Wallet"))
    jalali_date = jmodels.jDateField(verbose_name=_("Jalali Date"))
    
    def __str__(self):
        return f'{self.amount} -> {self.date}'
    
    def get_jalali_date(self):
         return jdatetime.date.fromgregorian(day=self.date.day,month=self.date.month,year=self.date.year)
         
    def get_persian_type(self):
         return 'خرج' if self.type == 'expense' else 'درامد'

    class Meta:
        ordering = ['-date']