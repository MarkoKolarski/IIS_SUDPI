# IIS_SUDPI

Django (REST) + Oracle backend, React (CRA) frontend.

## Preduslovi

- Python 3.10+
- Node.js 18
- Pristup Oracle bazi (konekcija se podešava kroz `.env`)

## Backend (`back/IIS_SUDPI/`)

```bash
cd back/IIS_SUDPI
python -m venv .venv && .venv\Scripts\Activate.ps1   # ili: source .venv/bin/activate
pip install -r requirements.txt
```

`.env` (po uzoru na [.env.example](back/IIS_SUDPI/.env.example)):

```
DATABASE_ENGINE=django.db.backends.oracle
DATABASE_NAME=host:1521/servis
DATABASE_USER=...
DATABASE_PASSWORD=...
SECRET_KEY=...
DEBUG=True
```

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

API na `:8000`, Django admin na `/admin/`.

## Frontend (`front/IIS_SUDPI/`)

```bash
cd front/IIS_SUDPI
npm install
npm start          # :3000, proxy na :8000
```

## Seed podaci i prijava

Skripte se pokreću u SQL klijentu nad istim šemom korisnikom iz `.env`.
Prijava je po e-mailu (`mail_k`).

### `scripts/insert_diplomski.sql` — jedini seed usklađen s trenutnom šemom

Pokriva finansijsko-analitički podsistem. Nakon učitavanja loguje se
**finansijski analitičar**:

| E-mail | Lozinka |
|---|---|
| `1@gmail.com` | `1Qwertz*` |

> Skripta sama restartuje PK generatore na kraju (blok „RESETOVANJE GENERATORA
> PK VREDNOSTI") — bez toga prvi ORM `.create()` bez PK-a puca sa `ORA-00001`.
> Reset čiste baze: `scripts/dropALL.txt` → `migrate` → `insert_diplomski.sql`.

### Ostale uloge

`User.USER_TYPES` ([app/models.py](back/IIS_SUDPI/app/models.py)):
`finansijski_analiticar`, `nabavni_menadzer`, `kontrolor_kvaliteta`,
`skladisni_operater`, `logisticki_koordinator`, `administrator`. Frontend po
tipu preusmerava na `/dashboard-{fa,nm,kk,so,lk,admin}`.