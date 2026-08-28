from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

# ============================================================================
# DRUGI PASS (avgust 2026): mentorka je tražila izmene EER-a i podsistem je
# SUŽEN isključivo na finansijsko-analitički deo (dobavljači, katalog/cenovnik,
# ugovori/penali, fakture/stavke, transakcije, izveštavanje, kontrolna tabla).
# Zalihe, nabavka, skladištenje, kontrola kvaliteta i notifikacije NISU deo ovog
# EER-a - njihovi modeli ispod (sekcija "OSTALI PODSISTEMI") su namerno
# NETAKNUTI, uključujući i deljeni Dobavljac koji zadržava par polja koja taj
# kod i dalje koristi. Vidi CLAUDE.md za punu listu odstupanja.
#
# Konvencija (ista kao u prvom passu): ime Python polja = ime ER atributa;
# svaki FK dobija db_column jednak ER koloni; JSON ključevi ka frontendu
# ostaju nepromenjeni preko serializers_mk.py (source=...) ili @property.
# ============================================================================


# ============================================================================
# MOJI MODELI - finansijsko-analitički podsistem (views_mk.py, serializers_mk.py)
# ============================================================================

# Model za korisnika - centralni entitet (KORISNIK). Deljen sa svim ostalim
# ulogama u aplikaciji (tip_k zadržava svih 6 vrednosti - odstupanje od ER-ovog
# "samo FINANSIJSKI_ANALITICAR", jer bi suženje pokvarilo prijavu za ostale
# uloge čiji kod namerno ne diramo).
class User(AbstractUser):
    USER_TYPES = (
        ('logisticki_koordinator', 'Logistički koordinator'),
        ('skladisni_operater', 'Skladišni operater'),
        ('nabavni_menadzer', 'Nabavni menadžer'),
        ('finansijski_analiticar', 'Finansijski analitičar'),
        ('kontrolor_kvaliteta', 'Kontrolor kvaliteta'),
        ('administrator', 'Administrator'),
    )

    sifra_k = models.AutoField(primary_key=True)
    ime_k = models.CharField(max_length=50)
    prz_k = models.CharField(max_length=50)
    mail_k = models.EmailField(max_length=100, unique=True)
    tip_k = models.CharField(max_length=30, choices=USER_TYPES)

    USERNAME_FIELD = 'mail_k'
    REQUIRED_FIELDS = ['ime_k', 'prz_k', 'tip_k']

    class Meta:
        db_table = 'korisnik'

    @property
    def id(self):
        return self.sifra_k

    def __str__(self):
        return f"{self.ime_k} {self.prz_k} ({self.get_tip_k_display()})"


# FinansijskiAnaliticar - parcijalna specijalizacija Korisnika (ne mora svaki
# korisnik biti analitičar). PK JE sifra_k korisnika, tačno kao u ER-u.
class FinansijskiAnaliticar(models.Model):
    korisnik = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column='sifra_k', related_name="finansijski_analiticar"
    )

    class Meta:
        db_table = 'finansijski_analiticar'

    def __str__(self):
        return f"Finansijski analitičar: {self.korisnik.ime_k} {self.korisnik.prz_k}"


# Šifarnik jedinica mere - koristi se i za količinske jedinice i za valute
# (redovi tipa NOVAC: RSD, EUR).
class JedinicaMere(models.Model):
    TIP_CHOICES = (
        ('KOLICINA', 'Količina'),
        ('MASA', 'Masa'),
        ('ZAPREMINA', 'Zapremina'),
        ('NOVAC', 'Novac'),
        ('PROCENAT', 'Procenat'),
        ('VREME', 'Vreme'),
    )

    sifra_jm = models.AutoField(primary_key=True)
    naziv_jm = models.CharField(max_length=100)
    oznaka_jm = models.CharField(max_length=20)
    tip_jm = models.CharField(max_length=20, choices=TIP_CHOICES)

    class Meta:
        db_table = 'jedinica_mere'

    def __str__(self):
        return f"{self.naziv_jm} ({self.oznaka_jm})"


# Model za dobavljača (DOBAVLJAC) - DELJEN entitet. ER traži samo
# sifra_db/naziv_db/email_db/pib_db; ocena_db/datum_ocenjivanja/ime_sirovine/
# cena/rok_isporuke/izabran su NAMERNO zadržani jer ih views_mv.py i
# views_mv2.py (nabavni menadžer / kontrolor kvaliteta - van obima ove izmene)
# aktivno čitaju i pišu. Brisanje bi pokvarilo taj kod.
class Dobavljac(models.Model):
    sifra_db = models.AutoField(primary_key=True)
    naziv_db = models.CharField(max_length=150)
    email_db = models.EmailField(max_length=100)
    pib_db = models.CharField(max_length=20, unique=True)

    # --- van ER-a, zadržano za NM/KK podsistem (ne dirati) ---
    ocena_db = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))])
    datum_ocenjivanja = models.DateField()
    ime_sirovine = models.CharField(max_length=200)
    cena = models.DecimalField(max_digits=10, decimal_places=2)
    rok_isporuke = models.IntegerField(help_text="Rok isporuke u danima")
    izabran = models.BooleanField(default=False)

    class Meta:
        db_table = 'dobavljac'

    # kompatibilnost sa starim imenom (NM/KK kod)
    @property
    def sifra_d(self):
        return self.sifra_db

    @property
    def naziv(self):
        return self.naziv_db

    @property
    def email(self):
        return self.email_db

    @property
    def PIB_d(self):
        return self.pib_db

    @property
    def ocena(self):
        return self.ocena_db

    def __str__(self):
        return f"{self.naziv_db} - {self.ime_sirovine}"


