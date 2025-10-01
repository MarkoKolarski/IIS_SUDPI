from django.urls import path
from .views import LoginView, index, register, dashboard_finansijski_analiticar, invoice_list, invoice_filter_options, invoice_detail, invoice_action, reports_data, reports_filter_options, penalties_list, penalties_filter_options, penalties_analysis, suppliers

urlpatterns = [
    path('', index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('dashboard-fa/', dashboard_finansijski_analiticar, name='dashboard_finansijski_analiticar'),
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/filter-options/', invoice_filter_options, name='invoice_filter_options'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/action/', invoice_action, name='invoice_action'),
    path('reports/', reports_data, name='reports_data'),
    path('reports/filter-options/', reports_filter_options, name='reports_filter_options'),
    path('penalties/', penalties_list, name='penalties_list'),
    path('penalties/filter-options/', penalties_filter_options, name='penalties_filter_options'),
    path('penalties/analysis/', penalties_analysis, name='penalties_analysis'),
    path('suppliers/', suppliers.as_view(), name='dobavljaci-list'),
]
