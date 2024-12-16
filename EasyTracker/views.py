from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TransactionForm, WalletForm, CategoryForm
from .models import Transaction, Wallet, Category 
from datetime import date
from django.utils.translation import activate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import JsonResponse
from django.views import generic
from django.db.models import *
from django.db.models import *
import jdatetime


class HomeView(LoginRequiredMixin,View):
    def get(self,request):
        if 'lang' in request.session:
            activate(request.session['lang'])
        total_wallet = Wallet.objects.get(user=request.user,exclude_from_total=False,name='Total')
        total_balance = total_wallet.initial_balance + total_wallet.income - total_wallet.expense
        wallets = Wallet.objects.filter(user=request.user,exclude_from_total=False).exclude(name='Total').order_by('-balance')


        return render(request,'EasyTracker/new-home.html',{
            'wallets':wallets,'total_balance':total_balance
        })
    
class WalletsView(LoginRequiredMixin,View):
    def get(self,request):
        if 'lang' in request.session:
                activate(request.session['lang'])
        total_wallet = Wallet.objects.get(user=request.user,name='Total')
        has_wallet = False
        wallets = Wallet.objects.filter(user=request.user,exclude_from_total=False).exclude(name='Total')
        if wallets:
            has_wallet = True
        return render(request,'EasyTracker/wallets.html',{'total_wallet':total_wallet,
                                                          'wallets':wallets,'has_wallet':has_wallet})
    
class WalletView(LoginRequiredMixin,View):
    def get(self,request,pk):
        wallet = Wallet.objects.get(user=request.user,pk=pk)
        wallet_d = Wallet.objects.filter(user=request.user,pk=pk)\
            .values('transactions__date__month','transactions__date__year')\
                .annotate(count=Count('transactions'))
        have_transactions = False
        if wallet_d[0]['count'] > 0 :
            have_transactions=True
        return render(request,'EasyTracker/wallet.html',{"pk":pk,
            'wallet':wallet,'wallet_d':wallet_d,'have_transactions':have_transactions
        })
    
class WalletDetailView(LoginRequiredMixin,View):
    def get(self,request,pk,month,year):
        incomes = Transaction.objects.filter(user=request.user,wallet_name__pk=pk,date__month=month,type='income',\
                                             date__year=year).values_list('amount').aggregate(sum=Sum('amount',default=0))['sum']
        expenses = Transaction.objects.filter(user=request.user,wallet_name__pk=pk,date__month=month,type='expense',\
                                              date__year=year).values_list('amount').aggregate(sum=Sum('amount',default=0))['sum']
        
        transaction_summary = Transaction.objects\
        .filter(user=request.user,wallet_name__pk=pk,date__month=month,date__year=year)\
        .values('date')\
        .annotate(
            sum_incomes=Sum(Case(
                When(type='income', then='amount'),
                output_field=FloatField(),default=0,
            )),
            sum_expenses=Sum(Case(
                When(type='expense', then='amount'),
                output_field=FloatField(),default=0,
            ))
        ).order_by('-date')

        # CONVERT TO JALALI
        # for item in transaction_summary:
        #     item['date'] = jdatetime.date.fromgregorian(day=item['date'].day,
        #     month=item['date'].month,year=item['date'].year)

        return render(request,'EasyTracker/month-detail.html',{'pk':pk,'incomes':incomes,'expenses':expenses,
                                                               'month':month,'year':year,'transaction_summary':transaction_summary})



class WalletDayDetailView(LoginRequiredMixin,View):
    def get(self,request,pk,date):
        transactions = Transaction.objects.filter(user=request.user,wallet_name__pk=pk,date=date)
        return render(request,'EasyTracker/day-detail-transactions.html',{'pk':pk,'transactions':transactions,'date':date})


class MonthReportView(LoginRequiredMixin,View):
    def get(self,request,pk,month,year):
        transaction_summary = Transaction.objects\
        .filter(user=request.user,wallet_name__pk=pk,date__month=month,date__year=year)\
        .values('date')\
        .annotate(
            sum_incomes=Sum(Case(
                When(type='income', then='amount'),
                output_field=FloatField(),default=0,
            )),
            sum_expenses=Sum(Case(
                When(type='expense', then='amount'),
                output_field=FloatField(),default=0,
            ))
        ).order_by('-date')
        print(transaction_summary)
        dates = [item['date'].strftime(format="%d-%m") for item in transaction_summary]
        incomes = [item['sum_incomes'] for item in transaction_summary]
        expenses = [item['sum_expenses'] for item in transaction_summary]

        categories = Transaction.objects.filter(user=request.user,wallet_name__pk=pk,date__month=month,date__year=year)\
        .values('category__name').annotate(sum_expens=Sum('amount'))
        category_names = [item['category__name'] for item in categories]
        category_expense = [item['sum_expens'] for item in categories]
        return render(request,'EasyTracker/dashboard.html',{'dates':dates,'incomes':incomes,
                                                            'expenses':expenses})