# Model za kategoriju proizvoda (KATEGORIJA_PROIZVODA). limit_kp uklonjen (ER).
class KategorijaProizvoda(models.Model):
    sifra_kp = models.AutoField(primary_key=True)
    naziv_kp = models.CharField(max_length=100)

    class Meta:
        db_table = 'kategorija_proizvoda'

    def __str__(self):
        return self.naziv_kp


# Model za proizvod (PROIZVOD) - master katalog proizvoda (bez cene/dobavljača,
# to je sada u ProizvodDobavljaca/Cenovnik).
class Proizvod(models.Model):
    PDV_CHOICES = (
        (0, '0%'),
        (10, '10%'),
        (20, '20%'),
    )

    sifra_pr = models.AutoField(primary_key=True)
    naziv_pr = models.CharField(max_length=150)
    # ER deklariše VARCHAR2(2000); zadržan TextField (CLOB) - NVARCHAR2 na
    # Oracle-u koristi 2 bajta/karakter pa bi 2000 karaktera tražilo 4000+
    # bajtova, na granici/preko standardnog Oracle limita (ORA-00910).
    opis_pr = models.TextField(blank=True)
    pdv_stopa_pr = models.IntegerField(choices=PDV_CHOICES, default=20)

    kategorija = models.ForeignKey(KategorijaProizvoda, on_delete=models.PROTECT, db_column='KATEGORIJA_PROIZVODA_sifra_kp', related_name='proizvodi')
    jedinica_mere = models.ForeignKey(JedinicaMere, on_delete=models.PROTECT, db_column='JEDINICA_MERE_sifra_jm', related_name='proizvodi')

    class Meta:
        db_table = 'proizvod'

    def __str__(self):
        return self.naziv_pr


# Gerund nad vezom "nudi" (Dobavljac <-> Proizvod) - jedna kataloška stavka
# dobavljača. Prirodni ključ (dobavljac, proizvod).
class ProizvodDobavljaca(models.Model):
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, db_column='DOBAVLJAC_sifra_db', related_name='katalog')
    proizvod = models.ForeignKey(Proizvod, on_delete=models.PROTECT, db_column='PROIZVOD_sifra_pr', related_name='ponude_dobavljaca')
    sifra_kod_dobavljaca_pd = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'proizvod_dobavljaca'
        constraints = [
            models.UniqueConstraint(fields=['dobavljac', 'proizvod'], name='uq_proizvod_dobavljaca'),
        ]

    def __str__(self):
        return f"{self.proizvod.naziv_pr} @ {self.dobavljac.naziv_db}"


# Ugovorena neto cena kataloške stavke (rabati su već uračunati - popust se
# ne modeluje odvojeno).
class Cenovnik(models.Model):
    sifra_c = models.AutoField(primary_key=True)
    cena_c = models.DecimalField(max_digits=12, decimal_places=2)
    datum_od_c = models.DateField()
    datum_do_c = models.DateField(null=True, blank=True, help_text="NULL = trenutno važeća cena")

    proizvod_dobavljaca = models.ForeignKey(ProizvodDobavljaca, on_delete=models.CASCADE, db_column='PROIZVOD_DOBAVLJACA_id', related_name='cenovnik')
    valuta = models.ForeignKey(JedinicaMere, on_delete=models.PROTECT, db_column='JEDINICA_MERE_sifra_jm', related_name='cene')

    class Meta:
        db_table = 'cenovnik'
        constraints = [
            models.UniqueConstraint(fields=['proizvod_dobavljaca', 'datum_od_c'], name='uq_cenovnik_pd_datum_od'),
            models.CheckConstraint(
                check=models.Q(datum_do_c__isnull=True) | models.Q(datum_do_c__gte=models.F('datum_od_c')),
                name='ck_cenovnik_datum_do_posle_od',
            ),
        ]

    def __str__(self):
        return f"{self.proizvod_dobavljaca} - {self.cena_c} od {self.datum_od_c}"


# Model za ugovor (UGOVOR)
class Ugovor(models.Model):
    STATUS_CHOICES = (
        ('u_pripremi', 'U pripremi'),
        ('aktivan', 'Aktivan'),
        ('istekao', 'Istekao'),
        ('raskinut', 'Raskinut'),
    )

    sifra_u = models.AutoField(primary_key=True)
    datum_potpisa_u = models.DateField()
    datum_isteka_u = models.DateField()
    status_u = models.CharField(max_length=30, choices=STATUS_CHOICES, default='aktivan')
    uslovi_u = models.TextField()

    # PROTECT: finansijski/pravni trag - ugovor sa već izdatim fakturama/penalima
    # ne sme nestati zajedno sa dobavljačem.
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.PROTECT, db_column='DOBAVLJAC_sifra_db', related_name='ugovori')

    class Meta:
        db_table = 'ugovor'

    def __str__(self):
        return f"Ugovor {self.sifra_u} sa {self.dobavljac.naziv_db}"


