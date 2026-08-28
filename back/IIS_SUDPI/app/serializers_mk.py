"""
Serijalajzeri podsistema finansijskog analitičara (FA).

Svaki serijalajzer ovde eksplicitno mapira nova imena polja iz models.py
(usklađena sa ER dijagramom) na STARE JSON ključeve koje front/ već čita -
preko `source=`. Time front/ ostaje nepromenjen, a šema ispod njega je
nova.
"""
from rest_framework import serializers
from datetime import date, timedelta

from .models import Faktura, Transakcija, Ugovor, StavkaFakture, Penal
from .serializers import DobavljacSerializer


class TransakcijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transakcija
        fields = ['sifra_t', 'datum_t', 'potvrda_t', 'status_t']


class UgovorSerializer(serializers.ModelSerializer):
    dobavljac = DobavljacSerializer(read_only=True)

    class Meta:
        model = Ugovor
        fields = ['sifra_u', 'datum_potpisa_u', 'datum_isteka_u', 'status_u', 'uslovi_u', 'dobavljac']


class StavkaFaktureSerializer(serializers.ModelSerializer):
    kolicina_sf = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    cena_po_jed = serializers.DecimalField(source='cena_po_jed_sf', max_digits=12, decimal_places=2, coerce_to_string=False, read_only=True)

    class Meta:
        model = StavkaFakture
        fields = ['sifra_sf', 'naziv_sf', 'kolicina_sf', 'cena_po_jed', 'opis_sf']


class FakturaSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv_db', read_only=True)
    dobavljac_id = serializers.IntegerField(source='ugovor.dobavljac.sifra_db', read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Faktura
        fields = [
            'sifra_f',
            'iznos_f',
            'datum_prijema_f',
            'rok_placanja_f',
            'status_f',
            'status_display',
            'dobavljac_naziv',
            'dobavljac_id'
        ]

    def get_status_display(self, obj):
        """Vraća čitljiv naziv statusa"""
        status_mapping = {
            'primljena': 'Čeka verifikaciju',
            'verifikovana': 'Čeka isplatu',
            'isplacena': 'Plaćeno',
            'odbijena': 'Odbačeno'
        }
        return status_mapping.get(obj.status_f, obj.status_f)


class FakturaDetailSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv_db', read_only=True)
    dobavljac_id = serializers.IntegerField(source='ugovor.dobavljac.sifra_db', read_only=True)
    status_display = serializers.SerializerMethodField()
    ugovor = UgovorSerializer(read_only=True)
    transakcija = serializers.SerializerMethodField()
    stavke = StavkaFaktureSerializer(many=True, read_only=True)
    process_steps = serializers.SerializerMethodField()

    class Meta:
        model = Faktura
        fields = [
            'sifra_f',
            'iznos_f',
            'datum_prijema_f',
            'rok_placanja_f',
            'status_f',
            'status_display',
            'razlog_cekanja_f',
            'dobavljac_naziv',
            'dobavljac_id',
            'ugovor',
            'transakcija',
            'stavke',
            'process_steps'
        ]

    def get_status_display(self, obj):
        status_mapping = {
            'primljena': 'Čeka verifikaciju',
            'verifikovana': 'Čeka isplatu',
            'isplacena': 'Plaćeno',
            'odbijena': 'Odbačeno'
        }
        return status_mapping.get(obj.status_f, obj.status_f)

    def get_transakcija(self, obj):
        """Faktura.transakcija je sada FK 1:N (poslednja transakcija čuva staru 1:1 semantiku)."""
        transakcija = obj.transakcija
        if transakcija is None:
            return None
        return TransakcijaSerializer(transakcija).data

    def get_process_steps(self, obj):
        """Generiše korake procesa na osnovu statusa fakture"""
        steps = [
            {
                'number': 1,
                'label': 'Prijem fakture',
                'status': 'completed'
            }
        ]

        if obj.status_f in ['verifikovana', 'isplacena']:
            steps.append({
                'number': 2,
                'label': 'Verifikacija',
                'status': 'completed'
            })
        elif obj.status_f == 'primljena':
            steps.append({
                'number': 2,
                'label': 'Verifikacija',
                'status': 'active'
            })
        elif obj.status_f == 'odbijena':
            steps.append({
                'number': 2,
                'label': 'Verifikacija',
                'status': 'rejected'
            })

        if obj.status_f == 'isplacena':
            steps.append({
                'number': 3,
                'label': 'Isplata',
                'status': 'completed'
            })
        elif obj.status_f in ['verifikovana']:
            steps.append({
                'number': 3,
                'label': 'Isplata',
                'status': 'active'
            })
        elif obj.status_f in ['primljena', 'odbijena']:
            steps.append({
                'number': 3,
                'label': 'Isplata',
                'status': 'upcoming'
            })

        return steps


class ReportDataSerializer(serializers.Serializer):
    proizvod = serializers.CharField()
    kolicina = serializers.CharField()
    ukupan_trosak = serializers.CharField()
    profitabilnost = serializers.CharField()


class ChartDataSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.FloatField()


class ReportsSerializer(serializers.Serializer):
    table_data = ReportDataSerializer(many=True)
    chart_profitability = ChartDataSerializer(many=True)
    chart_costs = ChartDataSerializer(many=True)
    total_summary = ReportDataSerializer()
    period_info = serializers.DictField()


class PenalSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv_db', read_only=True)
    ugovor_sifra = serializers.CharField(source='ugovor.sifra_u', read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Penal
        fields = [
            'sifra_p',
            'razlog_p',
            'iznos_p',
            'datum_p',
            'dobavljac_naziv',
            'ugovor_sifra',
            'status_display'
        ]

    def get_status_display(self, obj):
        """Generiše status na osnovu datuma i logike penala"""
        danas = date.today()
        if obj.datum_p < danas - timedelta(days=30):
            return 'Rešen'
        else:
            return 'Obavešten'


