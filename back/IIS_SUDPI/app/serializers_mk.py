"""
Serijalajzeri podsistema finansijskog analitičara (FA) - DTO sloj.

"""
from rest_framework import serializers
from datetime import date, timedelta

from .constants_mk import (
    PENAL_DANI_DO_RESENJA, PENAL_STATUS_OBAVESTEN, PENAL_STATUS_RESEN,
    STATUS_FAKTURE_PRIKAZ,
)
from .models import Faktura, Transakcija, Ugovor, StavkaFakture, Penal
from .serializers import DobavljacSerializer


# ========== ULAZNI DTO (validacija zahteva) ==========

class InvoiceActionSerializer(serializers.Serializer):
    """Telo POST /invoices/<id>/action/ zahteva.

    Zamenjuje ručno čitanje `request.data.get('action')` u view-u: dozvoljene
    akcije su deklarisane kao domen, a poslovno pravilo "odbacivanje mora imati
    razlog" se proverava ovde, a ne usred orkestracije.
    """
    ACTION_CHOICES = (
        ('approve', 'Verifikuj'),
        ('reject', 'Odbaci'),
    )

    action = serializers.ChoiceField(
        choices=ACTION_CHOICES,
        error_messages={
            'invalid_choice': 'Nevalidna akcija.',
            'required': 'Nevalidna akcija.',
            'null': 'Nevalidna akcija.',
        },
    )
    # razlog se upisuje u PromenaStatusa.razlog_ps (max_length=500)
    reason = serializers.CharField(
        max_length=500, required=False, allow_blank=True, trim_whitespace=True
    )

    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('reason'):
            raise serializers.ValidationError('Razlog odbacivanja je obavezan.')
        return attrs


# ========== IZLAZNI DTO (oblik odgovora) ==========

class TransakcijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transakcija
        fields = ['sifra_t', 'datum_t', 'broj_potvrde_t', 'status_t']


class UgovorSerializer(serializers.ModelSerializer):
    dobavljac = DobavljacSerializer(read_only=True)

    class Meta:
        model = Ugovor
        fields = ['sifra_u', 'datum_potpisa_u', 'datum_isteka_u', 'status_u', 'uslovi_u', 'dobavljac']


class StavkaFaktureSerializer(serializers.ModelSerializer):
    kolicina_sf = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    cena_po_jed_sf = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False, read_only=True)

    class Meta:
        model = StavkaFakture
        fields = ['sifra_sf', 'naziv_sf', 'kolicina_sf', 'cena_po_jed_sf', 'opis_sf']


class FakturaSerializer(serializers.ModelSerializer):
    naziv_db = serializers.CharField(source='ugovor.dobavljac.naziv_db', read_only=True)
    sifra_db = serializers.IntegerField(source='ugovor.dobavljac.sifra_db', read_only=True)
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
            'naziv_db',
            'sifra_db'
        ]

    def get_status_display(self, obj):
        """Vraća čitljiv naziv statusa"""
        return STATUS_FAKTURE_PRIKAZ.get(obj.status_f, obj.status_f)


class FakturaDetailSerializer(serializers.ModelSerializer):
    naziv_db = serializers.CharField(source='ugovor.dobavljac.naziv_db', read_only=True)
    sifra_db = serializers.IntegerField(source='ugovor.dobavljac.sifra_db', read_only=True)
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
            'naziv_db',
            'sifra_db',
            'ugovor',
            'transakcija',
            'stavke',
            'process_steps'
        ]

    def get_status_display(self, obj):
        return STATUS_FAKTURE_PRIKAZ.get(obj.status_f, obj.status_f)

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


class InvoiceActionResultSerializer(serializers.Serializer):
    """Odgovor POST /invoices/<id>/action/ - raw šifre statusa (Django
    konvencija status_display je rezervisana za get_FOO_display() prikaz)."""
    poruka = serializers.CharField()
    status_f = serializers.CharField()
    status_t = serializers.CharField(required=False, allow_null=True)