# Model za fakturu (FAKTURA)
class Faktura(models.Model):
    STATUS_CHOICES = (
        ('primljena', 'Primljena'),
        ('verifikovana', 'Verifikovana'),
        ('isplacena', 'Isplaćena'),
        ('odbijena', 'Odbijena'),
    )
    # NAMERNO ODSTUPANJE: ER traži širi skup (PRIMLJENA, U_OBRADI, ODOBRENA,
    # NA_CEKANJU, PLACENA, ODBIJENA, STORNIRANA). front/ (Invoice.js,
    # InvoiceDetails.js) hardkoduje tačno ove 4 postojeće vrednosti za prikaz
    # dugmadi/toka procesa, a front se ne dira - zato je zadržan uži, već
    # funkcionalan skup. Vidi CLAUDE.md.

    sifra_f = models.AutoField(primary_key=True)
    iznos_f = models.DecimalField(max_digits=12, decimal_places=2)
    datum_prijema_f = models.DateField()
    rok_placanja_f = models.DateField()
    status_f = models.CharField(max_length=30, choices=STATUS_CHOICES, default='primljena')

    # PROTECT: faktura je finansijski dokument, ne sme nestati ako se ugovor obriše.
    ugovor = models.ForeignKey(Ugovor, on_delete=models.PROTECT, db_column='UGOVOR_sifra_u', related_name='fakture')
    valuta = models.ForeignKey(JedinicaMere, on_delete=models.PROTECT, db_column='JEDINICA_MERE_sifra_jm', related_name='fakture')

    class Meta:
        db_table = 'faktura'

    @property
    def transakcija(self):
        """Kompatibilnost sa starim 1:1 pristupom - vraća poslednju transakciju fakture."""
        return self.transakcije.order_by('-datum_t', '-sifra_t').first()

    @property
    def razlog_cekanja_f(self):
        """ER uklanja ovu kolonu sa Faktura - razlog se sada čuva po promeni
        statusa (PromenaStatusa.razlog_ps). Vraća razlog poslednje zabeležene
        promene statusa, čime front/ i dalje dobija isti JSON ključ/ponašanje."""
        poslednja = self.promene_statusa.order_by('-datum_vreme_ps', '-sifra_ps').first()
        return poslednja.razlog_ps if poslednja and poslednja.razlog_ps else None

    def promeni_status(self, novi_status, korisnik, razlog=''):
        """Servisna metoda (poslovno pravilo #5): SVAKA promena Faktura.status_f
        mora ići kroz ovu metodu (ne kroz direktno self.status_f = ...; save()),
        jer upisuje istorijat u PromenaStatusa. status_f ostaje na Fakturi kao
        namerno redundantno, lako dostupno polje (poslovno pravilo #7)."""
        stari_status = self.status_f
        self.status_f = novi_status
        self.save(update_fields=['status_f'])
        PromenaStatusa.objects.create(
            faktura=self,
            korisnik=korisnik,
            stari_status_ps=stari_status,
            novi_status_ps=novi_status,
            razlog_ps=razlog or '',
        )
        return self

    def __str__(self):
        return f"Faktura {self.sifra_f} - {self.iznos_f} RSD"


# Model za stavku fakture (STAVKA_FAKTURE) - sada FK ka ProizvodDobavljaca
# (kataloškoj stavci dobavljača), NE direktno ka Proizvod.
class StavkaFakture(models.Model):
    sifra_sf = models.AutoField(primary_key=True)
    naziv_sf = models.CharField(max_length=150)
    kolicina_sf = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cena_po_jed_sf = models.DecimalField(max_digits=12, decimal_places=2)
    opis_sf = models.CharField(max_length=1000, blank=True)

    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE, db_column='FAKTURA_sifra_f', related_name='stavke')
    proizvod_dobavljaca = models.ForeignKey(ProizvodDobavljaca, on_delete=models.PROTECT, db_column='PROIZVOD_DOBAVLJACA_id', related_name='stavke_fakture')

    class Meta:
        db_table = 'stavka_fakture'

    @property
    def cena_po_jed(self):
        return self.cena_po_jed_sf

    @property
    def proizvod(self):
        """Kompatibilnost - direktan pristup proizvodu kroz katalošku stavku dobavljača."""
        return self.proizvod_dobavljaca.proizvod

    def clean(self):
        """Poslovno pravilo #1: dobavljač na fakturi (preko ugovora) mora biti
        isti kao dobavljač kataloške stavke koju ova stavka fakture koristi."""
        if self.proizvod_dobavljaca_id and self.faktura_id:
            if self.proizvod_dobavljaca.dobavljac_id != self.faktura.ugovor.dobavljac_id:
                raise ValidationError(
                    "Dobavljač stavke fakture mora biti isti kao dobavljač na ugovoru fakture."
                )

    def __str__(self):
        return f"Stavka {self.naziv_sf} - {self.kolicina_sf} x {self.cena_po_jed_sf}"


# Model za transakciju (TRANSAKCIJA)
class Transakcija(models.Model):
    STATUS_CHOICES = (
        ('na_cekanju', 'Na čekanju'),
        ('uspesna', 'Uspešna'),
        ('neuspesna', 'Neuspešna'),
    )
    # NAMERNO ODSTUPANJE: ER traži INICIRANA/IZVRSENA/NEUSPELA/STORNIRANA;
    # zadržan postojeći skup iz istog razloga kao Faktura.status_f (front/
    # prikazuje get_status_t_display() teksta koje smo already lokalizovali).

    sifra_t = models.AutoField(primary_key=True)
    datum_t = models.DateTimeField(auto_now_add=True)
    broj_potvrde_t = models.CharField(max_length=100, unique=True)
    status_t = models.CharField(max_length=30, choices=STATUS_CHOICES, default='na_cekanju')
    iznos_t = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # PROTECT: transakcija je finansijski dokaz o plaćanju, ne sme nestati
    # zajedno sa fakturom.
    faktura = models.ForeignKey(Faktura, on_delete=models.PROTECT, db_column='FAKTURA_sifra_f', related_name='transakcije')

    class Meta:
        db_table = 'transakcija'

    @property
    def potvrda_t(self):
        return self.broj_potvrde_t

    def __str__(self):
        return f"Transakcija {self.broj_potvrde_t} za fakturu {self.faktura.sifra_f}"


