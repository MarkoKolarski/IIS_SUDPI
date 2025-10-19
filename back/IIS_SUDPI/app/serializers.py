from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from .models import Faktura, Vozac, User, Dobavljac, Transakcija, Ugovor, Penal, StavkaFakture, Proizvod, Poseta, Reklamacija, Skladiste, Artikal, Zalihe, Popust, Temperatura, Notifikacija, Vozilo, Servis, Ruta, Isporuka, Upozorenje, voziloOmogucavaTemperatura, Izvestaj, Sertifikat, Rampa, TerminUtovara

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
        fields = ['sifra_d', 'naziv', 'email', 'PIB_d', 'ime_sirovine', 
                 'cena', 'rok_isporuke', 'ocena', 'datum_ocenjivanja', 'izabran']

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

class VisitSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='dobavljac.naziv', read_only=True)
    
    class Meta:
        model = Poseta
        fields = ['poseta_id', 'datum_od', 'datum_do', 'status', 'dobavljac', 'dobavljac_naziv']

class ComplaintSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.CharField(source='dobavljac.naziv', read_only=True)
    
    class Meta:
        model = Reklamacija
        fields = [
            'reklamacija_id',
            'datum_prijema',
            'status',
            'opis_problema',
            'vreme_trajanja',
            'jacina_zalbe',
            'dobavljac',
            'dobavljac_naziv'
        ]
        read_only_fields = ['reklamacija_id', 'datum_prijema', 'status']

# Serializers za skladište, artikal i zalihe
class SkladisteSerializer(serializers.ModelSerializer):
    poslednja_temperatura = serializers.SerializerMethodField()
    
    class Meta:
        model = Skladiste
        fields = ['sifra_s', 'mesto_s', 'status_rizika_s', 'poslednja_temperatura']
    
    def get_poslednja_temperatura(self, obj):
        """Vraća poslednju izmerenu temperaturu za skladište"""
        from .models import Temperatura
        
        poslednja_temp = Temperatura.objects.filter(
            skladiste=obj
        ).order_by('-vreme_merenja').first()
        
        if poslednja_temp:
            return float(poslednja_temp.vrednost)
        return None

class ArtikalSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Artikal
        fields = ['sifra_a', 'naziv_a', 'osnovna_cena_a', 'rok_trajanja_a', 'status_trajanja', 'status']
    
    def get_status(self, obj):
        """Mapira backend status na frontend status"""
        status_map = {
            'aktivan': 'ok',
            'istice': 'rizik', 
            'istekao': 'isteklo'
        }
        return status_map.get(obj.status_trajanja, 'ok')

class ZaliheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zalihe
        fields = ['trenutna_kolicina_a', 'datum_azuriranja', 'artikal', 'skladiste']

class DodajSkladisteSerializer(serializers.Serializer):
    mesto_s = serializers.CharField(max_length=200)
    status_rizika_s = serializers.ChoiceField(
        choices=[
            ('nizak', 'Nizak rizik'),
            ('umeren', 'Umeren rizik'),
            ('visok', 'Visok rizik')
        ]
    )
    
    def validate_mesto_s(self, value):
        if Skladiste.objects.filter(mesto_s=value).exists():
            raise serializers.ValidationError("Skladište sa ovim mestom već postoji.")
        return value
    
    def create(self, validated_data):
        # Automatski generiši šifru skladišta
        from django.db.models import Max
        max_sifra = Skladiste.objects.aggregate(Max('sifra_s'))['sifra_s__max'] or 0
        nova_sifra = max_sifra + 1
        
        skladiste = Skladiste.objects.create(
            sifra_s=nova_sifra,
            mesto_s=validated_data['mesto_s'],
            status_rizika_s=validated_data['status_rizika_s']
        )
        
        return skladiste