class SimTransakcijaSerializer(serializers.Serializer):
    """Transakcija u odgovoru simulacije plaćanja - status_display ovde je
    stvarno get_status_t_display() (čitljiv naziv), ne šifra."""
    sifra_t = serializers.IntegerField()
    broj_potvrde_t = serializers.CharField()
    status_display = serializers.CharField()
    datum_t = serializers.CharField()
    iznos_t = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)


class SimFakturaSerializer(serializers.Serializer):
    sifra_f = serializers.IntegerField()
    status_display = serializers.CharField()
    naziv_db = serializers.CharField()


class NotifikacijeSimulacijeSerializer(serializers.Serializer):
    """Nije vezano za entitet Notifikacija (van FA EER-a, vidi CLAUDE.md
    odstupanje #2) - samo status slanja email obaveštenja tokom simulacije."""
    obavestenje_poslato = serializers.BooleanField()
    potvrda_poslata = serializers.BooleanField()
    primalac = serializers.EmailField()


class SimulacijaPlacanjaSerializer(serializers.Serializer):
    """Odgovor POST /invoices/<id>/simulate-payment/."""
    uspesno = serializers.BooleanField()
    poruka = serializers.CharField()
    transakcija = SimTransakcijaSerializer()
    faktura = SimFakturaSerializer()
    notifikacije = NotifikacijeSimulacijeSerializer()


# ========== DASHBOARD ==========

class PregledFinansijaSerializer(serializers.Serializer):
    ukupno_placeno = serializers.FloatField()
    na_cekanju = serializers.FloatField()
    prosecno_vreme_placanja = serializers.IntegerField()
    broj_faktura_na_cekanju = serializers.IntegerField()
    udeo_na_cekanju = serializers.FloatField()


class ProfitabilnostDobavljacaSerializer(serializers.Serializer):
    naziv_db = serializers.CharField()
    profitabilnost = serializers.FloatField()


class NadolazecaIsplataSerializer(serializers.Serializer):
    sifra_f = serializers.IntegerField()
    naziv_db = serializers.CharField()
    iznos_f = serializers.FloatField()


class TroskovMesecaSerializer(serializers.Serializer):
    mesec = serializers.CharField()
    iznos = serializers.FloatField()


class ChartWindowSerializer(serializers.Serializer):
    offset = serializers.IntegerField()
    window_start = serializers.CharField()
    window_end = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    pregled_finansija = PregledFinansijaSerializer()
    profitabilnost_dobavljaca = ProfitabilnostDobavljacaSerializer(many=True)
    nadolazece_isplate = NadolazecaIsplataSerializer(many=True)
    vizualizacija_troskova = TroskovMesecaSerializer(many=True)
    chart_window = ChartWindowSerializer()


class TrendTroskovaSerializer(serializers.Serializer):
    """Odgovor GET /dashboard-fa/costs-trend/."""
    offset = serializers.IntegerField()
    limit = serializers.IntegerField()
    window_start = serializers.CharField()
    window_end = serializers.CharField()
    vizualizacija_troskova = TroskovMesecaSerializer(many=True)


# ========== IZVEŠTAJI ==========

class StavkaIzvestajaSerializer(serializers.Serializer):
    """Jedan red izveštaja (proizvod/dobavljač/kategorija, zavisno od
    group_by parametra) - nije vezan za jedan model, već za agregat."""
    naziv = serializers.CharField()
    kolicina = serializers.IntegerField()
    ukupan_trosak = serializers.DecimalField(max_digits=14, decimal_places=2, coerce_to_string=False)
    profitabilnost = serializers.FloatField()


class GrafikStavkaSerializer(serializers.Serializer):
    naziv = serializers.CharField()
    vrednost = serializers.FloatField()


class GrafikoniIzvestajaSerializer(serializers.Serializer):
    profitabilnost = GrafikStavkaSerializer(many=True)
    troskovi = GrafikStavkaSerializer(many=True)


