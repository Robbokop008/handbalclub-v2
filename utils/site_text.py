"""
utils/site_text.py
-------------------
Kleine, admin-bewerkbare tekstfragmenten (hero-titels/introzinnen) die
verspreid over de site in templates gebruikt worden - zie models.SiteText.

Elke sleutel heeft een standaardwaarde (SITE_TEXT_DEFAULTS). Zolang een
admin niets aangepast heeft, of als een veld leeggelaten wordt bij het
opslaan, valt de site terug op die standaardtekst - zo kan een lege
admin-invoer nooit een kapotte/lege hero-sectie opleveren.
"""

from extensions import db
from models import SiteText

# (groep, sleutel, omschrijving, standaardwaarde)
SITE_TEXT_DEFAULTS = [
    ("Homepage", "home_hero_titel", "Hero-titel", "Handbal Sint-Truiden"),
    ("Homepage", "home_hero_subtitel", "Hero-subtekst", "Welkom bij de officiële website van Handbal Sint-Truiden!"),

    ("Contact", "contact_hero_titel", "Hero-titel", "Contacteer ons"),
    ("Contact", "contact_hero_intro", "Hero-intro", "Heb je vragen of hulp nodig? Stuur ons een bericht en we nemen binnenkort contact met je op."),

    ("Inschrijving nieuwe speler", "inschrijving_hero_titel", "Hero-titel", "Inschrijving nieuwe speler"),
    ("Inschrijving nieuwe speler", "inschrijving_hero_intro", "Hero-intro", "Vul onderstaand formulier in om je (of je kind) in te schrijven. We nemen zo snel mogelijk contact met je op."),
    ("Inschrijving nieuwe speler", "inschrijving_bedankt_titel", "Titel van de bedanktpagina", "Bedankt voor je inschrijving!"),

    ("Inloggen", "login_hero_titel", "Hero-titel", "Veilig inloggen op uw account"),
    ("Inloggen", "login_hero_subtitel", "Hero-subtekst", "Log in om verder te gaan."),

    ("Registreren", "register_hero_titel", "Hero-titel", "Start je avontuur met Handbal Sint-Truiden"),
    ("Registreren", "register_hero_subtitel", "Hero-subtekst", "Registreer nu om onze webshop te ontdekken en bestellingen te plaatsen."),

    ("Profiel", "profiel_hero_titel", "Hero-titel", "Jouw profiel, verfijnd"),
    ("Profiel", "profiel_hero_subtitel", "Hero-subtekst", "Beheer je account, bekijk recente aankopen en houd je lidmaatschapsgegevens up-to-date in één elegant controlecentrum."),

    ("Accountinstellingen", "account_instellingen_hero_titel", "Hero-titel", "Accountinstellingen"),
    ("Accountinstellingen", "account_instellingen_hero_subtitel", "Hero-subtekst", "Update uw accountgegevens hier."),

    ("Webshop", "shop_hero_titel", "Hero-titel (productenoverzicht)", "Ontdek onze collectie"),
    ("Webshop", "cart_hero_titel", "Hero-titel (winkelmandje, gevuld)", "Je winkelmandje"),
    ("Webshop", "cart_hero_subtitel", "Hero-subtekst (winkelmandje, gevuld)", "Beoordeel je geselecteerde items, pas aantallen aan en ga naar de checkout wanneer je klaar bent."),
    ("Webshop", "cart_leeg_hero_titel", "Hero-titel (winkelmandje, leeg)", "Je winkelmandje is leeg"),
    ("Webshop", "cart_leeg_hero_subtitel", "Hero-subtekst (winkelmandje, leeg)", "Bekijk onze producten en voeg items toe aan je winkelmandje."),
    ("Webshop", "checkout_success_hero_titel", "Hero-titel (orderbevestiging)", "Bedankt!"),
    ("Webshop", "checkout_success_hero_subtitel", "Hero-subtekst (orderbevestiging)", "Uw bestelling is succesvol geplaatst. Een bevestigingsmail is naar u verzonden met de bestelgegevens. Wij zullen uw artikelen zo spoedig mogelijk verwerken en verzenden."),

    ("Wedstrijdkalender", "kalender_hero_titel", "Hero-titel", "Wedstrijden"),
    ("Wedstrijdkalender", "kalender_hero_subtitel", "Hero-subtekst", "Onze wedstrijdkalender via Spond, rechtstreeks ingebed."),

    ("Footer", "footer_over_ons_tekst", "Tekst onder 'Over ons'", "Leer meer over onze club en onze waarden"),
    ("Footer", "footer_copyright", "Copyright-regel", "© 2026 Robbe Boyen. Alle rechten voorbehouden."),
]

DEFAULT_VALUES = {sleutel: waarde for _groep, sleutel, _omschrijving, waarde in SITE_TEXT_DEFAULTS}


def get_site_teksten():
    """Geeft een dict {sleutel: waarde} terug voor gebruik in templates, met fallback op de standaardwaarde."""
    rijen = {r.sleutel: r.waarde for r in SiteText.query.all()}
    ontbrekend = [d for d in SITE_TEXT_DEFAULTS if d[1] not in rijen]
    if ontbrekend:
        for _groep, sleutel, omschrijving, waarde in ontbrekend:
            db.session.add(SiteText(sleutel=sleutel, omschrijving=omschrijving, waarde=waarde))
            rijen[sleutel] = waarde
        db.session.commit()
    return {**DEFAULT_VALUES, **rijen}
