# Coderr Backend

Backend-API für das Abschlussprojekt **Coderr** der Developer Akademie.

## Frontend-Version

Getestet für das Coderr-Frontend **Version 1.2.1** aus:
`Developer-Akademie-Backendkurs/project.Coderr`

## Voraussetzungen

- Python 3.12 oder neuer
- pip
- das Coderr-Frontend separat geklont

## Installation

```bash
python -m venv .venv
```

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Abhängigkeiten installieren und Datenbank vorbereiten:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_guest
python manage.py runserver
```

## Frontend-Konfiguration

In `shared/scripts/config.js` des Frontends müssen Backend und statische Dateien auf den lokalen Django-Server zeigen:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/';
const STATIC_BASE_URL = 'http://127.0.0.1:8000/';
```

Für den Gastlogin werden durch `python manage.py seed_guest` diese Benutzer angelegt:

```text
Offizieller Customer-Gast:
username: andrey
password: asdasd

Offizieller Business-Gast:
username: kevin
password: asdasd24

Eigener Customer-Testzugang:
username: kristina_customer
password: test1234

Eigener Business-Testzugang:
username: kristina_business
password: test1234
```

Die beiden offiziellen Gastzugänge bleiben unverändert. Die beiden zusätzlichen Kristina-Testkonten können direkt über den normalen Login verwendet werden.

## API-Bereiche

- Registrierung und Login
- Profile für Customer und Business
- Angebote und Angebotsdetails
- Bestellungen
- Bewertungen
- Startseiten-Statistiken
- Bestellzähler für Business-Profile

## Tests

```bash
python manage.py test
coverage run manage.py test
coverage report
```

Die `.coveragerc` nimmt Migrationen, Tests und Django-Startdateien aus der fachlichen Coverage aus. Ziel ist mindestens 95 % Coverage des eigenen Anwendungscodes.

## Hinweise

Die SQLite-Datenbank wird bewusst nicht mit Git versioniert. Bilder liegen lokal unter `media/` und werden ebenfalls nicht eingecheckt.
