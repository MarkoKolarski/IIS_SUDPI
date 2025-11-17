from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, datetime

# Model za korisnika - centralni entitet
class User(AbstractUser):
    USER_TYPES = (
        ('logisticki_koordinator', 'Logistički koordinator'),
        ('skladisni_operater', 'Skladišni operater'),
        ('nabavni_menadzer', 'Nabavni menadžer'),
        ('finansijski_analiticar', 'Finansijski analitičar'),
        ('kontrolor_kvaliteta', 'Kontrolor kvaliteta'),
        ('administrator', 'Administrator'),
    )
    
    # Atributi prema ER dijagramu
    sifra_k = models.AutoField(primary_key=True)
    ime_k = models.CharField(max_length=100)
    prz_k = models.CharField(max_length=100)
    mail_k = models.EmailField(unique=True)
    tip_k = models.CharField(max_length=30, choices=USER_TYPES)

    # Koristi email kao username za autentifikaciju
    USERNAME_FIELD = 'mail_k'
    REQUIRED_FIELDS = ['ime_k', 'prz_k', 'tip_k']

    class Meta:
        db_table = 'korisnik'

    @property
    def id(self):
        return self.sifra_k

    def __str__(self):
        return f"{self.ime_k} {self.prz_k} ({self.get_tip_k_display()})"

# Modeli za različite tipove korisnika
class Administrator(models.Model):
    korisnik = models.OneToOneField(User, on_delete=models.CASCADE, related_name="administrator")
    
    class Meta:
        db_table = 'administrator'
    
    def __str__(self):
        return f"Administrator: {self.korisnik.ime_k} {self.korisnik.prz_k}"


class LogistickiKoordinator(models.Model):
    korisnik = models.OneToOneField(User, on_delete=models.CASCADE, related_name="logisticki_koordinator")
    
    class Meta:
        db_table = 'logisticki_koordinator'
    
    def __str__(self):
        return f"Logistički koordinator: {self.korisnik.ime_k} {self.korisnik.prz_k}"

class SkladisniOperater(models.Model):
    korisnik = models.OneToOneField(User, on_delete=models.CASCADE, related_name="skladisni_operater")
    
    class Meta:
        db_table = 'skladisni_operater'
    
    def __str__(self):
        return f"Skladišni operater: {self.korisnik.ime_k} {self.korisnik.prz_k}"

class NabavniMenadzer(models.Model):
    korisnik = models.OneToOneField(User, on_delete=models.CASCADE, related_name="nabavni_menadzer")
    
    class Meta:
        db_table = 'nabavni_menadzer'
    
    def __str__(self):
        return f"Nabavni menadžer: {self.korisnik.ime_k} {self.korisnik.prz_k}"

class FinansijskiAnaliticar(models.Model):
    korisnik = models.OneToOneField(User, on_delete=models.CASCADE, related_name="finansijski_analiticar")
    
    class Meta:
        db_table = 'finansijski_analiticar'
    
    def __str__(self):
        return f"Finansijski analitičar: {self.korisnik.ime_k} {self.korisnik.prz_k}"

class KontrolorKvaliteta(models.Model):
    korisnik = models.OneToOneField(User, on_delete=models.CASCADE, related_name="kontrolor_kvaliteta")
    
    class Meta:
        db_table = 'kontrolor_kvaliteta'
    
    def __str__(self):
        return f"Kontrolor kvaliteta: {self.korisnik.ime_k} {self.korisnik.prz_k}"

# Model za skladište
class Skladiste(models.Model):
    RIZIK_CHOICES = (
        ('nizak', 'Nizak rizik'),
        ('umeren', 'Umeren rizik'),
        ('visok', 'Visok rizik'),
    )
    
    sifra_s = models.AutoField(primary_key=True)
    mesto_s = models.CharField(max_length=200)
    status_rizika_s = models.CharField(max_length=20, choices=RIZIK_CHOICES, default='nizak')
    
    class Meta:
        db_table = 'skladiste'
    
    def __str__(self):
        return f"Skladište {self.sifra_s} - {self.mesto_s}"

