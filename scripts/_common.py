"""
scripts/_common.py
--------------------
Gedeelde helper voor alle scripts/*.py: bouwt de Flask-app met dezelfde
config als de effectief draaiende site.

Voorheen deed elk script hardcoded create_app("development") - dat werkt
lokaal, maar op een hostingdienst is dat de VERKEERDE config: enkel
ProductionConfig (config.py) normaliseert bv. een oude 'postgres://'-
databank-URL naar 'postgresql://' (vereist door SQLAlchemy 1.4+), en zet
SESSION_COOKIE_SECURE correct. Met deze helper bepaalt de omgevingsvariabele
FLASK_CONFIG welke config gebruikt wordt (zelfde manier waarop wsgi.py voor
de site zelf "production" kiest) - standaard nog steeds "development",
zodat lokaal draaien zonder extra instellingen blijft werken.

Gebruik (in een script, na de gebruikelijke sys.path.insert):
    from scripts._common import get_app
    app = get_app()
    with app.app_context():
        ...
"""

import os

from sqlalchemy import inspect, text

from app import create_app
from extensions import db


def get_app():
    return create_app(os.environ.get("FLASK_CONFIG", "development"))


def add_column_if_missing(table, column, ddl_type):
    """Voegt 'column' toe aan 'table' via ALTER TABLE, tenzij ze al bestaat.
    Vereist een actieve app-context. Werkt op sqlite én postgresql (de 2
    databanken die deze site gebruikt, zie config.py) - vandaar SQLAlchemy's
    inspector i.p.v. sqlite-specifieke PRAGMA table_info."""
    kolommen = {kol["name"] for kol in inspect(db.engine).get_columns(table)}
    if column in kolommen:
        print(f"kolom '{column}' bestaat al op '{table}', overslaan")
        return
    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}"))
    db.session.commit()
    print(f"kolom '{column}' toegevoegd aan '{table}'")