# Model za penal (PENAL)
class Penal(models.Model):
    TIP_PENALA_CHOICES = (
        ('KASNJENJE_ISPORUKE', 'Kašnjenje isporuke'),
        ('KASNJENJE_PLACANJA', 'Kašnjenje plaćanja'),
        ('KVALITET', 'Kvalitet'),
        ('OSTALO', 'Ostalo'),
    )

    sifra_p = models.AutoField(primary_key=True)
    razlog_p = models.CharField(max_length=500)
    iznos_p = models.DecimalField(max_digits=12, decimal_places=2)
    datum_p = models.DateField(auto_now_add=True)
    tip_penala_p = models.CharField(max_length=30, choices=TIP_PENALA_CHOICES, default='OSTALO')

    ugovor = models.ForeignKey(Ugovor, on_delete=models.PROTECT, db_column='UGOVOR_sifra_u', related_name='penali')

    class Meta:
        db_table = 'penal'

    def __str__(self):
        return f"Penal {self.sifra_p} - {self.iznos_p} RSD"


# Istorijat promena statusa fakture (Ugovor i Transakcija nemaju istorijat -
# njihov status se izvodi iz datuma).
class PromenaStatusa(models.Model):
    sifra_ps = models.AutoField(primary_key=True)
    datum_vreme_ps = models.DateTimeField(auto_now_add=True)
    stari_status_ps = models.CharField(max_length=30, choices=Faktura.STATUS_CHOICES, blank=True, null=True)
    novi_status_ps = models.CharField(max_length=30, choices=Faktura.STATUS_CHOICES)
    razlog_ps = models.CharField(max_length=500, blank=True)

    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE, db_column='FAKTURA_sifra_f', related_name='promene_statusa')
    # PROTECT: ne sme se izgubiti "ko je izvršio promenu" brisanjem korisnika.
    korisnik = models.ForeignKey(User, on_delete=models.PROTECT, db_column='KORISNIK_sifra_k', related_name='promene_statusa_izvrsene')

    class Meta:
        db_table = 'promena_statusa'
        ordering = ['-datum_vreme_ps']

    def __str__(self):
        return f"Faktura {self.faktura_id}: {self.stari_status_ps} -> {self.novi_status_ps}"


# Ocena dobavljača po kriterijumu i periodu (zamenjuje staru jednu ocena_db kolonu
# vremenskom istorijom po kriterijumima - ocena_db na Dobavljac je i dalje
# zadržana zbog NM/KK koda, ali FA sada vodi svoju, precizniju analitiku ovde).
class OcenaDobavljaca(models.Model):
    KRITERIJUM_CHOICES = (
        ('TACNOST_FAKTURISANJA', 'Tačnost fakturisanja'),
        ('POSTOVANJE_ROKOVA', 'Poštovanje rokova'),
        ('BROJ_PENALA', 'Broj penala'),
        ('ODNOS_CENA', 'Odnos cena'),
    )

    sifra_od = models.AutoField(primary_key=True)
    kriterijum_od = models.CharField(max_length=30, choices=KRITERIJUM_CHOICES)
    vrednost_od = models.DecimalField(max_digits=5, decimal_places=2)
    period_od_od = models.DateField()
    period_do_od = models.DateField()
    datum_ocenj_od = models.DateField()

    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, db_column='DOBAVLJAC_sifra_db', related_name='ocene')

    class Meta:
        db_table = 'ocena_dobavljaca'
        constraints = [
            models.UniqueConstraint(fields=['dobavljac', 'kriterijum_od', 'period_od_od'], name='uq_ocena_dobavljac_kriterijum_period'),
            models.CheckConstraint(check=models.Q(period_do_od__gte=models.F('period_od_od')), name='ck_ocena_period_do_posle_od'),
            models.CheckConstraint(check=models.Q(datum_ocenj_od__gte=models.F('period_do_od')), name='ck_ocena_datum_posle_period'),
        ]

    def __str__(self):
        return f"Ocena {self.dobavljac.naziv_db} - {self.kriterijum_od}: {self.vrednost_od}"


# Model za kontrolnu tablu (bivši DASHBOARD - preimenovan i pojednostavljen;
# JSON snapshot je zamenjen relacionim Metrika/Merenje modelima ispod).
class KontrolnaTabla(models.Model):
    sifra_kt = models.AutoField(primary_key=True)
    naziv_kt = models.CharField(max_length=150)
    opis_kt = models.CharField(max_length=500, blank=True)

    finansijski_analiticari = models.ManyToManyField(
        FinansijskiAnaliticar, through='Kreiranje', blank=True, related_name='kontrolne_table'
    )

    class Meta:
        db_table = 'kontrolna_tabla'

    def __str__(self):
        return self.naziv_kt


