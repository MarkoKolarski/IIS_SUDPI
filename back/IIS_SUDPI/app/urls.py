from django.urls import path
from .views import LoginView, index, register, dashboard_finansijski_analiticar, invoice_list, invoice_filter_options, invoice_detail, invoice_action, reports_data, reports_filter_options, penalties_list, penalties_filter_options, penalties_analysis, suppliers, visits_list, visit_detail, create_visit, complaints_list, create_complaint, select_supplier
from .views_saga import create_faktura_with_payment_saga, create_penal_saga, saga_status

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
    path('suppliers/<int:sifra_d>/', suppliers.as_view(), name='dobavljaci-detail'),
    path('suppliers/<int:sifra_d>/select/', select_supplier, name='select-supplier'),

    # Kontrolor Kvaliteta endpoints
    path('visits/', visits_list, name='visits-list'),
    path('visits/<int:visit_id>/', visit_detail, name='visit-detail'),
    path('visits/create/', create_visit, name='visit-create'),
    path('complaints/', complaints_list, name='complaints-list'),
    path('complaints/create/', create_complaint, name='complaint-create'),
    
    # SAGA PATTERN - Transakciona obrada podataka (Oracle + InfluxDB)
    path('saga/faktura-sa-placanjem/', create_faktura_with_payment_saga, name='saga-faktura-payment'),
    path('saga/penal/', create_penal_saga, name='saga-penal'),
    path('saga/status/', saga_status, name='saga-status'),
]