# Model za artikal
class Artikal(models.Model):
    STATUS_TRAJANJA_CHOICES = (
        ('aktivan', 'Aktivan'),
        ('istice', 'Uskoro ističe'),
        ('istekao', 'Istekao'),
    )
    
    sifra_a = models.AutoField(primary_key=True)
    naziv_a = models.CharField(max_length=200)
    osnovna_cena_a = models.DecimalField(max_digits=10, decimal_places=2)
    rok_trajanja_a = models.DateField()
    status_trajanja = models.CharField(max_length=20, choices=STATUS_TRAJANJA_CHOICES, default='aktivan')
    
    # Veza sa skladišnim operaterom (se_bavi - 0,N : 1,N)
    skladisni_operateri = models.ManyToManyField(SkladisniOperater, through='SeBavi', blank=True)
    
    class Meta:
        db_table = 'artikal'
    
    def __str__(self):
        return f"{self.naziv_a} ({self.sifra_a})"

# Model za zalihe
class Zalihe(models.Model):
    trenutna_kolicina_a = models.IntegerField(validators=[MinValueValidator(0)])
    datum_azuriranja = models.DateTimeField(auto_now=True)
    
    # Veze
    artikal = models.ForeignKey(Artikal, on_delete=models.CASCADE, related_name='zalihe')
    skladiste = models.ForeignKey(Skladiste, on_delete=models.CASCADE, related_name='zalihe')
    
    class Meta:
        db_table = 'zalihe'
        # Uklonjeno unique_together ograničenje
    
    def __str__(self):
        return f"Zalihe {self.artikal.naziv_a} u {self.skladiste.mesto_s}: {self.trenutna_kolicina_a}"

# Model za dobavljača
class Dobavljac(models.Model):
    sifra_d = models.AutoField(primary_key=True)
    naziv = models.CharField(max_length=200)
    email = models.EmailField()
    PIB_d = models.CharField(max_length=20, unique=True)
    ime_sirovine = models.CharField(max_length=200)
    cena = models.DecimalField(max_digits=10, decimal_places=2)
    rok_isporuke = models.IntegerField(help_text="Rok isporuke u danima")
    ocena = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))])
    datum_ocenjivanja = models.DateField()
    izabran = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'dobavljac'
    
    def __str__(self):
        return f"{self.naziv} - {self.ime_sirovine}"

# Intermedijarni model za vezu se_bavi (Skladišni operater ↔ Artikal)
class SeBavi(models.Model):
    skladisni_operater = models.ForeignKey(SkladisniOperater, on_delete=models.CASCADE)
    artikal = models.ForeignKey(Artikal, on_delete=models.CASCADE)
    datum_dodele = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'se_bavi'
        unique_together = ('skladisni_operater', 'artikal')
    
    def __str__(self):
        return f"{self.skladisni_operater} se bavi {self.artikal}"

class TerminUtovara(models.Model):
    sifra_tu = models.AutoField(primary_key=True)
    isporuka = models.OneToOneField('Isporuka', on_delete=models.CASCADE, related_name='termin_utovara')
    skladiste = models.ForeignKey('Skladiste', on_delete=models.CASCADE)
    vozilo = models.ForeignKey('Vozilo', on_delete=models.CASCADE)
    rampa = models.ForeignKey('Rampa', on_delete=models.CASCADE)
    operater = models.ForeignKey('SkladisniOperater', on_delete=models.SET_NULL, null=True)
    vreme_pocetka = models.DateTimeField()
    vreme_zavrsetka = models.DateTimeField()
    vreme_utovara = models.DurationField(help_text="Trajanje utovara u satima", null=True, blank=True)
    potvrda_operatera = models.BooleanField(default=False)

    class Meta:
        db_table = 'termin_utovara'
        #ordering = ['vreme_pocetka']

    def __str__(self):
        return f"Termin utovara {self.isporuka.sifra_i} ({self.vreme_pocetka.strftime('%d.%m.%Y %H:%M')})"

    def potvrdi_utovar(self):
        self.potvrda_operatera = True
        self.save()

    @staticmethod
    def predlozi_optimalan_termin(vozilo, isporuka):
        """
        Dinamički predlog optimalnog termina:
        - nalazi slobodnu rampu
        - proverava status vozila i osoblja
        """
        slobodne_rampe = Rampa.objects.filter(status='slobodna')
        slobodni_operateri = SkladisniOperater.objects.all()  # možeš dodati polje status kasnije

        if not slobodne_rampe.exists() or not slobodni_operateri.exists():
            return None

        rampa = slobodne_rampe.first()
        operater = slobodni_operateri.first()

        vreme_pocetka = timezone.now() + timedelta(hours=1)
        vreme_zavrsetka = vreme_pocetka + timedelta(hours=2)

        return TerminUtovara.objects.create(
            isporuka=isporuka,
            vozilo=vozilo,
            rampa=rampa,
            operater=operater,
            vreme_pocetka=vreme_pocetka,
            vreme_zavrsetka=vreme_zavrsetka,
        )
    