# Gerund nad vezom "kreira" (FinansijskiAnaliticar <-> KontrolnaTabla).
# Izvestaj visi na OVOM modelu (ne direktno na FA ili tabli), čime je
# garantovano da izveštaj pripada tačno onom paru (analitičar, tabla).
class Kreiranje(models.Model):
    finansijski_analiticar = models.ForeignKey(FinansijskiAnaliticar, on_delete=models.CASCADE, db_column='FINANSIJSKI_ANALITICAR_sifra_k')
    kontrolna_tabla = models.ForeignKey(KontrolnaTabla, on_delete=models.CASCADE, db_column='KONTROLNA_TABLA_sifra_kt')
    datum_kr = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kreiranje'
        constraints = [
            models.UniqueConstraint(fields=['finansijski_analiticar', 'kontrolna_tabla'], name='uq_kreiranje_fa_tabla'),
        ]

    def __str__(self):
        return f"{self.finansijski_analiticar} kreira {self.kontrolna_tabla}"


# Definicija metrike (npr. "Ukupno plaćeno", "Mesečni trošak"...).
class Metrika(models.Model):
    sifra_m = models.AutoField(primary_key=True)
    naziv_m = models.CharField(max_length=150)
    opis_m = models.CharField(max_length=500, blank=True)
    formula_m = models.CharField(max_length=500, blank=True)

    jedinica_mere = models.ForeignKey(JedinicaMere, on_delete=models.PROTECT, db_column='JEDINICA_MERE_sifra_jm', related_name='metrike')

    class Meta:
        db_table = 'metrika'

    def __str__(self):
        return self.naziv_m


# Gerund nad vezom "se_meri" (KontrolnaTabla <-> Metrika) - jedna izmerena
# vrednost metrike na tabli u datom trenutku/periodu. Ovo zamenjuje bivši
# Dashboard.snimak_metrika_json.
class Merenje(models.Model):
    kontrolna_tabla = models.ForeignKey(KontrolnaTabla, on_delete=models.CASCADE, db_column='KONTROLNA_TABLA_sifra_kt', related_name='merenja')
    metrika = models.ForeignKey(Metrika, on_delete=models.PROTECT, db_column='METRIKA_sifra_m', related_name='merenja')
    vrednost_me = models.DecimalField(max_digits=14, decimal_places=2)
    # Namerno NIJE auto_now_add: za istorijske/periodične tačke (npr. mesečni
    # trošak) vreme_merenja_me predstavlja trenutak NA KOJI SE merenje odnosi,
    # ne trenutak upisa u bazu - inače bi svi redovi upisani u istom pozivu
    # dobili identičnu vrednost i pukli na unique_together.
    vreme_merenja_me = models.DateTimeField(default=timezone.now)
    period_od_me = models.DateField(null=True, blank=True)
    period_do_me = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'merenje'
        constraints = [
            models.UniqueConstraint(fields=['kontrolna_tabla', 'metrika', 'vreme_merenja_me'], name='uq_merenje_tabla_metrika_vreme'),
        ]

    def __str__(self):
        return f"{self.metrika.naziv_m} = {self.vrednost_me} ({self.kontrolna_tabla})"


# Model za izveštaj (IZVESTAJ) - sadržaj je sada relacioni (PredmetIzvestaja +
# Merenje), ne JSON blob; visi na Kreiranje (FA + tabla), ne direktno na FA.
class Izvestaj(models.Model):
    TIP_CHOICES = (
        ('FINANSIJSKI', 'Finansijski'),
        ('DOBAVLJACI', 'Dobavljači'),
        ('UGOVORI', 'Ugovori'),
        ('PLACANJA', 'Plaćanja'),
    )

    sifra_i = models.AutoField(primary_key=True)
    datum_i = models.DateTimeField(auto_now_add=True)
    tip_i = models.CharField(max_length=30, choices=TIP_CHOICES)
    period_od_i = models.DateField(null=True, blank=True)
    period_do_i = models.DateField(null=True, blank=True)
    pdf_fajl = models.FileField(upload_to='izvestaji_pdfs/', null=True, blank=True)

    kreiranje = models.ForeignKey(Kreiranje, on_delete=models.PROTECT, db_column='KREIRANJE_id', related_name='izvestaji')
    merenja = models.ManyToManyField(Merenje, blank=True, related_name='izvestaji')

    class Meta:
        db_table = 'izvestaj'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(period_od_i__isnull=True) | models.Q(period_do_i__isnull=True) |
                    models.Q(period_do_i__gte=models.F('period_od_i'))
                ),
                name='ck_izvestaj_period_do_posle_od',
            ),
        ]
        indexes = [
            models.Index(fields=['tip_i', 'datum_i']),
        ]

    # --- kompatibilnost sa starim pristupom (pre restrukturiranja Izvestaj-a) ---
    @property
    def pdf_file(self):
        return self.pdf_fajl

    @property
    def finansijski_analiticar(self):
        return self.kreiranje.finansijski_analiticar

    @property
    def kreirao_id(self):
        return self.kreiranje.finansijski_analiticar_id

    def __str__(self):
        return f"Izveštaj {self.sifra_i} - {self.get_tip_i_display()}"


