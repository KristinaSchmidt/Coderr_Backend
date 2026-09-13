# Coderr Backend

REST-Backend für das Abschlussprojekt **Coderr** der Developer Akademie.
Das Repository enthält ausschließlich das Django/DRF-Backend. Das Frontend
wird separat verwendet und nicht mit diesem Repository abgegeben.

## Verwendete Coderr-Version

- Coderr-Frontend: **Version 1.2.1**
- Frontend-Repository: `Developer-Akademie-Backendkurs/project.Coderr`
- Django: 5.2.6
- Django REST Framework: 3.16.1

## Voraussetzungen

- Python 3.12 oder neuer
- pip
- separat geklontes Coderr-Frontend

## Installation

Virtuelle Umgebung erstellen:

```bash
python -m venv .venv
```

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Pakete installieren und Projekt vorbereiten:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_guest
python manage.py runserver
```

Das Backend läuft anschließend unter `http://127.0.0.1:8000/`.

## Frontend-Konfiguration

In `shared/scripts/config.js` des Frontends müssen die URLs auf den lokalen
Django-Server zeigen:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/';
const STATIC_BASE_URL = 'http://127.0.0.1:8000/';
```

## Gastbenutzer

`python manage.py seed_guest` legt die benötigten Gast- und Testkonten
idempotent an.

| Typ | Benutzername | Passwort |
| --- | --- | --- |
| offizieller Customer-Gast | `andrey` | `asdasd` |
| offizieller Business-Gast | `kevin` | `asdasd24` |
| zusätzlicher Customer-Test | `kristina_customer` | `test1234` |
| zusätzlicher Business-Test | `kristina_business` | `test1234` |

## API-Endpunkte

Alle API-Routen beginnen mit `/api/`.

| Methode | Route | Berechtigung / Zweck |
| --- | --- | --- |
| POST | `/registration/` | Registrierung als `customer` oder `business` |
| POST | `/login/` | Login und Token-Ausgabe |
| GET | `/profile/<pk>/` | eigenes oder fremdes Profil abrufen, Login nötig |
| PATCH | `/profile/<pk>/` | nur eigenes Profil bearbeiten |
| GET | `/profiles/business/` | Liste aller Business-Profile |
| GET | `/profiles/customer/` | Liste aller Customer-Profile |
| GET | `/offers/` | öffentliche, paginierte Angebotsliste |
| POST | `/offers/` | Angebot mit genau drei Details, nur Business |
| GET | `/offers/<id>/` | einzelnes Angebot, Login nötig |
| PATCH | `/offers/<id>/` | nur Ersteller des Angebots |
| DELETE | `/offers/<id>/` | nur Ersteller, Antwort `204 No Content` |
| GET | `/offerdetails/<id>/` | vollständiges Angebotsdetail, Login nötig |
| GET | `/orders/` | Bestellungen des angemeldeten Users |
| POST | `/orders/` | Bestellung aus `offer_detail_id`, nur Customer |
| PATCH | `/orders/<id>/` | Status ändern, nur zuständiger Business-User |
| GET | `/order-count/<business_user_id>/` | offene Bestellungen zählen |
| GET | `/completed-order-count/<business_user_id>/` | abgeschlossene Bestellungen zählen |
| GET | `/reviews/` | Bewertungen mit Filter und Sortierung |
| POST | `/reviews/` | Bewertung erstellen, nur Customer |
| PATCH | `/reviews/<id>/` | nur Ersteller der Bewertung |
| DELETE | `/reviews/<id>/` | nur Ersteller, Antwort `204 No Content` |
| GET | `/base-info/` | Startseiten-Statistiken |

## Wichtige API-Eigenschaften

### Profile

Profilantworten enthalten die in der Endpoint-Dokumentation definierten
Felder. Leere Textfelder werden als leerer String und nicht als `null`
ausgegeben. Die E-Mail-Adresse kann beim eigenen Profil per `PATCH`
aktualisiert werden. Customer-Listen verwenden das dokumentierte Feld
`uploaded_at`, Business-Listen die dafür vorgesehenen Business-Felder.

### Angebote

`GET /offers/` unterstützt:

- `creator_id`
- `min_price`
- `max_delivery_time`
- `ordering=updated_at`, `ordering=-updated_at`, `ordering=min_price`
  oder `ordering=-min_price`
- `search`
- `page_size`

Die Listen- und Detailansicht eines Angebots gibt bei `details` nur `id` und
`url` zurück. Beim Erstellen und Aktualisieren wird dagegen die vollständige
Liste der Angebotsdetails mit `id`, `title`, `revisions`,
`delivery_time_in_days`, `price`, `features` und `offer_type` ausgegeben.

Beim Erstellen eines Angebots müssen genau die drei Typen `basic`, `standard`
und `premium` vorhanden sein. Bei `PATCH` können einzelne Felder und einzelne
Angebotsdetails aktualisiert werden. Bereits vorhandene Detail-IDs bleiben
erhalten.

### Bestellungen

Eine Bestellung wird aus einer vorhandenen `offer_detail_id` erstellt. Die
relevanten Angebotsdaten werden beim Erstellen in die Bestellung übernommen,
damit die Bestellung später unverändert bleibt, wenn das Angebot bearbeitet
wird. Nur Customer können Bestellungen anlegen. Nur der zuständige
Business-User kann den Status auf `in_progress`, `completed` oder `cancelled`
ändern.

### Bewertungen

Nur Customer können Bewertungen erstellen. Pro Customer und Business-User ist
nur eine Bewertung zulässig. `GET /reviews/` unterstützt die Filter
`business_user_id` und `reviewer_id` sowie Sortierung nach `updated_at` oder
`rating`.

### Zeitstempel

Das Projekt verwendet UTC. Dadurch werden API-Zeitstempel im erwarteten
ISO-8601-Format ausgegeben, zum Beispiel `2026-09-13T19:25:00Z`.

## HTTP-Statuscodes

Die Views verwenden die für die Aufgabe vorgesehenen Statuscodes:

- `200 OK` für erfolgreiche Abfragen und Aktualisierungen
- `201 Created` für neu erstellte Ressourcen
- `204 No Content` für erfolgreiches Löschen
- `400 Bad Request` bei ungültigen oder unvollständigen Daten
- `401 Unauthorized` ohne notwendige Authentifizierung
- `403 Forbidden` bei fehlender Berechtigung
- `404 Not Found` für nicht vorhandene Ressourcen

## Projektstruktur

```text
Coderr_Backend/
├── auth_app/
│   └── api/
├── offers_app/
│   └── api/
├── orders_app/
│   └── api/
├── reviews_app/
│   └── api/
├── core/
├── manage.py
├── requirements.txt
└── README.md
```

Jede App besitzt einen eigenen `api`-Ordner mit den jeweils benötigten
Serializern, Views, URLs und Permissions. Die zentrale URL-Konfiguration liegt
in `core/urls.py`.

## Tests und Coverage

Komplette Tests ausführen:

```bash
python manage.py test
```

Coverage erzeugen:

```bash
coverage run manage.py test
coverage report
coverage html
```

Die `.coveragerc` nimmt Migrationen, Tests und reinen Django-Boilerplate-Code
aus der fachlichen Coverage aus. Ziel ist mindestens **95 % Coverage** des
eigenen Anwendungscodes.

## Repository-Hinweise

Nicht in Git eingecheckt werden unter anderem:

- `.venv/`, `venv/`, `env/`
- `db.sqlite3` und andere SQLite-Dateien
- `media/`
- Coverage-Ausgaben und IDE-Dateien

Dadurch enthält das Repository nur den für die Abgabe benötigten Backend-Code.
