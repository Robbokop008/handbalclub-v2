#!/bin/bash
# Geeft een bestaande gebruiker adminrechten, uit te voeren via konsoleH's
# Cron job Manager (handmatig via het afspeel-icoontje, niet als terugkerende
# taak) - zelfde manier als update.sh. Het e-mailadres of de gebruikersnaam
# gaat als argument mee in het cron-commando:
#
#   bash /usr/home/drf93y/handbalsint-truiden/deploy/hetzner/make_admin.sh lisa@voorbeeld.be
#
# Schrijft het resultaat naar make_admin.log in de projectmap (via FTP te
# openen, naast app.py). Verwijder de cron job nadien weer.

PROJECT=/usr/home/drf93y/handbalsint-truiden
PYTHON=/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/python
LOG=$PROJECT/make_admin.log

cd "$PROJECT" || exit 1

{
    echo "=== make_admin gestart: $(date) ==="
    if [ -z "$1" ]; then
        echo "Geen gebruiker opgegeven: zet het e-mailadres of de gebruikersnaam achter het commando."
    else
        FLASK_CONFIG=production "$PYTHON" scripts/make_admin.py "$1"
    fi
    echo "=== Klaar: $(date) ==="
} > "$LOG" 2>&1