class DodajArtikalSerializer(serializers.Serializer):
    naziv_a = serializers.CharField(max_length=200)
    osnovna_cena_a = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    rok_trajanja_a = serializers.DateField()
    sifra_s = serializers.IntegerField(min_value=1)
    trenutna_kolicina_a = serializers.IntegerField(min_value=0)
    
    def validate_sifra_s(self, value):
        if not Skladiste.objects.filter(sifra_s=value).exists():
            raise serializers.ValidationError("Skladište sa ovom šifrom ne postoji.")
        return value
    
    def create(self, validated_data):
        from django.db import transaction
        
        with transaction.atomic():
            # Kreiranje artikla
            artikal = Artikal.objects.create(
                naziv_a=validated_data['naziv_a'],
                osnovna_cena_a=validated_data['osnovna_cena_a'],
                rok_trajanja_a=validated_data['rok_trajanja_a']
            )
            
            # Kreiranje zaliha
            skladiste = Skladiste.objects.get(sifra_s=validated_data['sifra_s'])
            zalihe = Zalihe.objects.create(
                artikal=artikal,
                skladiste=skladiste,
                trenutna_kolicina_a=validated_data['trenutna_kolicina_a']
            )
            
            return {
                'artikal': artikal,
                'zalihe': zalihe
            }

class RizicniArtikalSerializer(serializers.ModelSerializer):
    popust_cena = serializers.SerializerMethodField()
    dani_do_isteka = serializers.SerializerMethodField()
    
    class Meta:
        model = Artikal
        fields = ['sifra_a', 'naziv_a', 'osnovna_cena_a', 'rok_trajanja_a', 'status_trajanja', 'popust_cena', 'dani_do_isteka']
    
    def get_popust_cena(self, obj):
        """Vraća cenu sa popustom ako postoji aktivan popust"""
        from datetime import date
        from .models import Popust
        
        danas = date.today()
        aktivan_popust = Popust.objects.filter(
            artikli=obj,
            datum_pocetka_vazenja_p__lte=danas,
            datum_kraja_vazenja_p__gte=danas
        ).first()
        
        if aktivan_popust:
            return float(aktivan_popust.predlozena_cena_a)
        return None
    
    def get_dani_do_isteka(self, obj):
        """Računa broj dana do isteka roka trajanja"""
        from datetime import date
        danas = date.today()
        razlika = obj.rok_trajanja_a - danas
        return razlika.days

class TemperaturaSerializer(serializers.ModelSerializer):
    skladiste_info = serializers.CharField(source='skladiste.mesto_s', read_only=True)
    
    class Meta:
        model = Temperatura
        fields = '__all__'

class NotifikacijaSerializer(serializers.ModelSerializer):
    korisnik_info = serializers.CharField(source='korisnik.ime_k', read_only=True)
    
    class Meta:
        model = Notifikacija
        fields = '__all__'

class VoziloSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Vozilo
        fields = '__all__'

class ServisSerializer(serializers.ModelSerializer):
    vozilo_info = serializers.CharField(source='vozilo.registracija', read_only=True)
    vrsta_display = serializers.CharField(source='get_vrsta_display', read_only=True)
    vozilo_id = serializers.PrimaryKeyRelatedField(
        queryset=Vozilo.objects.all(), source='vozilo', write_only=True
    )
    class Meta:
        model = Servis
        fields = '__all__'

class RutaSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Ruta
        fields = '__all__'
    def get_vreme_putovanja_sati(self, obj):
        """Vraća vreme putovanja u satima kao decimalni broj"""
        return round(obj.vreme_dolaska.total_seconds() / 3600, 2)

    def get_vreme_putovanja_formatirano(self, obj):
        """Vraća formatirano vreme putovanja (npr. '2h 30min')"""
        total_seconds = obj.vreme_dolaska.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}min"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}min"
        
class VozacSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Vozac
        fields = '__all__'
        #fields = ['sifra_vo', 'ime_vo', 'prz_vo', 'br_voznji', 'status', 'status_display']