# TABLE VIEW
class TableView(LoginRequiredMixin,View):
    def get(self,request):
        print(request.GET)
        transactions = Transaction.objects.filter(user=request.user,wallet_name__exclude_from_total=False)
        categories = Category.objects.filter(user=request.user)
        cat = 'all'
        if 'category' in request.GET:
            cat = request.GET.get('category')
            if cat != 'all':
                transactions = transactions.filter(category=cat)
        from_date = request.GET.get('from-date')
        if from_date:
            transactions = transactions.filter(date__gte=from_date)
        to_date = request.GET.get('to-date')
        if to_date:
            transactions = transactions.filter(date__lte=to_date)
        cat = int(cat) if cat != 'all' else cat
        income = int(transactions.filter(type='income').aggregate(Sum('amount',default=0))['amount__sum'])
        expense = int(transactions.filter(type='expense').aggregate(Sum('amount',default=0))['amount__sum'])
        return render(request,'EasyTracker/table.html',{'transactions':transactions,'categories':categories,
        'income':income,'expense':expense,'selected_cat':cat,'from_date':from_date,'to_date':to_date})
    # def get(self,request):
    #         if 'lang' in request.session:
    #             activate(request.session['lang'])
    #         categories = Category.objects.filter(user=request.user)
    #         transactions = Transaction.objects.filter(user=request.user,wallet_name__exclude_from_total=False)
    #         cat = 'all'
    #         type = 'all'
    #         year = 'all'
    #         month = 'all'
    #         wallet = 'all'

    #         if 'wallet' in request.GET:
    #             wallet = request.GET.get('wallet')
    #             if wallet != 'all':
    #                 transactions = transactions.filter(wallet_name__name=wallet)

    #         if 'category' in request.GET:
    #             cat = request.GET.get('category')
    #             if cat != 'all':
    #                 transactions = transactions.filter(category=cat)

            
    #         if 'type' in request.GET:
    #             type = request.GET.get('type')
    #             if type != 'all':
    #                 transactions = transactions.filter(type=type)

    #         months = set(transactions.values_list('date__month',flat=True).distinct())
    #         years = set(transactions.values_list('date__year',flat=True).distinct())
    #         wallets = set(transactions.values_list('wallet_name__name',flat=True).distinct())

    #         if 'year' in request.GET:
    #             year = request.GET.get('year')
    #             if year != 'all':
    #                 year = int(year)
    #                 transactions = transactions.filter(date__year=year)
                
    #         if 'month' in request.GET:
    #             month = request.GET.get('month')
    #             if month != 'all':
    #                 month = int(month)
    #                 transactions = transactions.filter(date__month=month)

    #         income = int(transactions.filter(type='income').aggregate(Sum('amount',default=0))['amount__sum'])
    #         expense = int(transactions.filter(type='expense').aggregate(Sum('amount',default=0))['amount__sum'])
    #         net = income-expense
    #         return render(request,'EasyTracker/home.html',{'transactions':transactions,'categories':categories,
    #                                                        'cat':cat,'type':type,'income':income,
    #                                                        'expense':expense,'net':net,'months':months,'years':years,
    #                                                        'month':month,'year':year,'wallets':wallets,'wallet':wallet})


class ChangeLangView(LoginRequiredMixin,View):
    def get(self,request):
        lang = request.GET.get('lang')
        request.session['lang'] = lang
        request.session.save()
        return redirect(request.GET.get('next'))
    

