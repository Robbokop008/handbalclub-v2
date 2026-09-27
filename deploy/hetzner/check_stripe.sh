#!/bin/bash
# Diagnose voor "Invalid signature" op de Stripe-webhook, uit te voeren via
# konsoleH's Cron job Manager (handmatig via het afspeel-icoontje). Schrijft
# naar stripe_check.log in de projectmap en herstart op het einde de app,
# zodat een aangepaste .env zeker ingelezen wordt.
#
# Toont de webhook secret NOOIT volledig: enkel begin, einde en lengte, om
# te vergelijken met wat Stripe toont bij "Reveal signing secret".

PROJECT=/usr/home/drf93y/handbalsint-truiden
PYTHON=/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/python
FCGI=/usr/home/drf93y/public_html/handbalclub-public/app.fcgi
LOG=$PROJECT/stripe_check.log

cd "$PROJECT" || exit 1

{
    echo "=== Check gestart: $(date) ==="
    echo "Servertijd (UTC): $(date -u '+%Y-%m-%d %H:%M:%S') - vergelijk met de echte tijd, max. 5 min verschil"

    echo
    echo "=== .env laatst gewijzigd ==="
    ls -l .env

    echo
    echo "=== Draaiende app-processen (gestart vóór de .env-wijziging = oude secret) ==="
    ps -u "$(whoami)" -o pid,lstart,args | grep "[h]andbalclub-public/app.fcgi" || echo "(geen)"

    echo
    echo "=== Webhook secret zoals de app die inleest ==="
    "$PYTHON" - <<'EOF'
import os
# Staat de variabele al in de omgeving vóór .env ingelezen wordt, dan
# negeert load_dotenv() de waarde uit .env (override=False).
print("al gezet buiten .env:", "STRIPE_WEBHOOK_SECRET" in os.environ)
import config
s = config.Config.STRIPE_WEBHOOK_SECRET
if not s:
    print("LEEG of ontbreekt!")
else:
    print("begin:", s[:10], "| einde:", s[-4:], "| lengte:", len(s))
    print("spaties/witruimte:", s != s.strip())
    print("aanhalingstekens:", any(c in s for c in "\"'"))
    print("begint met whsec_:", s.startswith("whsec_"))
k = config.Config.STRIPE_API_KEY or ""
print("API key soort:", k[:8] + "..." if k else "LEEG")
EOF

    echo
    echo "=== App herstarten ==="
    touch "$FCGI"
    pkill -f "handbalclub-public/app.fcgi" && echo "processen gestopt" || echo "geen processen om te stoppen"

    echo
    echo "=== Klaar: $(date) ==="
} > "$LOG" 2>&1