# Generički "predmet" izveštaja - tačno JEDAN od 4 FK-a sme biti popunjen
# (garantovano CheckConstraint-om), a tip_predmeta_pi mora njemu odgovarati
# (poslovno pravilo #4, proverava se u clean()).
class PredmetIzvestaja(models.Model):
    TIP_PREDMETA_CHOICES = (
        ('DOBAVLJAC', 'Dobavljač'),
        ('FAKTURA', 'Faktura'),
        ('UGOVOR', 'Ugovor'),
        ('PROIZVOD', 'Proizvod'),
    )

    sifra_pi = models.AutoField(primary_key=True)
    tip_predmeta_pi = models.CharField(max_length=20, choices=TIP_PREDMETA_CHOICES)

    izvestaj = models.ForeignKey(Izvestaj, on_delete=models.CASCADE, db_column='IZVESTAJ_sifra_i', related_name='predmeti')
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.SET_NULL, null=True, blank=True, db_column='DOBAVLJAC_sifra_db', related_name='+')
    faktura = models.ForeignKey(Faktura, on_delete=models.SET_NULL, null=True, blank=True, db_column='FAKTURA_sifra_f', related_name='+')
    ugovor = models.ForeignKey(Ugovor, on_delete=models.SET_NULL, null=True, blank=True, db_column='UGOVOR_sifra_u', related_name='+')
    proizvod = models.ForeignKey(Proizvod, on_delete=models.SET_NULL, null=True, blank=True, db_column='PROIZVOD_sifra_pr', related_name='+')

    class Meta:
        db_table = 'predmet_izvestaja'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(dobavljac__isnull=False, faktura__isnull=True, ugovor__isnull=True, proizvod__isnull=True) |
                    models.Q(dobavljac__isnull=True, faktura__isnull=False, ugovor__isnull=True, proizvod__isnull=True) |
                    models.Q(dobavljac__isnull=True, faktura__isnull=True, ugovor__isnull=False, proizvod__isnull=True) |
                    models.Q(dobavljac__isnull=True, faktura__isnull=True, ugovor__isnull=True, proizvod__isnull=False)
                ),
                name='ck_predmet_izvestaja_tacno_jedan_fk',
            ),
        ]

    def clean(self):
        """Poslovno pravilo #4: tip_predmeta_pi mora odgovarati popunjenom FK-u."""
        mapping = {
            'DOBAVLJAC': self.dobavljac_id,
            'FAKTURA': self.faktura_id,
            'UGOVOR': self.ugovor_id,
            'PROIZVOD': self.proizvod_id,
        }
        if not mapping.get(self.tip_predmeta_pi):
            raise ValidationError(f"tip_predmeta_pi='{self.tip_predmeta_pi}' zahteva popunjen odgovarajući FK.")

    def __str__(self):
        return f"Predmet {self.tip_predmeta_pi} izveštaja {self.izvestaj_id}"


# ============================================================================
# OSTALI PODSISTEMI - NE MENJATI (van obima ovog EER-a; nabavni menadžer,
# skladišni operater, kontrolor kvaliteta, logistički koordinator). Ovi modeli
# su namerno ostavljeni netaknuti - njihov kod (views_mv.py, views_mv2.py, deo
# views.py, signals.py, management komande) i dalje radi bez izmena.
# ============================================================================

class Administrator(models.Model):
    korisnik = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column='sifra_k', related_name="administrator"
    )

    class Meta:
        db_table = 'administrator'

    def __str__(self):
        return f"Administrator: {self.korisnik.ime_k} {self.korisnik.prz_k}"


class LogistickiKoordinator(models.Model):
    korisnik = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column='sifra_k', related_name="logisticki_koordinator"
    )

    class Meta:
        db_table = 'logisticki_koordinator'

    def __str__(self):
        return f"Logistički koordinator: {self.korisnik.ime_k} {self.korisnik.prz_k}"


class SkladisniOperater(models.Model):
    korisnik = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column='sifra_k', related_name="skladisni_operater"
    )

    class Meta:
        db_table = 'skladisni_operater'

    def __str__(self):
        return f"Skladišni operater: {self.korisnik.ime_k} {self.korisnik.prz_k}"


class NabavniMenadzer(models.Model):
    korisnik = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column='sifra_k', related_name="nabavni_menadzer"
    )

    class Meta:
        db_table = 'nabavni_menadzer'

    def __str__(self):
        return f"Nabavni menadžer: {self.korisnik.ime_k} {self.korisnik.prz_k}"


class KontrolorKvaliteta(models.Model):
    korisnik = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        db_column='sifra_k', related_name="kontrolor_kvaliteta"
    )

    class Meta:
        db_table = 'kontrolor_kvaliteta'

    def __str__(self):
        return f"Kontrolor kvaliteta: {self.korisnik.ime_k} {self.korisnik.prz_k}"


class Skladiste(models.Model):
    RIZIK_CHOICES = (
        ('nizak', 'Nizak rizik'),
        ('umeren', 'Umeren rizik'),
        ('visok', 'Visok rizik'),
    )

    sifra_sk = models.AutoField(primary_key=True)
    mesto_sk = models.CharField(max_length=150)
    status_rizika_sk = models.CharField(max_length=30, choices=RIZIK_CHOICES, default='nizak')

    class Meta:
        db_table = 'skladiste'

    @property
    def sifra_s(self):
        return self.sifra_sk

    @property
    def mesto_s(self):
        return self.mesto_sk

    @property
    def status_rizika_s(self):
        return self.status_rizika_sk

    def __str__(self):
        return f"Skladište {self.sifra_sk} - {self.mesto_sk}"


