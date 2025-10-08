from django.urls import path
from .views_saga import create_faktura_with_payment_saga, create_penal_saga, saga_status
from .views import LoginView, index, register, dashboard_finansijski_analiticar, invoice_list, invoice_filter_options, invoice_detail, invoice_action, reports_data, reports_filter_options, penalties_list, penalties_filter_options, penalties_analysis, check_and_create_penalties, preview_contract_violations, select_supplier, skladista_list, dodaj_skladiste, dodaj_artikal, artikli_list, obrisi_artikal, artikal_detail, izmeni_artikal, zalihe_list, zaliha_detail, izmeni_zalihu, rizicni_artikli_list, artikli_statistike, artikli_grafikon_po_nedeljama, simulate_payment
from .views_mv import suppliers, visits_list, visit_detail, create_visit, complaints_list, create_complaint, busy_visit_slots

urlpatterns = [
    path('', index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('dashboard-fa/', dashboard_finansijski_analiticar, name='dashboard_finansijski_analiticar'),
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/filter-options/', invoice_filter_options, name='invoice_filter_options'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/action/', invoice_action, name='invoice_action'),
    path('invoices/<int:invoice_id>/simulate-payment/', simulate_payment, name='simulate_payment'),
    path('reports/', reports_data, name='reports_data'),
    path('reports/filter-options/', reports_filter_options, name='reports_filter_options'),
    path('penalties/', penalties_list, name='penalties_list'),
    path('penalties/filter-options/', penalties_filter_options, name='penalties_filter_options'),
    path('penalties/analysis/', penalties_analysis, name='penalties_analysis'),
    path('penalties/check-violations/', preview_contract_violations, name='preview_contract_violations'),
    path('penalties/auto-create/', check_and_create_penalties, name='check_and_create_penalties'),
    path('suppliers/', suppliers.as_view(), name='dobavljaci-list'),
    path('suppliers/<int:sifra_d>/', suppliers.as_view(), name='dobavljaci-detail'),
    path('suppliers/<int:sifra_d>/select/', select_supplier, name='select-supplier'),

    # Kontrolor Kvaliteta endpoints
    path('visits/', visits_list, name='visits-list'),
    path('visits/<int:visit_id>/', visit_detail, name='visit-detail'),
    path('visits/create/', create_visit, name='visit-create'),
    path('visits/busy-slots/', busy_visit_slots, name='busy-visit-slots'),
    path('complaints/', complaints_list, name='complaints-list'),
    path('complaints/create/', create_complaint, name='complaint-create'),

    # SAGA PATTERN - Transakciona obrada podataka (Oracle + InfluxDB)
    path('saga/faktura-sa-placanjem/', create_faktura_with_payment_saga, name='saga-faktura-payment'),
    path('saga/penal/', create_penal_saga, name='saga-penal'),
    path('saga/status/', saga_status, name='saga-status'),

    # Artikal i Skladiste endpoints
    path('skladista/', skladista_list, name='skladista-list'),
    path('skladista/dodaj/', dodaj_skladiste, name='dodaj-skladiste'),
    path('artikli/', artikli_list, name='artikli-list'),
    path('artikli/dodaj/', dodaj_artikal, name='dodaj-artikal'),
    path('artikli/<int:sifra_a>', artikal_detail, name='artikal-detail'),
    path('artikli/<int:sifra_a>/izmeni', izmeni_artikal, name='izmeni-artikal'),
    path('artikli/<int:sifra_a>/obrisi', obrisi_artikal, name='obrisi-artikal'),
    path('zalihe/', zalihe_list, name='zalihe-list'),
    path('zalihe/<int:zaliha_id>/', zaliha_detail, name='zaliha-detail'),
    path('zalihe/<int:zaliha_id>/izmeni/', izmeni_zalihu, name='izmeni-zalihu'),
    
    # Rizični artikli endpoint
    path('rizicni-artikli/', rizicni_artikli_list, name='rizicni-artikli-list'),
    
    # Statistike artikala endpoint
    path('artikli/statistike/', artikli_statistike, name='artikli-statistike'),
    
    # Grafikon artikala po nedeljama endpoint
    path('artikli/grafikon-po-nedeljama/', artikli_grafikon_po_nedeljama, name='artikli-grafikon-po-nedeljama'),
]
