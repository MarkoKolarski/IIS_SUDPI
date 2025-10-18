from django.urls import path, include
from . import views
from . import views_mv
from .views_saga import create_faktura_with_payment_saga, create_penal_saga, saga_status
from .views import (LoginView, index, register, api_login, dashboard_finansijski_analiticar, invoice_list, 
                    invoice_filter_options, invoice_detail, invoice_action, reports_data, reports_filter_options, 
                    penalties_list, penalties_filter_options, penalties_analysis, check_and_create_penalties, 
                    preview_contract_violations, select_supplier, skladista_list, dodaj_skladiste, dodaj_artikal, 
                    artikli_list, obrisi_artikal, artikal_detail, izmeni_artikal, zalihe_list, zaliha_detail, 
                    izmeni_zalihu, rizicni_artikli_list, artikli_statistike, artikli_grafikon_po_nedeljama, 
                    simulate_payment)
from .views_mv import suppliers, expiring_certificates, visits_list, visit_detail, create_visit, busy_visit_slots, complaints_list, create_complaint
from .views_mv2 import (
    check_service_health, sync_suppliers, sync_complaints, sync_certificates, 
    get_supplier_report, get_supplier_comparison_report, get_material_suppliers_report, 
    create_complaint_with_rating, get_supplier_risk_analysis, get_alternative_suppliers,
    get_suppliers, get_material_suppliers_report_post, get_performance_trends_report,
    get_risk_analysis_report, get_alternative_suppliers_post, get_supplier_performance_trends,
    get_material_market_dynamics, supplier_analysis_dashboard, supplier_complaint_transaction,
    upload_izvestaj
)
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings
#from .views import LoginView, index, register, dashboard_finansijski_analiticar, invoice_list, invoice_filter_options, invoice_detail, invoice_action, reports_data, reports_filter_options, penalties_list, penalties_filter_options, penalties_analysis, suppliers, visits_list, visit_detail, create_visit, complaints_list, create_complaint, select_supplier, skladista_list, dodaj_skladiste, dodaj_artikal, artikli_list, obrisi_artikal, artikal_detail, izmeni_artikal, zalihe_list, zaliha_detail, izmeni_zalihu, rizicni_artikli_list, artikli_statistike, artikli_grafikon_po_nedeljama
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/login/', api_login, name='api-login'),  # API endpoint za JWT login
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
    path('expiring-certificates/', expiring_certificates, name='expiring_certificates'),

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


    # Supplier Analysis Dashboard
    path('supplier-analysis/', supplier_analysis_dashboard, name='supplier_analysis_dashboard'),
    path('supplier-complaint-transaction/', supplier_complaint_transaction, name='supplier_complaint_transaction'),

    # Supplier Analysis Microservice integration
    path('api/supplier-analysis/health/', check_service_health, name='supplier_analysis_health'),
    path('api/supplier-analysis/sync/suppliers/', sync_suppliers, name='sync_suppliers'),
    path('api/supplier-analysis/sync/complaints/', sync_complaints, name='sync_complaints'),
    path('api/supplier-analysis/sync/certificates/', sync_certificates, name='sync_certificates'),
    path('api/supplier-analysis/reports/supplier/<int:supplier_id>/', get_supplier_report, name='supplier_report'),
    path('api/supplier-analysis/reports/supplier-comparison/', get_supplier_comparison_report, name='supplier_comparison_report'),
    path('api/supplier-analysis/reports/material/<str:material_name>/', get_material_suppliers_report, name='material_suppliers_report'),
    path('api/supplier-analysis/reports/material/', get_material_suppliers_report_post, name='material_suppliers_report_post'),
    path('api/supplier-analysis/reports/performance-trends/', get_performance_trends_report, name='performance_trends_report'),
    path('api/supplier-analysis/reports/risk-analysis/', get_risk_analysis_report, name='risk_analysis_report'),
    path('api/supplier-analysis/complaints/create/', create_complaint_with_rating, name='create_complaint_with_rating'),
    path('api/supplier-analysis/risk-analysis/', get_supplier_risk_analysis, name='supplier_risk_analysis'),
    path('api/supplier-analysis/alternative-suppliers/<str:material_name>/', get_alternative_suppliers, name='alternative_suppliers'),
    path('api/supplier-analysis/analysis/alternative-suppliers/', get_alternative_suppliers_post, name='alternative_suppliers_post'),
    path('api/supplier-analysis/analysis/supplier-performance-trends/', get_supplier_performance_trends, name='supplier_performance_trends'),
    path('api/supplier-analysis/analysis/material-market-dynamics/', get_material_market_dynamics, name='material_market_dynamics'),
    path('api/supplier-analysis/suppliers/', get_suppliers, name='get_suppliers'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('api/izvestaji/upload/', upload_izvestaj, name='izvestaj-upload'),

    # Profil trenutnog korisnika
    path('api/user/profile/', views.get_user_profile, name='get_user_profile'),
    path('api/user/profile/update/', views.update_user_profile, name='update_user_profile'),
    
    # Profil određenog korisnika (samo admin)
    path('api/user/profile/<int:user_id>/', views.get_user_profile_by_id, name='get_user_profile_by_id'),
    path('api/user/profile/update/<int:user_id>/', views.update_user_profile, name='update_user_profile_by_id'),
    
    # Lista svih korisnika (samo admin)
    path('api/users/', views.get_users_list, name='get_users_list'),

    # Lista svih vozaca i vozila (samo admin)
    path('api/vozila/', views.vozila_list, name='vozila_list'),
    path('api/vozaci/', views.vozaci_list, name='vozaci_list'),

    # Vozila
    path('vozila/<int:pk>/', views.get_vozilo, name='get_vozilo'),
    path('vozila/update/<int:pk>/', views.update_vozilo, name='update_vozilo'),
    path('vozila/delete/<int:pk>/', views.delete_vozilo, name='delete_vozilo'),
    path('vozila/<int:vozilo_id>/servisi/', views.servisi_po_vozilu, name='servisi_po_vozilu'),

    # Servisi
    path('servisi/', views.list_servisi, name='list_servisi'),
    path('servisi/<int:pk>/', views.get_servis, name='get_servis'),
    path('servisi/create/', views.create_servis, name='create_servis'),
    path('servisi/update/<int:pk>/', views.update_servis, name='update_servis'),
    path('servisi/delete/<int:pk>/', views.delete_servis, name='delete_servis'),

    # Vozac update_status_vozaca
    path('vozaci/update-status/<int:pk>/', views.update_status_vozaca, name='update_status_vozaca'),
    #path('vozaci/predlozi-vozaca/', views.predlozi_vozaca, name='predlozi_vozaca'),
    # Isporuke
    path('isporuke/', views.list_isporuke, name='list_isporuke'),
    path('isporuke/aktivne/', views.list_aktivne_isporuke, name='list_aktivne_isporuke'),
    path('isporuke/debug/', views.debug_sve_isporuke, name='debug_sve_isporuke'),
    path('isporuke/u_toku/', views.list_u_toku_isporuke, name='list_utoku_isporuke'),
    # notifikacije
    path('notifikacije/', views.list_notifikacije, name='list_notifikacije'),
    path('notifikacije/<int:pk>/mark-as-read/', views.mark_notifikacija_as_read, name='mark_notifikacija_as_read'),
    path('notifikacije/user/<int:user_id>/', views.list_user_notifikacije, name='list_user_notifikacije'),

     # Plan isporuke endpoints
    path('api/predlozi-vozaca/', views.predlozi_vozaca, name='predlozi_vozaca'),
    path('api/predlozi-vozilo/', views.predlozi_vozilo, name='predlozi_vozilo'),
    path('api/predlozi-rutu/', views.predlozi_rutu, name='predlozi_rutu'),
    path('api/kreiraj-isporuku/<int:pk>', views.kreiraj_isporuku, name='kreiraj_isporuku'),
    path('api/izracunaj-datum-dolaska/', views.izracunaj_datum_dolaska, name='izracunaj_datum_dolaska'),
    #path('api/isporuke/<int:pk>/', views.isporuka_detail, name='isporuka_detail'),
    #path('api/isporuke/<int:isporuka_id>/zavrsi/', views.zavrsi_isporuku, name='zavrsi_isporuku'),

    # endpoints za rute
    path('api/rute/', views.list_rute, name='list_rute'),
    path('api/rute/aktivne/', views.list_aktivne_rute, name='list_aktivne_rute'),
    path('api/rute/<int:pk>/', views.ruta_detail, name='ruta_detail'),
    path('api/rute/<int:pk>/directions/', views.ruta_directions, name='ruta_directions'),
    path('api/rute/<int:pk>/map-preview/', views.ruta_map_preview, name='ruta_map_preview'),
    #upozorenja
    path('api/upozorenja/', views.list_upozorenja, name='list_upozorenja'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
