from django.urls import path
from .views import *

app_name = 'easy-tracker'
urlpatterns = [
    path('change-lang/',ChangeLangView.as_view(),name='change-lang'),
    path('',HomeView.as_view(),name='home'),
    path('add-transaction/',AddTransactionView.as_view(),name='add-transaction'),
    path('more/',TransactionMoreView.as_view(),name='transaction-more'),
    path('less/',TransactionLessView.as_view(),name='transaction-less'),
    path('wallets/',WalletsView.as_view(),name='wallets'),
    path('wallet/<int:pk>/',WalletView.as_view(),name='wallet'),
    path('wallet/<int:pk>/<int:month>/<int:year>/',WalletDetailView.as_view(),name='month-detail'),
    path('wallet/<int:pk>/<str:date>/',WalletDayDetailView.as_view(),name='day-detail'),
    path('wallet/report/<int:pk>/<int:month>/<int:year>',MonthReportView.as_view(),name='month-report'),
    path('add-wallet/',AddWalletView.as_view(),name='add-wallet'),
    path('categories/',CategoriesView.as_view(),name='categories'),
    path('add-category/',AddCategoryView.as_view(),name='add-category'),
    path('table/',TableView.as_view(),name='table'),
]