# Model za ugovor
class Ugovor(models.Model):
    STATUS_CHOICES = (
        ('aktivan', 'Aktivan'),
        ('istekao', 'Istekao'),
        ('otkazan', 'Otkazan'),
    )
    
    sifra_u = models.AutoField(primary_key=True)
    datum_potpisa_u = models.DateField()
    datum_isteka_u = models.DateField()
    status_u = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktivan')
    uslovi_u = models.TextField()
    
    # Veza sa dobavljačem (1,1 : 0,N)
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, related_name='ugovori')
    
    class Meta:
        db_table = 'ugovor'
    
    def __str__(self):
        return f"Ugovor {self.sifra_u} sa {self.dobavljac.naziv}"

# Model za fakturu
class Faktura(models.Model):
    STATUS_CHOICES = (
        ('primljena', 'Primljena'),
        ('verifikovana', 'Verifikovana'),
        ('isplacena', 'Isplaćena'),
        ('odbijena', 'Odbijena'),
    )
    
    sifra_f = models.AutoField(primary_key=True)
    iznos_f = models.DecimalField(max_digits=12, decimal_places=2)
    datum_prijema_f = models.DateField()
    rok_placanja_f = models.DateField()
    status_f = models.CharField(max_length=20, choices=STATUS_CHOICES, default='primljena')
    razlog_cekanja_f = models.TextField(blank=True, null=True)
    
    # Veza sa ugovorom (obuhvata - 1,1 : 0,N)
    ugovor = models.ForeignKey(Ugovor, on_delete=models.CASCADE, related_name='fakture')
    
    class Meta:
        db_table = 'faktura'
    
    def __str__(self):
        return f"Faktura {self.sifra_f} - {self.iznos_f} RSD"

# Model za transakciju
class Transakcija(models.Model):
    STATUS_CHOICES = (
        ('na_cekanju', 'Na čekanju'),
        ('uspesna', 'Uspešna'),
        ('neuspesna', 'Neuspešna'),
    )
    
    sifra_t = models.AutoField(primary_key=True)
    datum_t = models.DateTimeField(auto_now_add=True)
    potvrda_t = models.CharField(max_length=100, unique=True)
    status_t = models.CharField(max_length=20, choices=STATUS_CHOICES, default='na_cekanju')
    
    # Veza sa fakturom (ima_plaćanje - 0,N : 1,1)
    faktura = models.OneToOneField(Faktura, on_delete=models.CASCADE, related_name='transakcija')
    
    class Meta:
        db_table = 'transakcija'
    
    def __str__(self):
        return f"Transakcija {self.potvrda_t} za fakturu {self.faktura.sifra_f}"

# Model za penal
class Penal(models.Model):
    sifra_p = models.AutoField(primary_key=True)
    razlog_p = models.TextField()
    iznos_p = models.DecimalField(max_digits=10, decimal_places=2)
    datum_p = models.DateField(auto_now_add=True)
    
    # Veza sa ugovorom (generiše se iz - 0,N : 1,1)
    ugovor = models.ForeignKey(Ugovor, on_delete=models.CASCADE, related_name='penali')
    
    class Meta:
        db_table = 'penal'
    
    def __str__(self):
        return f"Penal {self.sifra_p} - {self.iznos_p} RSD"