class Artikal(models.Model):
    STATUS_TRAJANJA_CHOICES = (
        ('aktivan', 'Aktivan'),
        ('istice', 'Uskoro ističe'),
        ('istekao', 'Istekao'),
    )

    sifra_a = models.AutoField(primary_key=True)
    naziv_a = models.CharField(max_length=150)
    osnovna_cena_a = models.DecimalField(max_digits=12, decimal_places=2)
    rok_trajanja_a = models.DateField()
    status_trajanja_a = models.CharField(max_length=30, choices=STATUS_TRAJANJA_CHOICES, default='aktivan')

    skladisni_operateri = models.ManyToManyField(SkladisniOperater, through='SeBavi', blank=True, related_name='artikli')

    class Meta:
        db_table = 'artikal'

    @property
    def status_trajanja(self):
        return self.status_trajanja_a

    def __str__(self):
        return f"{self.naziv_a} ({self.sifra_a})"


class Zalihe(models.Model):
    sifra_z = models.AutoField(primary_key=True)
    trenutna_kol_z = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    datum_azuriranja_z = models.DateTimeField(auto_now=True)

    artikal = models.ForeignKey(Artikal, on_delete=models.CASCADE, db_column='ARTIKAL_sifra_a', related_name='zalihe')
    skladiste = models.ForeignKey(Skladiste, on_delete=models.CASCADE, db_column='SKLADISTE_sifra_sk', related_name='zalihe')

    class Meta:
        db_table = 'zalihe'

    @property
    def trenutna_kolicina_a(self):
        return self.trenutna_kol_z

    @property
    def datum_azuriranja(self):
        return self.datum_azuriranja_z

    def __str__(self):
        return f"Zalihe {self.artikal.naziv_a} u {self.skladiste.mesto_sk}: {self.trenutna_kol_z}"


class SeBavi(models.Model):
    skladisni_operater = models.ForeignKey(SkladisniOperater, on_delete=models.CASCADE, db_column='SKLADISNI_OPERATOR_sifra_k')
    artikal = models.ForeignKey(Artikal, on_delete=models.CASCADE, db_column='ARTIKAL_sifra_a')
    datum_dodele = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'se_bavi'
        unique_together = ('skladisni_operater', 'artikal')

    def __str__(self):
        return f"{self.skladisni_operater} se bavi {self.artikal}"


class Sertifikat(models.Model):
    TIP_CHOICES = (
        ('ISO', 'ISO'),
        ('HACCP', 'HACCP'),
        ('GMP', 'GMP'),
        ('BRC', 'BRC'),
        ('IFS', 'IFS'),
        ('ostalo', 'Ostalo'),
    )

    sifra_s = models.AutoField(primary_key=True)
    naziv_s = models.CharField(max_length=150)
    tip_s = models.CharField(max_length=50, choices=TIP_CHOICES)
    datum_izdavanja_s = models.DateField()
    aktuelno_s = models.BooleanField(default=True)
    datum_isteka_s = models.DateField()

    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, db_column='DOBAVLJAC_sifra_db', related_name='sertifikati')

    class Meta:
        db_table = 'sertifikat'

    @property
    def sertifikat_id(self):
        return self.sifra_s

    @property
    def naziv(self):
        return self.naziv_s

    @property
    def tip(self):
        return self.tip_s

    @property
    def datum_izdavanja(self):
        return self.datum_izdavanja_s

    @property
    def datum_isteka(self):
        return self.datum_isteka_s

    def __str__(self):
        return f"Sertifikat {self.naziv_s} ({self.tip_s}) - {self.dobavljac.naziv_db}"


class Poseta(models.Model):
    STATUS_CHOICES = (
        ('zakazana', 'Zakazana'),
        ('u_toku', 'U toku'),
        ('zavrsena', 'Završena'),
        ('otkazana', 'Otkazana'),
    )

    sifra_po = models.AutoField(primary_key=True)
    datum_od_po = models.DateTimeField()
    datum_do_po = models.DateTimeField(null=True, blank=True)
    status_po = models.CharField(max_length=30, choices=STATUS_CHOICES, default='zakazana')

    kontrolor = models.ForeignKey(KontrolorKvaliteta, on_delete=models.CASCADE, db_column='KONTROLOR_KVALITETA_sifra_k', related_name='posete')
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, db_column='DOBAVLJAC_sifra_db', related_name='posete')

    class Meta:
        db_table = 'poseta'

    @property
    def poseta_id(self):
        return self.sifra_po

    @property
    def datum_od(self):
        return self.datum_od_po

    @property
    def datum_do(self):
        return self.datum_do_po

    @property
    def status(self):
        return self.status_po

    def __str__(self):
        return f"Poseta kod {self.dobavljac.naziv_db} - {self.datum_od_po.strftime('%d.%m.%Y')}"


class Reklamacija(models.Model):
    STATUS_CHOICES = (
        ('prijem', 'Prijem'),
        ('analiza', 'Analiza'),
        ('odgovor', 'Odgovor'),
        ('zatvaranje', 'Zatvaranje'),
    )

    sifra_r = models.AutoField(primary_key=True)
    datum_prijema_r = models.DateField(auto_now_add=True)
    status_r = models.CharField(max_length=30, choices=STATUS_CHOICES, default='prijem')
    opis_problema_r = models.TextField()
    vreme_trajanja_r = models.IntegerField(help_text="Vreme trajanja u danima")
    jacina_zalbe_r = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Jačina žalbe na skali 1-10"
    )

    kontrolor = models.ForeignKey(KontrolorKvaliteta, on_delete=models.CASCADE, db_column='KONTROLOR_KVALITETA_sifra_k', related_name='reklamacije')
    dobavljac = models.ForeignKey(Dobavljac, on_delete=models.CASCADE, db_column='DOBAVLJAC_sifra_db', related_name='reklamacije')

    class Meta:
        db_table = 'reklamacija'

    @property
    def reklamacija_id(self):
        return self.sifra_r

    @property
    def datum_prijema(self):
        return self.datum_prijema_r

    @property
    def status(self):
        return self.status_r

    @property
    def opis_problema(self):
        return self.opis_problema_r

    @property
    def vreme_trajanja(self):
        return self.vreme_trajanja_r

    @property
    def jacina_zalbe(self):
        return self.jacina_zalbe_r

    def __str__(self):
        return f"Reklamacija {self.sifra_r} protiv {self.dobavljac.naziv_db}"