class IzvestajTroskovaSerializer(serializers.Serializer):
    """Odgovor GET /reports/."""
    ukupna_profitabilnost = serializers.FloatField()
    ukupan_trosak = serializers.FloatField()
    ukupna_kolicina = serializers.IntegerField()
    stavke = StavkaIzvestajaSerializer(many=True)
    grafikoni = GrafikoniIzvestajaSerializer()


class PenalSerializer(serializers.ModelSerializer):
    naziv_db = serializers.CharField(source='ugovor.dobavljac.naziv_db', read_only=True)
    sifra_u = serializers.IntegerField(source='ugovor.sifra_u', read_only=True)
    iznos_p = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False, read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Penal
        fields = [
            'sifra_p',
            'razlog_p',
            'iznos_p',
            'datum_p',
            'naziv_db',
            'sifra_u',
            'status_display'
        ]

    def get_status_display(self, obj):
        """Status penala nije kolona - izvodi se iz starosti zapisa. Isti prag
        (`PENAL_DANI_DO_RESENJA`) koristi i filter u `penalties_list`."""
        prag = date.today() - timedelta(days=PENAL_DANI_DO_RESENJA)
        return PENAL_STATUS_RESEN if obj.datum_p < prag else PENAL_STATUS_OBAVESTEN


class AnalizaDobavljacaSerializer(serializers.Serializer):
    """Jedan red automatske analize saradnje (GET /penalties/analysis/).

    Nije vezan za model - view agregira po dobavljaču pa ovaj DTO samo
    deklariše oblik i tipove izlaza.
    """
    naziv_db = serializers.CharField()
    broj_penala = serializers.IntegerField()
    ukupno_ugovora = serializers.IntegerField()
    ugovori_sa_penalima = serializers.IntegerField()
    ukupan_iznos = serializers.DecimalField(max_digits=14, decimal_places=2, coerce_to_string=False)
    stopa_krsenja = serializers.FloatField()
    preporuka = serializers.CharField()
    tip_preporuke = serializers.CharField()


class KrsenjeUgovoraSerializer(serializers.Serializer):
    """Jedno detektovano kršenje ugovora (GET /penalties/check-violations/).

    `check_contract_violations()` vraća dict sa `Ugovor` instancom pod ključem
    'ugovor', pa se atributi ugovora čitaju kroz `source='ugovor....'`.
    """
    sifra_u = serializers.IntegerField(source='ugovor.sifra_u')
    naziv_db = serializers.CharField(source='ugovor.dobavljac.naziv_db')
    email_db = serializers.EmailField(source='ugovor.dobavljac.email_db')
    datum_potpisa_u = serializers.DateField(source='ugovor.datum_potpisa_u')
    datum_isteka_u = serializers.DateField(source='ugovor.datum_isteka_u')
    status_u = serializers.CharField(source='ugovor.status_u')
    tip_krsenja = serializers.CharField()
    razlog = serializers.CharField()
    iznos_penala = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    detalji = serializers.CharField()


class KreiraniPenalSerializer(serializers.Serializer):
    """Penal kreiran automatskom proverom (POST /penalties/auto-create/)."""
    sifra_p = serializers.IntegerField()
    sifra_u = serializers.IntegerField()
    naziv_db = serializers.CharField()
    tip_krsenja = serializers.CharField()
    iznos_p = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    razlog_p = serializers.CharField()


class GreskaKreiranjaPenalaSerializer(serializers.Serializer):
    """Ugovor za koji automatsko kreiranje penala nije uspelo."""
    sifra_u = serializers.IntegerField()
    naziv_db = serializers.CharField()
    greska = serializers.CharField()


class AutoKreiranjePenalaSerializer(serializers.Serializer):
    """Odgovor POST /penalties/auto-create/."""
    poruka = serializers.CharField()
    broj_krsenja = serializers.IntegerField()
    broj_kreiranih_penala = serializers.IntegerField()
    penali = KreiraniPenalSerializer(many=True)
    greske = GreskaKreiranjaPenalaSerializer(many=True)


