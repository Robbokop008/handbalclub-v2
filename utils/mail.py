"""
utils/mail.py
--------------
Helperfuncties om e-mails te versturen via de mailserver van Hetzner: het
contactformulier, de orderbevestiging na een geslaagde betaling, een
wijziging van een afhaalmoment (acties), en de meldingen aan de club
(inschrijvingen, GDPR-verzoeken, annuleringen).

Elke mail bestaat uit een platte-tekstversie (hier opgebouwd) en een
HTML-versie in de clubstijl (templates/mail/). Mailprogramma's tonen de
HTML-versie; wie geen HTML toont of wil, krijgt de tekstversie - die
helpt ook tegen spamfilters, die een mail met enkel HTML wantrouwen.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid
from flask import current_app, has_request_context, render_template, request, url_for
from werkzeug.routing import BuildError

from models import actie_lijnen_per_moment


def _veilige_header_waarde(waarde):
    """Verwijdert regeleinden uit een waarde vóór die in een e-mailheader
    (Reply-To, Subject, ...) terechtkomt. Zonder dit zou gebruikersinvoer
    (bv. het e-mailadres/naam in een formulier) extra headers of een
    volledig nieuwe e-mailinhoud kunnen injecteren (header/CRLF-injectie)."""
    return (waarde or "").replace("\r", " ").replace("\n", " ").strip()


def _send(msg):
    """Verstuurt een bericht met club@ als afzender. Date en Message-ID zetten
    we zelf: Gmail vulde die vroeger aan, de mailserver van Hetzner niet
    noodzakelijk, en spamfilters rekenen ontbrekende headers aan."""
    config = current_app.config
    afzender = config["MAIL_FROM"]
    msg["From"] = formataddr((config["MAIL_FROM_NAME"], afzender))
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=afzender.split("@")[-1])

    # Timeout zodat een hangende mailserver het request (bv. de Stripe-webhook)
    # niet eindeloos laat wachten. Als envelope-afzender gebruiken we de
    # mailbox waarmee we inloggen: onbestelbare mails komen zo terug in
    # webmaster@ in plaats van via de forward van club@.
    with smtplib.SMTP(config["MAIL_SERVER"], config["MAIL_PORT"], timeout=15) as server:
        server.starttls()
        server.login(config["MAIL_USERNAME"], config["MAIL_PASSWORD"])
        server.send_message(msg, from_addr=config["MAIL_USERNAME"])


def _basis_url():
    """Adres van de site (zonder / op het einde) voor links in de mails: de
    vaste canonieke host in productie, anders het adres van het huidige
    request (lokaal), of leeg."""
    url = current_app.config.get("CANONICAL_BASE_URL")
    if not url and has_request_context():
        url = request.url_root
    return (url or "").rstrip("/")


def _admin_url(endpoint, **kwargs):
    """Volledige link naar een adminpagina (knop in de interne meldingen), of
    None als die niet op te bouwen is."""
    basis = _basis_url()
    try:
        return f"{basis}{url_for(endpoint, **kwargs)}" if basis else None
    except (RuntimeError, BuildError):
        return None


def _bericht(onderwerp, aan, tekst, html_template, reply_to=None, **context):
    """Bouwt een mail met tekst- en HTML-versie (multipart/alternative: de
    laatste versie is de voorkeur van het mailprogramma, dus HTML achteraan)."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = _veilige_header_waarde(onderwerp)
    msg["To"] = aan
    if reply_to:
        msg["Reply-To"] = _veilige_header_waarde(reply_to)
    html = render_template(html_template, onderwerp=onderwerp, basis_url=_basis_url(), **context)
    msg.attach(MIMEText(tekst, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def _melding(onderwerp, tekst, titel, gegevens, inleiding=None, bericht_titel=None, bericht=None,
             knop_url=None, knop_tekst=None, reply_to=None):
    """Interne melding aan de club (MAIL_ADMIN), zie templates/mail/_melding.html."""
    return _bericht(
        onderwerp, current_app.config["MAIL_ADMIN"], tekst, "mail/_melding.html", reply_to=reply_to,
        titel=titel, inleiding=inleiding, gegevens=gegevens, vrije_tekst_titel=bericht_titel, vrije_tekst=bericht,
        knop_url=knop_url, knop_tekst=knop_tekst,
    )


def send_contact_mail(name, email, message):
    """Stuurt een kopie van het contactformulier naar de clubmail."""
    tekst = f"""Nieuw bericht via het contactformulier

Naam: {name}
E-mail: {email}

Bericht:
{message}
"""
    _send(_melding(
        "Nieuw contactformulier bericht", tekst,
        titel="Nieuw bericht via het contactformulier",
        inleiding="Antwoord rechtstreeks op deze mail om de afzender te bereiken.",
        gegevens=[("Naam", name), ("E-mail", email)],
        bericht_titel="Bericht", bericht=message,
        reply_to=email,
    ))


def send_order_confirmation_mail(order):
    """Stuurt een orderbevestiging naar de klant na een geslaagde betaling."""
    body = f"""Beste {order.user.first_name} {order.user.last_name},

Bedankt voor je bestelling!

Bestelnummer: {order.order_id}

"""
    if order.lines:
        body += "Bestelling:\n"
    for line in order.lines:
        variant_label = ""
        if line.variant:
            variant_label = f" ({line.variant.color} / {line.variant.size})"
        body += f"- {line.product.product_name}{variant_label} x {line.quantity} (€{float(line.price):.2f})\n"
        if line.print_front:
            body += f"    Bedrukking voorkant: {line.print_front}\n"
        if line.print_back:
            body += f"    Bedrukking achterkant: {line.print_back}\n"

    if order.ticket_lines:
        if order.lines:
            body += "\n"
        body += "Tickets:\n"
        # Gegroepeerd per wedstrijd, in chronologische volgorde
        for wedstrijd, lijnen in _tickets_per_wedstrijd(order):
            body += f"\n{wedstrijd.titel}\n"
            body += f"  Datum: {wedstrijd.datum_tijd.strftime('%d/%m/%Y')} om {wedstrijd.datum_tijd.strftime('%H:%M')}\n"
            if wedstrijd.locatie:
                body += f"  Locatie: {wedstrijd.locatie}\n"
            for line in lijnen:
                body += f"  - {line.ticket_type.naam} x {line.quantity} (€{float(line.price):.2f})\n"

    if order.actie_lines:
        if order.lines or order.ticket_lines:
            body += "\n"
        body += "Afhalen:\n"
        for moment, lijnen in actie_lijnen_per_moment(order.actie_lines):
            body += _afhaal_blok(moment, lijnen)

    body += f"\nSubtotaal: €{float(order.total_price):.2f}\n"
    if order.lines:
        body += f"Verzendkosten: {'Gratis' if not order.shipping_cost else '€' + f'{float(order.shipping_cost):.2f}'}\n"
    body += f"Totaal: €{order.total_paid:.2f}\n\n"

    if order.ticket_lines:
        body += (
            "TOEGANG TOT DE WEDSTRIJD\n"
            f"Je staat op de naamlijst onder de naam {order.user.first_name} {order.user.last_name} "
            f"(bestelnummer {order.order_id}). Toon deze e-mail aan de ingang van de sporthal "
            "om binnen te gaan of je tickets op te halen. Je hoeft niets af te drukken.\n\n"
        )
    if order.actie_lines:
        body += (
            "AFHALEN\n"
            "Kom je bestelling afhalen op het gekozen moment en adres. Vermeld daar je naam "
            f"({order.user.first_name} {order.user.last_name}) of bestelnummer {order.order_id}.\n\n"
        )
    if order.lines:
        body += "We gaan meteen met je bestelling aan de slag."
    elif order.actie_lines:
        body += "Tot bij het afhalen!"
    else:
        body += "Tot in de sporthal!"

    enkel_tickets = order.ticket_lines and not order.lines and not order.actie_lines
    onderwerp = f"{'Ticketbevestiging' if enkel_tickets else 'Bestelbevestiging'} #{order.order_id}"
    _send(_bericht(
        onderwerp, order.user.email, body, "mail/bestelbevestiging.html",
        order=order, tickets_per_wedstrijd=_tickets_per_wedstrijd(order),
    ))


def _tickets_per_wedstrijd(order):
    """[(wedstrijd, [ticketregels])], chronologisch."""
    per_wedstrijd = {}
    for line in order.ticket_lines:
        per_wedstrijd.setdefault(line.wedstrijd, []).append(line)
    return [(w, per_wedstrijd[w]) for w in sorted(per_wedstrijd, key=lambda w: w.datum_tijd)]


def _afhaal_blok(moment, lijnen):
    """Tekstblok met één actie, haar afhaalmoment en de bestelde artikelen."""
    blok = f"\n{moment.actie.titel}\n"
    blok += f"  Afhalen: {moment.label}\n"
    blok += f"  Adres: {moment.adres}\n"
    for line in lijnen:
        blok += f"  - {line.variant.volledige_naam} x {line.quantity} (€{float(line.price):.2f})\n"
    return blok


def send_afhaalmoment_wijziging_mail(order, moment, bericht):
    """Meldt een koper dat er iets veranderd is aan zijn afhaalmoment: het
    moment zelf werd verplaatst/gewijzigd of geschrapt, of de admin zette de
    bestelling op een ander moment. 'bericht' is de uitleg van de admin."""
    lijnen = [line for line in order.actie_lines if line.moment_id == moment.id]
    body = f"""Beste {order.user.first_name} {order.user.last_name},

Er is iets gewijzigd aan het afhalen van je bestelling #{order.order_id} bij {moment.actie.titel}.

"""
    if bericht:
        body += f"{bericht}\n\n"
    if moment.is_active:
        body += "Je afhaalmoment is nu:\n"
        body += _afhaal_blok(moment, lijnen)
    else:
        body += (
            f"Het afhaalmoment {moment.label} op {moment.adres} gaat niet door. "
            "De club neemt contact met je op over het verdere verloop.\n"
        )
    body += "\nVragen? Antwoord gerust op deze e-mail.\n"

    _send(_bericht(
        f"Wijziging afhaalmoment - {moment.actie.titel} (bestelling #{order.order_id})",
        order.user.email, body, "mail/afhaalmoment_wijziging.html",
        order=order, moment=moment, lijnen=lijnen, bericht=bericht,
    ))


def send_admin_cancellation_mail(order):
    """Meldt de admin dat een bestelling geannuleerd is."""
    body = f"""Admin,

De bestelling met bestelnummer {order.order_id} van gebruiker {order.user.first_name} {order.user.last_name} ({order.user.email}) is geannuleerd.

Dit is een automatische melding, gelieve hier niet op te antwoorden.
"""
    _send(_melding(
        f"Bestelling #{order.order_id} geannuleerd", body,
        titel=f"Bestelling #{order.order_id} geannuleerd",
        inleiding="Deze bestelling werd in het adminpaneel op Geannuleerd gezet.",
        gegevens=[
            ("Bestelnummer", f"#{order.order_id}"),
            ("Klant", f"{order.user.first_name} {order.user.last_name}"),
            ("E-mail", order.user.email),
            ("Totaal", f"€{order.total_paid:.2f}"),
        ],
        knop_url=_admin_url("admin.view_order", order_id=order.order_id), knop_tekst="Bekijk de bestelling",
    ))


def send_inschrijving_notification(inschrijving):
    """Meldt de club dat er een nieuwe inschrijving is binnengekomen."""
    geboortedatum_tekst = inschrijving.geboortedatum.strftime('%d/%m/%Y') if inschrijving.geboortedatum else '-'
    speler_naam = f"{inschrijving.voornaam_speler or ''} {inschrijving.achternaam_speler or ''}".strip() or '-'

    body = f"""Nieuwe inschrijving ontvangen!

Categorie: {inschrijving.categorie or '-'}

Speler: {speler_naam}
Geboortedatum: {geboortedatum_tekst}
Geboorteplaats: {inschrijving.geboorteplaats or '-'}
Adres: {inschrijving.straat_nr or '-'}, {inschrijving.postcode or ''} {inschrijving.gemeente or ''}

E-mail: {inschrijving.email or '-'}
Gsm: {inschrijving.telefoon or '-'}

Hoe leren kennen: {inschrijving.hoe_gehoord or '-'}
School: {inschrijving.school or '-'}
Opmerkingen: {inschrijving.opmerkingen or '-'}

Ingediend op: {inschrijving.aangemaakt_op.strftime('%d/%m/%Y %H:%M')}
"""
    adres = f"{inschrijving.straat_nr or ''}, {inschrijving.postcode or ''} {inschrijving.gemeente or ''}".strip(" ,")
    _send(_melding(
        f"Nieuwe inschrijving: {speler_naam} ({inschrijving.categorie or '-'})", body,
        titel="Nieuwe inschrijving",
        inleiding=f"{speler_naam} schreef zich in voor {inschrijving.categorie or 'een onbekende categorie'}.",
        gegevens=[
            ("Categorie", inschrijving.categorie),
            ("Speler", speler_naam),
            ("Geboortedatum", geboortedatum_tekst if inschrijving.geboortedatum else None),
            ("Geboorteplaats", inschrijving.geboorteplaats),
            ("Adres", adres),
            ("E-mail", inschrijving.email),
            ("Gsm", inschrijving.telefoon),
            ("Hoe leren kennen", inschrijving.hoe_gehoord),
            ("School", inschrijving.school),
            ("Opmerkingen", inschrijving.opmerkingen),
            ("Ingediend op", inschrijving.aangemaakt_op.strftime('%d/%m/%Y %H:%M')),
        ],
        knop_url=_admin_url("admin.view_inschrijving", inschrijving_id=inschrijving.id), knop_tekst="Open de inschrijving",
        reply_to=inschrijving.email,
    ))


def send_vergeet_mij_notification(verzoek):
    """Meldt de club dat er een GDPR-verwijderingsverzoek is binnengekomen."""
    body = f"""Nieuw GDPR-verzoek: gegevens verwijderen

Naam: {verzoek.naam}
E-mail: {verzoek.email}
Lidnummer: {verzoek.lidnummer or '-'}
Opmerking: {verzoek.opmerking or '-'}

Ingediend op: {verzoek.aangemaakt_op.strftime('%d/%m/%Y %H:%M')}

Gelieve dit verzoek binnen de wettelijke termijn te verwerken.
"""
    _send(_melding(
        f"GDPR-verzoek: {verzoek.naam}", body,
        titel="Nieuw GDPR-verzoek: gegevens verwijderen",
        inleiding="Gelieve dit verzoek binnen de wettelijke termijn te verwerken.",
        gegevens=[
            ("Naam", verzoek.naam),
            ("E-mail", verzoek.email),
            ("Lidnummer", verzoek.lidnummer),
            ("Ingediend op", verzoek.aangemaakt_op.strftime('%d/%m/%Y %H:%M')),
        ],
        bericht_titel="Opmerking" if verzoek.opmerking else None, bericht=verzoek.opmerking,
        knop_url=_admin_url("admin.view_gdpr_verzoek", verzoek_id=verzoek.id), knop_tekst="Open het verzoek",
        reply_to=verzoek.email,
    ))
