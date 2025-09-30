from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Faktura, Dobavljac, Transakcija, Ugovor, Penal, StavkaFakture, Proizvod

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = get_user_model()
        fields = ['ime_k', 'prz_k', 'mail_k', 'password', 'tip_k']

    def validate_mail_k(self, value):
        if get_user_model().objects.filter(mail_k=value).exists():
            raise serializers.ValidationError("Korisnik sa ovim email-om već postoji.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Lozinka mora imati najmanje 8 karaktera.")
        if value.isdigit():
            raise serializers.ValidationError("Lozinka ne može biti samo numerička.")
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['mail_k'],
            ime_k=validated_data['ime_k'],
            prz_k=validated_data['prz_k'],
            mail_k=validated_data['mail_k'],
            password=validated_data['password'],
            tip_k=validated_data['tip_k']
        )
        return user

class DobavljacSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dobavljac
        fields = ['sifra_d', 'naziv']

class FakturaSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv', read_only=True)
    dobavljac_id = serializers.IntegerField(source='ugovor.dobavljac.sifra_d', read_only=True)
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
            'primljena': 'Primljeno',
            'verifikovana': 'Čeka verifikaciju',
            'isplacena': 'Plaćeno',
            'odbijena': 'Odbačeno'
        }
        return status_mapping.get(obj.status_f, obj.status_f)

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
    class Meta:
        model = StavkaFakture
        fields = ['sifra_sf', 'naziv_sf', 'kolicina_sf', 'cena_po_jed', 'opis_sf']

class FakturaDetailSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv', read_only=True)
    dobavljac_id = serializers.IntegerField(source='ugovor.dobavljac.sifra_d', read_only=True)
    status_display = serializers.SerializerMethodField()
    ugovor = UgovorSerializer(read_only=True)
    transakcija = TransakcijaSerializer(read_only=True)
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
        """Vraća čitljiv naziv statusa"""
        status_mapping = {
            'primljena': 'Primljeno',
            'verifikovana': 'Čeka verifikaciju',
            'isplacena': 'Plaćeno',
            'odbijena': 'Odbačeno'
        }
        return status_mapping.get(obj.status_f, obj.status_f)
    
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
    dobavljac_naziv = serializers.CharField(source='ugovor.dobavljac.naziv', read_only=True)
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
        # Za sada ću koristiti jednostavnu logiku - možeš proširiti po potrebi
        from datetime import date, timedelta
        
        danas = date.today()
        # Ako je penal stariji od 30 dana, smatra se rešenim
        if obj.datum_p < danas - timedelta(days=30):
            return 'Rešen'
        else:
            return 'Obavešten'