# Model za kategoriju proizvoda
class KategorijaProizvoda(models.Model):
    sifra_kp = models.AutoField(primary_key=True)
    naziv_kp = models.CharField(max_length=200)
    limit_kp = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'kategorija_proizvoda'
    
    def __str__(self):
        return self.naziv_kp

# Model za proizvod
class Proizvod(models.Model):
    sifra_pr = models.AutoField(primary_key=True)
    naziv_pr = models.CharField(max_length=200)
    opis_pr = models.TextField()
    
    # Veza sa kategorijom (sadrži - 0,N : 1,1)
    kategorija = models.ForeignKey(KategorijaProizvoda, on_delete=models.CASCADE, related_name='proizvodi')
    
    class Meta:
        db_table = 'proizvod'
    
    def __str__(self):
        return self.naziv_pr

# Model za stavku fakture
class StavkaFakture(models.Model):
    sifra_sf = models.AutoField(primary_key=True)
    naziv_sf = models.CharField(max_length=200)
    kolicina_sf = models.IntegerField(validators=[MinValueValidator(1)])
    cena_po_jed = models.DecimalField(max_digits=10, decimal_places=2)
    opis_sf = models.TextField(blank=True)
    
    # Veze
    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE, related_name='stavke')
    proizvod = models.ForeignKey(Proizvod, on_delete=models.CASCADE, related_name='stavke_fakture')
    
    class Meta:
        db_table = 'stavka_fakture'
    
    def __str__(self):
        return f"Stavka {self.naziv_sf} - {self.kolicina_sf} x {self.cena_po_jed}"

# Model za sertifikat
class Sertifikat(models.Model):
    TIP_CHOICES = (
        ('ISO', 'ISO'),
        ('HACCP', 'HACCP'),
        ('GMP', 'GMP'),
        ('BRC', 'BRC'),
        ('IFS', 'IFS'),
        ('ostalo', 'Ostalo'),
    )
    
    sertifikat_id = models.AutoField(primary_key=True)
    naziv = models.CharField(max_length=200)
    tip = models.CharField(max_length=20, choices=TIP_CHOICES)
    datum_izdavanja = models.DateField()
    datum_isteka = models.DateField()
    
    # Veza sa dobavljačem (sertifikuje - 1,1 : 0,N)
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, related_name='sertifikati')
    
    class Meta:
        db_table = 'sertifikat'
    
    def __str__(self):
        return f"Sertifikat {self.naziv} ({self.tip}) - {self.dobavljac.naziv}"

# Model za posetu
class Poseta(models.Model):
    STATUS_CHOICES = (
        ('zakazana', 'Zakazana'),
        ('u_toku', 'U toku'),
        ('zavrsena', 'Završena'),
        ('otkazana', 'Otkazana'),
    )
    
    poseta_id = models.AutoField(primary_key=True)
    datum_od = models.DateTimeField()
    datum_do = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='zakazana')
    
    # Veze
    kontrolor = models.ForeignKey(KontrolorKvaliteta, on_delete=models.CASCADE, related_name='posete')
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, related_name='posete')
    
    class Meta:
        db_table = 'poseta'
    
    def __str__(self):
        return f"Poseta kod {self.dobavljac.naziv} - {self.datum_od.strftime('%d.%m.%Y')}"

# Model za reklamaciju
class Reklamacija(models.Model):
    STATUS_CHOICES = (
        ('prijem', 'Prijem'),
        ('analiza', 'Analiza'),
        ('odgovor', 'Odgovor'),
        ('zatvaranje', 'Zatvaranje'),
    )
    
    reklamacija_id = models.AutoField(primary_key=True)
    datum_prijema = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prijem')
    opis_problema = models.TextField()
    vreme_trajanja = models.IntegerField(help_text="Vreme trajanja u danima")
    jacina_zalbe = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Jačina žalbe na skali 1-10"
    )
    
    # Veze
    kontrolor = models.ForeignKey(KontrolorKvaliteta, on_delete=models.CASCADE, related_name='reklamacije')
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, related_name='reklamacije')
    
    class Meta:
        db_table = 'reklamacija'
    
    def __str__(self):
        return f"Reklamacija {self.reklamacija_id} protiv {self.dobavljac.naziv}"