class AddTransactionView(LoginRequiredMixin,View):
    def get(self,request):
        if request.htmx:  
            if 'lang' in request.session:
                activate(request.session['lang'])
            has_wallet = False
            if Wallet.objects.filter(user=request.user).exclude(name='Total'):
                has_wallet = True
            form = TransactionForm(request.user,initial={'date': date.today,'type':'expense'})
            categories = Category.objects.filter(user=request.user)
            return render(request,'EasyTracker/add-transaction.html',{'form':form,
                                                                      'categories':categories,
                                                                        'has_wallet':has_wallet})
        # 
        # transactions = Transaction.objects.filter(user=request.user,wallet_name__exclude_from_total=False)
        # return render(request,'EasyTracker/home.html',{'transactions':transactions,'categories':categories,
        #                                                'wallets':wallets})
    
    def post(self,request):
        if request.htmx:
            if 'lang' in request.session:
                activate(request.session['lang'])
                print(request.POST)
            form = TransactionForm(request.user,request.POST)
            has_wallet = False
            if Wallet.objects.filter(user=request.user).exclude(name='Total'):
                has_wallet = True
            # categories = Category.objects.filter(user=request.user)
            if form.is_valid():
                cd = form.cleaned_data
                date = cd['date']
                jdate = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
                Transaction.objects.create(user=request.user,type=cd['type'],amount=cd['amount'],
                                        category=cd['category'],date=cd['date'],repeating=cd['repeating'],
                                        note=cd['note'],wallet_name=cd['wallet_name'],jalali_date = jdate)
                w = Wallet.objects.get(user = request.user,name = cd['wallet_name'])
                total_wallet = Wallet.objects.get(user = request.user,name = 'Total')
                if cd['type'] == 'income':
                    w.income += int(cd['amount'])
                    if w.exclude_from_total == False:
                        total_wallet.income += int(cd['amount'])
                else:
                    w.expense += int(cd['amount'])
                    if w.exclude_from_total == False:
                        total_wallet.expense += int(cd['amount'])
                w.save()
                total_wallet.save()
                
                print(jdate)
                messages.success(request,_("Transactin added successfully"))
                return render(request,'EasyTracker/success.html')
            return render(request,'EasyTracker/add-transaction.html',{'form':form,'has_wallet':has_wallet})
        
class TransactionMoreView(LoginRequiredMixin,View):
    def get(self,request):
        if request.htmx:
            return render(request,'EasyTracker/more.html')
        
class TransactionLessView(LoginRequiredMixin,View):
    def get(self,request):
        if request.htmx:
            return render(request,'EasyTracker/less.html')




class AddWalletView(LoginRequiredMixin,View):
    def get(self,request):
        if request.htmx:
            if 'lang' in request.session:
                activate(request.session['lang'])
            form = WalletForm()
            print(form.data)    
            return render(request,'EasyTracker/add-wallet.html',{'form':form})
        
    def post(self,request):
        if request.htmx:
            try:
                if 'lang' in request.session:
                    activate(request.session['lang'])
                form = WalletForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    Wallet.objects.create(name=cd['name'],initial_balance=cd['initial_balance'],
                                        exclude_from_total=cd['exclude_from_total'],user=request.user)
                    total_wallet = Wallet.objects.get(user=request.user,name='Total')
                    if cd['exclude_from_total'] == False:
                        total_wallet.initial_balance += cd['initial_balance']
                        total_wallet.save()
                    messages.success(request,_("Wallet added successfully"))
                    return render(request,'EasyTracker/success.html')
                return render(request,'EasyTracker/add-wallet.html',{'form':form})
            except ValidationError as e:
                exc = _(e.message)
                return render(request,'EasyTracker/add-wallet.html',{'form':form,'exc':exc})
        


    
class CategoriesView(LoginRequiredMixin,View):
    def get(self,request):
        if 'lang' in request.session:
                activate(request.session['lang'])
        categories = Category.objects.filter(user=request.user)
        return render(request,'EasyTracker/categories.html',{'categories':categories})
    
class AddCategoryView(LoginRequiredMixin,View):
    def get(self,request):
        if request.htmx:
            if 'lang' in request.session:
                activate(request.session['lang'])
            form = CategoryForm()
            return render(request,'EasyTracker/add-category.html',{'form':form})
        
    def post(self,request):
        if request.htmx:
            try:
                if 'lang' in request.session:
                    activate(request.session['lang'])
                form = CategoryForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    Category.objects.create(name=cd['name'],user=request.user)
                    messages.success(request,_("Transactin added successfully"))
                    return render(request,'EasyTracker/success.html')
                return render(request,'EasyTracker/add-category.html',{'form':form})
            except ValidationError as e:
                exc = _(e.message)
                return render(request,'EasyTracker/add-category.html',{'form':form,'exc':exc})


