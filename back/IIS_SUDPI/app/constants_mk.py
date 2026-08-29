"""
Konstante podsistema finansijskog analitičara (FA).

Statične liste opcija za dropdown filtere i mape čitljivih naziva statusa.
Izdvojene iz `views_mk.py` da bi view ostao orkestracija (autorizacija ->
proračun -> serializer -> Response), a ne skladište literala. Sadržaj se ne
menja - iste vrednosti i redosled kao pre izdvajanja.
"""

# ========== ČITLJIVI NAZIVI STATUSA ==========

# Namerno se razlikuje od Faktura.STATUS_CHOICES (`get_status_f_display()`):
# choices opisuju stanje dokumenta ("Primljena"), a ovo opisuje šta se od
# korisnika očekuje ("Čeka verifikaciju"). Koristi ga `status_display`.
STATUS_FAKTURE_PRIKAZ = {
    'primljena': 'Čeka verifikaciju',
    'verifikovana': 'Čeka isplatu',
    'isplacena': 'Plaćeno',
    'odbijena': 'Odbačeno',
}


# ========== FILTERI: FAKTURE ==========

FAKTURE_STATUS_OPCIJE = [
    {'value': 'svi', 'label': 'Svi statusi'},
    {'value': 'primljena', 'label': 'Čeka verifikaciju'},
    {'value': 'verifikovana', 'label': 'Čeka isplatu'},
    {'value': 'isplacena', 'label': 'Plaćeno'},
    {'value': 'odbijena', 'label': 'Odbačeno'},
]

FAKTURE_DATUM_OPCIJE = [
    {'value': 'svi', 'label': 'Svi datumi'},
    {'value': 'danas', 'label': 'Danas'},
    {'value': 'ova_nedelja', 'label': 'Ova nedelja'},
    {'value': 'ovaj_mesec', 'label': 'Ovaj mesec'},
    {'value': 'poslednji_mesec', 'label': 'Prošli mesec'},
]


# ========== FILTERI: IZVEŠTAJI ==========

IZVESTAJI_STATUS_OPCIJE = [
    {'value': 'sve', 'label': 'Sve'},
    {'value': 'primljena', 'label': 'Primljeno'},
    {'value': 'verifikovana', 'label': 'Verifikovano'},
    {'value': 'isplacena', 'label': 'Isplaćeno'},
]

IZVESTAJI_PERIOD_OPCIJE = [
    {'value': 'sve', 'label': 'Sav period'},
    {'value': 'danas', 'label': 'Danas'},
    {'value': 'ova_nedelja', 'label': 'Ova nedelja'},
    {'value': 'ovaj_mesec', 'label': 'Ovaj mesec'},
    {'value': 'poslednji_mesec', 'label': 'Prošli mesec'},
    {'value': 'poslednja_3_meseca', 'label': 'Poslednja 3 meseca'},
]

IZVESTAJI_GRUPIRANJE_OPCIJE = [
    {'value': 'proizvodu', 'label': 'Proizvodu'},
    {'value': 'dobavljacu', 'label': 'Dobavljaču'},
    {'value': 'kategoriji', 'label': 'Kategoriji'},
]


# ========== PENALI ==========

# Penal se smatra rešenim kada prođe ovoliko dana od evidentiranja. Isto
# pravilo koristi i filter u `penalties_list` (upit nad datum_p) i izračunati
# `status_display` u `PenalSerializer` - zato stoji na jednom mestu.
PENAL_DANI_DO_RESENJA = 30
PENAL_STATUS_RESEN = 'Rešen'
PENAL_STATUS_OBAVESTEN = 'Obavešten'

PENALI_STATUS_OPCIJE = [
    {'value': 'svi', 'label': 'Svi statusi'},
    {'value': 'resen', 'label': PENAL_STATUS_RESEN},
    {'value': 'obavesten', 'label': PENAL_STATUS_OBAVESTEN},
]