# Model za dashboard
class Dashboard(models.Model):
    sifra_d = models.AutoField(primary_key=True)
    datum_d = models.DateTimeField(auto_now_add=True)
    
    # Veze prema ER dijagramu
    skladisni_operater = models.ForeignKey(SkladisniOperater, on_delete=models.SET_NULL, null=True, blank=True, related_name='dashboards')
    finansijski_analiticar = models.ForeignKey(FinansijskiAnaliticar, on_delete=models.SET_NULL, null=True, blank=True, related_name='dashboards')
    nabavni_menadzer = models.ForeignKey(NabavniMenadzer, on_delete=models.SET_NULL, null=True, blank=True, related_name='dashboards')
    
    class Meta:
        db_table = 'dashboard'
    
    def __str__(self):
        return f"Dashboard {self.sifra_d} - {self.datum_d.strftime('%d.%m.%Y %H:%M')}"

# Model za izveštaj
class Izvestaj(models.Model):
    TIP_CHOICES = (
        ('zalihe', 'Izveštaj o zalihama'),
        ('finansijski', 'Finansijski izveštaj'),
        ('dobavljaci', 'Izveštaj o dobavljačima'),
        ('kvalitet', 'Izveštaj o kvalitetu'),
        ('temperature', 'Izveštaj o temperaturama'),
        ('koordinator', 'Izveštaj logističkog koordinatora'),
    )
    
    sifra_iz = models.AutoField(primary_key=True)
    datum_i = models.DateTimeField(auto_now_add=True)
    tip_i = models.CharField(max_length=30, choices=TIP_CHOICES)
    sadrzaj_i = models.TextField()
    
    # Veza sa korisnikom koji je kreirao izveštaj
    kreirao = models.ForeignKey(User, on_delete=models.CASCADE, related_name='izvestaji')
    
    pdf_file = models.FileField(upload_to='izvestaji_pdfs/', null=True, blank=True)
    
    class Meta:
        db_table = 'izvestaj'
    
    def __str__(self):
        return f"Izveštaj {self.sifra_i} - {self.get_tip_i_display()}"

# Model za popust
class Popust(models.Model):
    sifra_p = models.AutoField(primary_key=True)
    predlozena_cena_a = models.DecimalField(max_digits=10, decimal_places=2)
    datum_pocetka_vazenja_p = models.DateField()
    datum_kraja_vazenja_p = models.DateField()
    
    # Veza sa artiklom (se_primenjuje - 0,N : 0,N)
    artikli = models.ManyToManyField(Artikal, related_name='popusti', blank=True)
    
    class Meta:
        db_table = 'popust'
    
    def __str__(self):
        return f"Popust {self.sifra_p} - {self.predlozena_cena_a} RSD"

# Model za temperaturu
class Temperatura(models.Model):
    id_merenja = models.AutoField(primary_key=True)
    vrednost = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperatura u Celzijusima")
    vreme_merenja = models.DateTimeField(auto_now_add=True)
    
    # Veza sa skladištem (beleži se u - 1,N : 1,N)
    skladiste = models.ForeignKey(Skladiste, on_delete=models.CASCADE, related_name='temperature',null=True, blank=True)
    vozilo = models.ForeignKey('Vozilo', on_delete=models.CASCADE, related_name='temperature', null=True, blank=True)
    class Meta:
        db_table = 'temperatura'
    
    def __str__(self):
        string = "Temperatura {self.vrednost}°C u "
        if self.skladiste is not None:
            string += f"{self.skladiste.mesto_s}"
        if self.vozilo is not None:
            string += f"vozilu {self.vozilo.marka} {self.vozilo.model}"
        #return f"Temperatura {self.vrednost}°C u {self.skladiste.mesto_s}"

