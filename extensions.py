"""
extensions.py
-------------
Hier worden Flask-extensies (zoals de database) één keer aangemaakt,
los van app.py en models.py. Dat voorkomt "circular import"-problemen:
zowel app.py als models.py kunnen dit bestand importeren zonder dat ze
elkaar nodig hebben.
"""

from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
csrf = CSRFProtect()

# De standaardlimieten gelden enkel voor formulieren/acties (POST e.d.), niet
# voor het gewoon bekijken van pagina's (GET/HEAD). Anders kreeg Googlebot -
# die vanaf een beperkt aantal IP's de hele site crawlt - na 50 pagina's per
# uur enkel nog 429's, zelfs op robots.txt en sitemap.xml. Google leest dat
# als een overbelaste server: het crawlt dan (bijna) niet meer en laat
# pagina's uit de index vallen. Routes met een eigen @limiter.limit (login,
# contact, ...) houden die gewoon.
limiter = Limiter(
    get_remote_address,
    default_limits=["500 per day", "50 per hour"],
    default_limits_exempt_when=lambda: request.method in ("GET", "HEAD"),
)
