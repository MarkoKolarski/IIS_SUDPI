from django.urls import path
from .views import LoginView, index, register, dashboard_finansijski_analiticar, invoice_list, invoice_filter_options

urlpatterns = [
    path('', index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('dashboard-fa/', dashboard_finansijski_analiticar, name='dashboard_finansijski_analiticar'),
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/filter-options/', invoice_filter_options, name='invoice_filter_options'),
]
