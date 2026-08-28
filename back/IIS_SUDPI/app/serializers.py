from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from .models import (
    Vozac, User, Dobavljac, Poseta, Reklamacija, Skladiste, Artikal, Zalihe,
    Popust, Temperatura, Notifikacija, Vozilo, Servis, Ruta, Isporuka,
    Upozorenje, voziloOmogucavaTemperatura, Izvestaj, Sertifikat,
)


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
    """Deljeni entitet - JSON ključevi ostaju stari, model polja su usklađena sa ER (DOBAVLJAC)."""
    sifra_d = serializers.IntegerField(source='sifra_db', read_only=True)
    naziv = serializers.CharField(source='naziv_db', max_length=150)
    email = serializers.EmailField(source='email_db', max_length=100)
    PIB_d = serializers.CharField(source='pib_db', max_length=20)
    ocena = serializers.DecimalField(source='ocena_db', max_digits=3, decimal_places=1)

    class Meta:
        model = Dobavljac
        fields = ['sifra_d', 'naziv', 'email', 'PIB_d', 'ime_sirovine',
                 'cena', 'rok_isporuke', 'ocena', 'datum_ocenjivanja', 'izabran']


class VisitSerializer(serializers.ModelSerializer):
    """Deljeni entitet - JSON ključevi ostaju stari, model polja su usklađena sa ER (POSETA)."""
    poseta_id = serializers.IntegerField(source='sifra_po', read_only=True)
    datum_od = serializers.DateTimeField(source='datum_od_po')
    datum_do = serializers.DateTimeField(source='datum_do_po', required=False, allow_null=True)
    status = serializers.CharField(source='status_po', required=False)
    dobavljac_naziv = serializers.CharField(source='dobavljac.naziv_db', read_only=True)

    class Meta:
        model = Poseta
        fields = ['poseta_id', 'datum_od', 'datum_do', 'status', 'dobavljac', 'dobavljac_naziv']


class ComplaintSerializer(serializers.ModelSerializer):
    """Deljeni entitet - JSON ključevi ostaju stari, model polja su usklađena sa ER (REKLAMACIJA)."""
    reklamacija_id = serializers.IntegerField(source='sifra_r', read_only=True)
    datum_prijema = serializers.DateField(source='datum_prijema_r', read_only=True)
    status = serializers.CharField(source='status_r', read_only=True)
    opis_problema = serializers.CharField(source='opis_problema_r')
    vreme_trajanja = serializers.IntegerField(source='vreme_trajanja_r')
    jacina_zalbe = serializers.IntegerField(source='jacina_zalbe_r')
    dobavljac_naziv = serializers.CharField(source='dobavljac.naziv_db', read_only=True)

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


# Serializers za skladište, artikal i zalihe
class SkladisteSerializer(serializers.ModelSerializer):
    sifra_s = serializers.IntegerField(source='sifra_sk', read_only=True)
    mesto_s = serializers.CharField(source='mesto_sk', max_length=150)
    status_rizika_s = serializers.CharField(source='status_rizika_sk')
    poslednja_temperatura = serializers.SerializerMethodField()

    class Meta:
        model = Skladiste
        fields = ['sifra_s', 'mesto_s', 'status_rizika_s', 'poslednja_temperatura']

    def get_poslednja_temperatura(self, obj):
        """Vraća poslednju izmerenu temperaturu za skladište"""
        poslednja_temp = Temperatura.objects.filter(
            skladiste=obj
        ).order_by('-vreme_merenja_tp').first()

        if poslednja_temp:
            return float(poslednja_temp.vrednost_tp)
        return None


class ArtikalSerializer(serializers.ModelSerializer):
    status_trajanja = serializers.CharField(source='status_trajanja_a', read_only=True)
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
        return status_map.get(obj.status_trajanja_a, 'ok')


class ZaliheSerializer(serializers.ModelSerializer):
    trenutna_kolicina_a = serializers.DecimalField(source='trenutna_kol_z', max_digits=12, decimal_places=2, coerce_to_string=False)
    datum_azuriranja = serializers.DateTimeField(source='datum_azuriranja_z', read_only=True)

    class Meta:
        model = Zalihe
        fields = ['trenutna_kolicina_a', 'datum_azuriranja', 'artikal', 'skladiste']


class DodajSkladisteSerializer(serializers.Serializer):
    mesto_s = serializers.CharField(max_length=150)
    status_rizika_s = serializers.ChoiceField(
        choices=[
            ('nizak', 'Nizak rizik'),
            ('umeren', 'Umeren rizik'),
            ('visok', 'Visok rizik')
        ]
    )

    def validate_mesto_s(self, value):
        if Skladiste.objects.filter(mesto_sk=value).exists():
            raise serializers.ValidationError("Skladište sa ovim mestom već postoji.")
        return value

    def create(self, validated_data):
        # Automatski generiši šifru skladišta
        from django.db.models import Max
        max_sifra = Skladiste.objects.aggregate(Max('sifra_sk'))['sifra_sk__max'] or 0
        nova_sifra = max_sifra + 1

        skladiste = Skladiste.objects.create(
            sifra_sk=nova_sifra,
            mesto_sk=validated_data['mesto_s'],
            status_rizika_sk=validated_data['status_rizika_s']
        )

        return skladiste


