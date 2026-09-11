#!/bin/bash
# Eenmalig installatiescript, uit te voeren via konsoleH's Cron job Manager
# (handmatig via het afspeel-icoontje, niet als terugkerende taak) - er is
# geen interactieve SSH-shell beschikbaar op Webhosting M, dit is de manier
# om toch commando's op de server te draaien. Zelfde recept als bij Flanders
# Trophy, met een eigen virtualenv-naam (handbalclub_v2) zodat de twee sites
# elkaar niet overschrijven.

python3 -m pip install --user --break-system-packages virtualenv
python3 -m virtualenv /usr/home/drf93y/virtualenvs/handbalclub_v2

# psycopg2-binary (PostgreSQL-driver) overslaan: de app gebruikt hier
# SQLite, en psycopg2-binary probeert anders C-code te compileren op de
# server, wat mislukt zonder de nodige compiler-bestanden (Python.h ontbreekt).
grep -v -i '^psycopg2' /usr/home/drf93y/handbalsint-truiden/requirements.txt > /usr/home/drf93y/requirements-server-handbalclub-v2.txt

/usr/home/drf93y/virtualenvs/handbalclub_v2/bin/pip install -r /usr/home/drf93y/requirements-server-handbalclub-v2.txt flup