class Popust(models.Model):
    sifra_pop = models.AutoField(primary_key=True)
    pred_cena_pop = models.DecimalField(max_digits=12, decimal_places=2)
    datum_poc_vaz_pop = models.DateField()
    datum_kr_vaz_pop = models.DateField()

    artikli = models.ManyToManyField(Artikal, through='SePrimenjuje', blank=True, related_name='popusti')

    class Meta:
        db_table = 'popust'

    @property
    def sifra_p(self):
        return self.sifra_pop

    @property
    def predlozena_cena_a(self):
        return self.pred_cena_pop

    @property
    def datum_pocetka_vazenja_p(self):
        return self.datum_poc_vaz_pop

    @property
    def datum_kraja_vazenja_p(self):
        return self.datum_kr_vaz_pop

    def __str__(self):
        return f"Popust {self.sifra_pop} - {self.pred_cena_pop} RSD"


class SePrimenjuje(models.Model):
    STATUS_CHOICES = (
        ('aktivan', 'Aktivan'),
        ('istekao', 'Istekao'),
    )

    artikal = models.ForeignKey(Artikal, on_delete=models.CASCADE, db_column='ARTIKAL_sifra_a')
    popust = models.ForeignKey(Popust, on_delete=models.CASCADE, db_column='POPUST_sifra_pop')
    status_pi = models.CharField(max_length=30, choices=STATUS_CHOICES, default='aktivan')

    class Meta:
        db_table = 'se_primenjuje'
        unique_together = ('artikal', 'popust')


class Temperatura(models.Model):
    sifra_tm = models.AutoField(primary_key=True)
    vrednost_tp = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperatura u Celzijusima")
    vreme_merenja_tp = models.DateTimeField(auto_now_add=True)

    skladiste = models.ForeignKey(Skladiste, on_delete=models.CASCADE, db_column='SKLADISTE_sifra_sk', related_name='temperature')

    class Meta:
        db_table = 'temperatura'

    @property
    def id_merenja(self):
        return self.sifra_tm

    @property
    def vrednost(self):
        return self.vrednost_tp

    @property
    def vreme_merenja(self):
        return self.vreme_merenja_tp

    def __str__(self):
        return f"Temperatura {self.vrednost_tp}°C u {self.skladiste.mesto_sk}"


class Notifikacija(models.Model):
    sifra_n = models.AutoField(primary_key=True)
    poruka_n = models.CharField(max_length=1000)
    datum_n = models.DateTimeField(auto_now_add=True)
    procitana_n = models.BooleanField(default=False)
    link_n = models.CharField(max_length=300, blank=True, null=True)

    korisnici = models.ManyToManyField(User, through='SeSalje', blank=True, related_name='notifikacije')

    class Meta:
        db_table = 'notifikacija'
        ordering = ['-datum_n']

    @property
    def korisnik(self):
        """Kompatibilnost sa starim 1:N pristupom - vraća prvog povezanog korisnika."""
        return self.korisnici.first()

    def __str__(self):
        return f"Notifikacija {self.sifra_n} - {self.datum_n.strftime('%d.%m.%Y')}"


class SeSalje(models.Model):
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE, db_column='KORISNIK_sifra_k')
    notifikacija = models.ForeignKey(Notifikacija, on_delete=models.CASCADE, db_column='NOTIFIKACIJA_sifra_n')

    class Meta:
        db_table = 'se_salje'
        unique_together = ('korisnik', 'notifikacija')


# ============================================================================
# Logistički podsistem (Vozilo, Ruta, Vozac, Isporuka, Servis, Upozorenje) nije
# deo nijednog EER-a koji je do sada dat (ni starog ni ovog novog) - pripada
# podsistemu logističkog koordinatora i namerno je ostavljen netaknut.
# ============================================================================

class Vozilo(models.Model):
    sifra_v = models.AutoField(primary_key=True)
    marka = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    registracija = models.DateField(null=False, blank=True)
    kapacitet = models.DecimalField(max_digits=10, decimal_places=2)
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

    def get_all_vozaci(request):
        vozaci = Vozac.objects.all()
        return vozaci

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Isporuka(models.Model):
    sifra_i = models.AutoField(primary_key=True)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, null=True)
    vozilo = models.ForeignKey(Vozilo, on_delete=models.CASCADE, null=True)
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

    tip = models.CharField(max_length=50, choices=tip_choices)
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
        if (self.vrednost > self.max_granica) & (self.vrednost < self.min_granica):
            return Upozorenje(isporuka=self.isporuka, tip='temperatura', poruka='Temperatura je izvan opsega.')

    class Meta:
        db_table = 'temperaturaVozilo'
