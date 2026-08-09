"""
utils/inschrijving.py
----------------------
Helpers voor het admin-bewerkbare inschrijvingsformulier (Jeugd/G-Handbal/
FIT-Handbal): labels + verplicht-status per veld (InschrijvingVeldConfig),
en de twee admin-beheerde keuzelijsten (InschrijvingCategorie,
HoeGehoordOptie). Elke lijst/config seedt zichzelf lazy met de
standaardwaarden uit models.py zodra ze voor het eerst opgevraagd wordt.
"""

from extensions import db
from models import (
    InschrijvingCategorie, HoeGehoordOptie, InschrijvingVeldConfig,
    DEFAULT_INSCHRIJVING_CATEGORIEEN, DEFAULT_HOE_GEHOORD_OPTIES, INSCHRIJVING_VELD_DEFINITIES,
)


def get_inschrijving_categorieen():
    """Geeft de lijst van InschrijvingCategorie-namen terug, geseed met de standaardlijst indien leeg."""
    if InschrijvingCategorie.query.count() == 0:
        for naam in DEFAULT_INSCHRIJVING_CATEGORIEEN:
            db.session.add(InschrijvingCategorie(naam=naam))
        db.session.commit()
    return [c.naam for c in InschrijvingCategorie.query.order_by(InschrijvingCategorie.id).all()]


def get_hoe_gehoord_opties():
    """Geeft de lijst van HoeGehoordOptie-namen terug, geseed met de standaardlijst indien leeg."""
    if HoeGehoordOptie.query.count() == 0:
        for naam in DEFAULT_HOE_GEHOORD_OPTIES:
            db.session.add(HoeGehoordOptie(naam=naam))
        db.session.commit()
    return [o.naam for o in HoeGehoordOptie.query.order_by(HoeGehoordOptie.id).all()]


def get_inschrijving_veld_config():
    """Geeft een dict {veld_sleutel: InschrijvingVeldConfig} terug, geseed met de standaardconfig indien nodig."""
    rijen = {c.veld_sleutel: c for c in InschrijvingVeldConfig.query.all()}
    ontbrekend = [d for d in INSCHRIJVING_VELD_DEFINITIES if d[0] not in rijen]
    if ontbrekend:
        for veld_sleutel, label, verplicht in ontbrekend:
            config = InschrijvingVeldConfig(veld_sleutel=veld_sleutel, label=label, verplicht=verplicht)
            db.session.add(config)
            rijen[veld_sleutel] = config
        db.session.commit()
    return rijen
