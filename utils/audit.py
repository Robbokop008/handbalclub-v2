from flask import g

from extensions import db
from models import AuditLog


def log_action(action, description):
    """Schrijft een auditlog-regel weg. Wordt aangeroepen vanuit een route
    die met @admin_required beveiligd is (g.user is dan altijd gezet).

    action: korte machine-tag, bv. "product.add"
    description: volledige, leesbare Nederlandse zin, bv.
        "Product 'Trainingsshirt' toegevoegd"

    Commit niet zelf: de aanroepende route commit sowieso al na de
    eigenlijke wijziging, zodat de log altijd in dezelfde transactie zit
    als de actie die hij beschrijft (of allebei lukken, of allebei niet).
    """
    actor = getattr(g, "user", None)
    actor_name = f"{actor.first_name} {actor.last_name} ({actor.username})" if actor else "Onbekend"

    db.session.add(AuditLog(
        user_id=actor.user_id if actor else None,
        actor_name=actor_name,
        action=action,
        description=description,
    ))