# Model za notifikaciju
class Notifikacija(models.Model):
    sifra_n = models.AutoField(primary_key=True)
    poruka_n = models.TextField()
    datum_n = models.DateTimeField(auto_now_add=True)
    procitana_n = models.BooleanField(default=False)
    link_n = models.URLField(blank=True, null=True)
    
    # Veza sa korisnikom (se_šalje - 0,N : 1,N)
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifikacije')
    
    class Meta:
        db_table = 'notifikacija'
        ordering = ['-datum_n']
    
    def __str__(self):
        return f"Notifikacija za {self.korisnik.ime_k} {self.korisnik.prz_k} - {self.datum_n.strftime('%d.%m.%Y')}"

#def get_isporuka_for_vehicle(self):
#    raise NotImplementedError
    

class Vozilo(models.Model):
    sifra_v = models.AutoField(primary_key=True)
    marka = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    #registracija = models.DateField(auto_now_add=True)
    registracija = models.DateField(null=False, blank=True)
    kapacitet = models.DecimalField(max_digits=10, decimal_places=2)
    #isporuka = models.ForeignKey(Isporuka, on_delete=models.CASCADE);
    status_choices = [
        ('zauzeto', 'Zauzeto'),
        ('slobodno', 'Slobodno'),
        ('u_kvaru', 'U kvaru'),
        ('na_servisu', 'Na servisu'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='aktivno')

    def __str__(self):
        return f"{self.marka} {self.model} ({self.registracija})"
    
    def get_isporuka_for_vehicle(self):
        return Isporuka.objects.filter(vozilo=self, status__in=['u_toku']).first()
    
    def save(self, *args, **kwargs):
        # if self.status in ['u_kvaru', 'na_servisu']:
        #     Upozorenje.objects.create(
        #         tip='kvar',
        #         poruka=f'Vozilo {self.marka} {self.model} je trenutno {self.status}.',
        #         isporuka = get_isporuka_for_vehicle(self) 
        #     )
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'vozilo'
    

class Servis(models.Model):
    sifra_s = models.AutoField(primary_key=True)
    vozilo = models.ForeignKey(Vozilo, on_delete=models.CASCADE)
    datum_servisa = models.DateField()
    napomena = models.TextField()
    vrsta_choices = [
        ('mali', 'Mali'),
        ('veliki', 'Veliki'),
        ('hitan', 'Hitan'),
    ]
    vrsta = models.CharField(max_length=20, choices=vrsta_choices)
    
    def __str__(self):
        return f"Servis {self.vozilo.registracija} - {self.datum_servisa}"
    
    class Meta:
        db_table = 'servis'

class Ruta(models.Model):
    sifra_r = models.AutoField(primary_key=True)
    polazna_tacka = models.CharField(max_length=100)
    odrediste = models.CharField(max_length=100)
    duzina_km = models.DecimalField(max_digits=10, decimal_places=2)
    vreme_dolaska = models.DurationField()
    status_choices = [
        ('planirana', 'Planirana'),
        ('zavrsena', 'Zavrsena'),
        ('u_toku', 'U toku'),
        ('odstupanje', 'Odstupanje od pocetne rute'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)

    
    def __str__(self):
        return f"{self.polazna_tacka} -> {self.odrediste}"
    
    class Meta:
        db_table = 'ruta'
class Vozac(models.Model):
    sifra_vo = models.AutoField(primary_key=True)
    ime_vo = models.CharField(max_length=100)
    prz_vo = models.CharField(max_length=100)
    br_voznji = models.IntegerField()
    status_choices = [
        ('slobodan', 'Slobodan'),
        ('zauzet', 'Zauzet'),
        ('na_odmoru', 'Na odmoru'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='slobodan')
    class Meta:
        db_table = 'vozac'
    @property
    def id(self):
        return self.sifra_vo
    def __str__(self):
        return f"{self.ime_vo} {self.prz_vo} ({self.br_voznji} vožnji)"
    status = models.CharField(max_length=20, choices=status_choices, default='slobodan')
    def get_all_vozaci(request):
        vozaci = Vozac.objects.all()
        return vozaci
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Isporuka(models.Model):
    sifra_i = models.AutoField(primary_key=True)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, null=True)
    vozilo = models.ForeignKey(Vozilo, on_delete=models.CASCADE , null=True)
    vozac = models.ForeignKey(Vozac, on_delete=models.CASCADE, null=True)
    status_choices = [
        ('aktivna', 'Nova'),
        ('u_toku', 'U toku'),
        ('spremna', 'Spremna'),
        ('zavrsena', 'Završena'),
    ]
    kolicina_kg = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=status_choices, default='aktivna')
    datum_kreiranja = models.DateTimeField(auto_now_add=True)
    datum_polaska = models.DateTimeField(null=True, blank=True)
    rok_is = models.DateTimeField(null=True, blank=True)
    datum_dolaska = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Isporuka {self.sifra_i} - {self.ruta}"
    
    class Meta:
        db_table = 'isporuka'
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
class Upozorenje(models.Model):
    sifra_u = models.AutoField(primary_key=True)
    isporuka = models.ForeignKey(Isporuka, on_delete=models.CASCADE)
    tip_choices = [
        ('odstupanje', 'odstupanje od rute'),
        ('temperatura', 'temperatura'),
        ('kvar', 'kvar vozila'),
        ('kasnjenje', 'kašnjenje utovara'),
        ('servis', 'servis vozila'),
    ]
    
    tip = models.CharField(max_length=50, choices= tip_choices)
    poruka = models.TextField()
    vreme = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.tip} - {self.isporuka}"
    
    class Meta:
        db_table = 'upozorenje'