class DodajArtikalSerializer(serializers.Serializer):
    naziv_a = serializers.CharField(max_length=150)
    osnovna_cena_a = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    rok_trajanja_a = serializers.DateField()
    sifra_s = serializers.IntegerField(min_value=1)
    trenutna_kolicina_a = serializers.IntegerField(min_value=0)

    def validate_sifra_s(self, value):
        if not Skladiste.objects.filter(sifra_sk=value).exists():
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
            skladiste = Skladiste.objects.get(sifra_sk=validated_data['sifra_s'])
            zalihe = Zalihe.objects.create(
                artikal=artikal,
                skladiste=skladiste,
                trenutna_kol_z=validated_data['trenutna_kolicina_a']
            )

            return {
                'artikal': artikal,
                'zalihe': zalihe
            }


class RizicniArtikalSerializer(serializers.ModelSerializer):
    status_trajanja = serializers.CharField(source='status_trajanja_a', read_only=True)
    popust_cena = serializers.SerializerMethodField()
    dani_do_isteka = serializers.SerializerMethodField()

    class Meta:
        model = Artikal
        fields = ['sifra_a', 'naziv_a', 'osnovna_cena_a', 'rok_trajanja_a', 'status_trajanja', 'popust_cena', 'dani_do_isteka']

    def get_popust_cena(self, obj):
        """Vraća cenu sa popustom ako postoji aktivan popust"""
        from datetime import date

        danas = date.today()
        aktivan_popust = Popust.objects.filter(
            artikli=obj,
            datum_poc_vaz_pop__lte=danas,
            datum_kr_vaz_pop__gte=danas
        ).first()

        if aktivan_popust:
            return float(aktivan_popust.pred_cena_pop)
        return None

    def get_dani_do_isteka(self, obj):
        """Računa broj dana do isteka roka trajanja"""
        from datetime import date
        danas = date.today()
        razlika = obj.rok_trajanja_a - danas
        return razlika.days


class TemperaturaSerializer(serializers.ModelSerializer):
    id_merenja = serializers.IntegerField(source='sifra_tm', read_only=True)
    vrednost = serializers.DecimalField(source='vrednost_tp', max_digits=5, decimal_places=2)
    vreme_merenja = serializers.DateTimeField(source='vreme_merenja_tp', read_only=True)
    skladiste_info = serializers.CharField(source='skladiste.mesto_sk', read_only=True)

    class Meta:
        model = Temperatura
        fields = ['id_merenja', 'vrednost', 'vreme_merenja', 'skladiste', 'skladiste_info']


class NotifikacijaSerializer(serializers.ModelSerializer):
    """Notifikacija <-> Korisnik je M:N u ER-u (se_šalje); JSON i dalje vraća pojedinačnog korisnika."""
    korisnik = serializers.SerializerMethodField()
    korisnik_info = serializers.SerializerMethodField()

    class Meta:
        model = Notifikacija
        fields = ['sifra_n', 'poruka_n', 'datum_n', 'procitana_n', 'link_n', 'korisnik', 'korisnik_info']

    def get_korisnik(self, obj):
        prvi_korisnik = obj.korisnik
        return prvi_korisnik.sifra_k if prvi_korisnik else None

    def get_korisnik_info(self, obj):
        prvi_korisnik = obj.korisnik
        return prvi_korisnik.ime_k if prvi_korisnik else None


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

class IsporukaSerializer(serializers.ModelSerializer):
    ruta_info = serializers.CharField(source='ruta.polazna_tacka', read_only=True)
    vozilo_info = serializers.CharField(source='vozilo.registracija', read_only=True)
    vozac_info = serializers.CharField(source='vozac.ime_vo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ruta = RutaSerializer(read_only=False)
    vozilo = VoziloSerializer(read_only=False)
    vozac = VozacSerializer(read_only=False)

    class Meta:
        model = Isporuka
        fields = '__all__'

class UpozorenjeSerializer(serializers.ModelSerializer):
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


class SertifikatSerializer(serializers.ModelSerializer):
    sertifikat_id = serializers.IntegerField(source='sifra_s', read_only=True)
    naziv = serializers.CharField(source='naziv_s', max_length=150)
    tip = serializers.CharField(source='tip_s')
    datum_izdavanja = serializers.DateField(source='datum_izdavanja_s')
    datum_isteka = serializers.DateField(source='datum_isteka_s')
    dobavljac_naziv = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Sertifikat
        fields = ['sertifikat_id', 'naziv', 'tip', 'datum_izdavanja', 'datum_isteka',
                 'dobavljac', 'dobavljac_naziv', 'days_left']

    def get_dobavljac_naziv(self, obj):
        return obj.dobavljac.naziv_db if obj.dobavljac else None

    def get_days_left(self, obj):
        today = timezone.now().date()
        return (obj.datum_isteka_s - today).days if obj.datum_isteka_s > today else 0


class IzvestajSerializer(serializers.ModelSerializer):
    """Generički upload izveštaja (van FA modula, trenutno nekorišćen od strane front/).
    Izvestaj sadržaj je sada relacioni (PredmetIzvestaja/Merenje), ne JSON blob -
    ovaj serijalajzer samo upisuje osnovni zapis + PDF, vezan na postojeći Kreiranje par."""
    pdf_file = serializers.FileField(source='pdf_fajl', required=False, allow_null=True)

    class Meta:
        model = Izvestaj
        fields = ['sifra_i', 'datum_i', 'tip_i', 'period_od_i', 'period_do_i', 'kreiranje', 'pdf_file']
        read_only_fields = ['sifra_i', 'datum_i']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password_confirm = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = get_user_model()
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

    class Meta:
        model = get_user_model()
        fields = ['sifra_k', 'ime_k', 'prz_k', 'mail_k', 'tip_k', 'tip_k_display']
        read_only_fields = ['sifra_k']