class IsporukaSerializer(serializers.ModelSerializer):
    ruta_info = serializers.CharField(source='ruta.polazna_tacka', read_only=True)
    vozilo_info = serializers.CharField(source='vozilo.registracija', read_only=True)
    vozac_info = serializers.CharField(source='vozac.ime_vo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    #ruta_info = RutaSerializer(source='ruta', read_only=True)
    #vozac_info = VozacSerializer(source='vozac', read_only=True)
    ruta = RutaSerializer(read_only=False)
    vozilo = VoziloSerializer(read_only=False)
    vozac = VozacSerializer(read_only=False)
    
    # vozac = serializers.StringRelatedField()

    # ruta_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ruta.objects.all(), source='ruta', write_only=True
    # )
    # vozilo_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Vozilo.objects.all(), source='vozilo', write_only=True
    # )
    class Meta:
        model = Isporuka
        fields = '__all__'

class UpozorenjeSerializer(serializers.ModelSerializer):
    #isporuka_info = serializers.CharField(source='isporuka.sifra_i', read_only=True)
    #tip_display = serializers.CharField(source='get_tip_display', read_only=True)
    isporuka = IsporukaSerializer(read_only=True)
    class Meta:
        model = Upozorenje
        fields = '__all__'

class VoziloOmogucavaTemperaturaSerializer(serializers.ModelSerializer):
    temperatura_info = serializers.CharField(source='sifra_temp.vrednost', read_only=True)
    vozilo_info = serializers.CharField(source='sifra_vozila.registracija', read_only=True)
    isporuka_info = serializers.CharField(source='isporuka.sifra_i', read_only=True)
    
    class Meta:
        model = voziloOmogucavaTemperatura
        fields = '__all__'

class IzvestajSerializer(serializers.ModelSerializer):
    kreirao_info = serializers.CharField(source='kreirao.ime', read_only=True)
    tip_i_display = serializers.CharField(source='get_tip_i_display', read_only=True)
    
    class Meta:
        model = Izvestaj
        fields = '__all__'

class SertifikatSerializer(serializers.ModelSerializer):
    dobavljac_naziv = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    
    class Meta:
        model = Sertifikat
        fields = ['sertifikat_id', 'naziv', 'tip', 'datum_izdavanja', 'datum_isteka', 
                 'dobavljac', 'dobavljac_naziv', 'days_left']
    
    def get_dobavljac_naziv(self, obj):
        return obj.dobavljac.naziv if obj.dobavljac else None
    
    def get_days_left(self, obj):
        today = timezone.now().date()
        return (obj.datum_isteka - today).days if obj.datum_isteka > today else 0



class IzvestajSerializer(serializers.ModelSerializer):
    class Meta:
        model = Izvestaj
        fields = ['sifra_i', 'datum_i', 'tip_i', 'sadrzaj_i', 'kreirao', 'pdf_file']
        read_only_fields = ['sifra_i', 'datum_i']
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password_confirm = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = get_user_model()
        #fields = ['ime_k', 'prz_k', 'mail_k', 'password', 'tip_k']
        #model = User
        fields = ['sifra_k', 'ime_k', 'prz_k', 'mail_k', 'tip_k', 'password', 'password_confirm']
        read_only_fields = ['sifra_k']

    def validate(self, data):
        if 'mail_k' in data:
            if User.objects.filter(mail_k=data['mail_k']).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"mail_k": "Email adresa se već koristi"})
        if data.get('password') and data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Lozinke se ne poklapaju"})
        return data

    def update(self, instance, validated_data):
        """Ažurira samo polja koja su prosleđena i hešira lozinku ako postoji"""
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)

        # Samo ažuriraj prosleđena polja
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
    
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer za prikaz korisničkog profila"""
    tip_k_display = serializers.CharField(source='get_tip_k_display', read_only=True)
    #password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    #confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        #model = User
        model = get_user_model()
        fields = ['sifra_k', 'ime_k', 'prz_k', 'mail_k', 'tip_k', 'tip_k_display']
        read_only_fields = ['sifra_k']

class RampaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rampa
        fields = '__all__'

class TerminUtovaraSerializer(serializers.ModelSerializer):
    skladiste = SkladisteSerializer(read_only=True)
    rampa = RampaSerializer(read_only=True)
    vozilo = VoziloSerializer(read_only=True)
    #operater = SkladisniOperaterSerializer(read_only=True)
    
    class Meta:
        model = TerminUtovara
        fields = '__all__'