class voziloOmogucavaTemperatura(models.Model):
    sifra_temp = models.ForeignKey(Temperatura, on_delete=models.CASCADE)
    sifra_vozila = models.ForeignKey(Vozilo, on_delete=models.CASCADE)
    isporuka = models.ForeignKey(Isporuka, on_delete=models.CASCADE)
    vreme = models.DateTimeField(auto_now_add=True)
    vrednost = models.DecimalField(max_digits=5, decimal_places=2)
    min_granica = models.DecimalField(max_digits=5, decimal_places=2)
    max_granica = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.isporuka} - {self.vrednost}°C"
    def vrednostIzvanGranica(self):
        if((self.vrednost > self.max_granica) & (self.vrednost < self.min_granica)):
            return Upozorenje(isporuka = self.isporuka, tip = 'temperatura', poruka = 'Temperatura je izvan opsega.' )
    class Meta:
        db_table = 'temperaturaVozilo'

class Rampa(models.Model):
    sifra_rp = models.AutoField(primary_key=True)
    skladiste = models.ForeignKey(Skladiste, on_delete=models.CASCADE, related_name='rampe')
    oznaka = models.CharField(max_length=50)
    status_choices = [
        ('slobodna', 'Slobodna'),
        ('zauzeta', 'Zauzeta'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='slobodna')

    def __str__(self):
        return f"Rampa {self.oznaka} ({self.status})"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    def zauzmi(self, trajanje_h):
        """Označava rampu kao zauzetu i postavlja vreme oslobađanja."""
        self.status = 'zauzeta'
        #self.vreme_zauzeca = datetime.now()
        #self.procenjeno_vreme_oslobadjanja = datetime.now() + timedelta(hours=trajanje_h)
        self.save()

    def oslobodi(self):
        """Menja status rampe u slobodna."""
        self.status = 'slobodna'
        #self.vreme_zauzeca = None
        #self.procenjeno_vreme_oslobadjanja = None
        self.save()

    class Meta:
        db_table = 'rampa'

class Voznja(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    trenutna_lat = models.FloatField()
    trenutna_lon = models.FloatField()
    vreme_azuriranja = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Voznja rute {self.ruta.polazna_tacka} → {self.ruta.odrediste} ({self.trenutna_lat}, {self.trenutna_lon})"

    class Meta:
        db_table = 'voznja'