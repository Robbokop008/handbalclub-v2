#!/bin/bash
# Na elke update uit te voeren via konsoleH's Cron job Manager (handmatig via
# het afspeel-icoontje, niet als terugkerende taak) - zelfde manier als
# setup.sh, want er is geen interactieve SSH-shell op Webhosting M.
#
# Doet drie dingen en schrijft alles naar update.log in de projectmap (via
# FTP te openen, naast app.py):
#   1. toont de wijzigingsdatum van enkele kernbestanden, om te controleren
#      of de upload effectief gelukt is
#   2. draait scripts/update_site.py (nieuwe kolommen e.d., veilig herhaalbaar)
#   3. herstart de app door app.fcgi aan te raken: mod_fcgid start dan
#      nieuwe processen met de nieuwe code

PROJECT=/usr/home/drf93y/handbalsint-truiden
PYTHON=/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/python
FCGI=/usr/home/drf93y/public_html/handbalclub-public/app.fcgi
LOG=$PROJECT/update.log

cd "$PROJECT" || exit 1

{
    echo "=== Update gestart: $(date) ==="

    echo
    echo "=== Geüploade bestanden (controleer de datums) ==="
    ls -l app.py models.py routes/shop.py routes/admin.py templates/shop/products.html templates/shop/_ticket_kaarten.html

    echo
    echo "=== scripts/update_site.py ==="
    FLASK_CONFIG=production "$PYTHON" scripts/update_site.py

    echo
    echo "=== App herstarten ==="
    # Enkel app.fcgi aanraken volstaat niet: mod_fcgid laat de draaiende
    # processen (met de oude code in het geheugen) gewoon verder lopen. Dus
    # de processen van DEZE site stoppen - het pad matcht enkel handbalclub-
    # public, niet de app.fcgi van Flanders Trophy. Apache start bij het
    # volgende bezoek vanzelf een nieuw proces met de nieuwe code.
    echo "Draaiende processen vóór herstart:"
    ps -u "$(whoami)" -o pid,lstart,args | grep "[h]andbalclub-public/app.fcgi" || echo "(geen)"
    touch "$FCGI"
    pkill -f "handbalclub-public/app.fcgi" && echo "processen gestopt" || echo "geen processen om te stoppen"
    sleep 2
    echo "Draaiende processen na herstart (hoort leeg te zijn):"
    ps -u "$(whoami)" -o pid,lstart,args | grep "[h]andbalclub-public/app.fcgi" || echo "(geen)"

    echo
    echo "=== Klaar: $(date) ==="
} > "$LOG" 2>&1
