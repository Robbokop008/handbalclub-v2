"""
utils/mail.py
--------------
Helperfuncties om e-mails te versturen via Gmail SMTP: het contactformulier,
de orderbevestiging na een geslaagde betaling, en de melding aan de admin
wanneer een bestelling geannuleerd wordt.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def _veilige_header_waarde(waarde):
    """Verwijdert regeleinden uit een waarde vóór die in een e-mailheader
    (Reply-To, Subject, ...) terechtkomt. Zonder dit zou gebruikersinvoer
    (bv. het e-mailadres/naam in een formulier) extra headers of een
    volledig nieuwe e-mailinhoud kunnen injecteren (header/CRLF-injectie)."""
    return (waarde or "").replace("\r", " ").replace("\n", " ").strip()


def _send(msg):
    gmail_user = current_app.config["GMAIL_USER"]
    gmail_password = current_app.config["GMAIL_APP_PASSWORD"]
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)


def send_contact_mail(name, email, message):
    """Stuurt een kopie van het contactformulier naar de clubmail."""
    gmail_user = current_app.config["GMAIL_USER"]

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg["Subject"] = "Nieuw contactformulier bericht"
    msg["Reply-To"] = _veilige_header_waarde(email)

    body = f"""
    Naam: {name}
    Email: {email}

    Bericht:
    {message}
    """
    msg.attach(MIMEText(body, "plain"))
    _send(msg)


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
        per_wedstrijd = {}
        for line in order.ticket_lines:
            per_wedstrijd.setdefault(line.wedstrijd, []).append(line)
        for wedstrijd in sorted(per_wedstrijd, key=lambda w: w.datum_tijd):
            body += f"\n{wedstrijd.titel}\n"
            body += f"  Datum: {wedstrijd.datum_tijd.strftime('%d/%m/%Y')} om {wedstrijd.datum_tijd.strftime('%H:%M')}\n"
            if wedstrijd.locatie:
                body += f"  Locatie: {wedstrijd.locatie}\n"
            for line in per_wedstrijd[wedstrijd]:
                body += f"  - {line.ticket_type.naam} x {line.quantity} (€{float(line.price):.2f})\n"

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
    if order.lines:
        body += "We gaan meteen met je bestelling aan de slag."
    else:
        body += "Tot in de sporthal!"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"{'Ticketbevestiging' if order.ticket_lines and not order.lines else 'Bestelbevestiging'} #{order.order_id}"
    msg["From"] = current_app.config["GMAIL_USER"]
    msg["To"] = order.user.email
    _send(msg)


def send_admin_cancellation_mail(order):
    """Meldt de admin dat een bestelling geannuleerd is."""
    gmail_user = current_app.config["GMAIL_USER"]

    body = f"""Admin,

De bestelling met bestelnummer {order.order_id} van gebruiker {order.user.first_name} {order.user.last_name} ({order.user.email}) is geannuleerd.

Dit is een automatische melding, gelieve hier niet op te antwoorden.
"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"Bestelling #{order.order_id} geannuleerd"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    _send(msg)


def send_inschrijving_notification(inschrijving):
    """Meldt de club dat er een nieuwe inschrijving is binnengekomen."""
    gmail_user = current_app.config["GMAIL_USER"]

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
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = _veilige_header_waarde(f"Nieuwe inschrijving: {speler_naam} ({inschrijving.categorie or '-'})")
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg["Reply-To"] = _veilige_header_waarde(inschrijving.email)
    _send(msg)


def send_vergeet_mij_notification(verzoek):
    """Meldt de club dat er een GDPR-verwijderingsverzoek is binnengekomen."""
    gmail_user = current_app.config["GMAIL_USER"]

    body = f"""Nieuw GDPR-verzoek: gegevens verwijderen

Naam: {verzoek.naam}
E-mail: {verzoek.email}
Lidnummer: {verzoek.lidnummer or '-'}
Opmerking: {verzoek.opmerking or '-'}

Ingediend op: {verzoek.aangemaakt_op.strftime('%d/%m/%Y %H:%M')}

Gelieve dit verzoek binnen de wettelijke termijn te verwerken.
"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = _veilige_header_waarde(f"GDPR-verzoek: {verzoek.naam}")
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg["Reply-To"] = _veilige_header_waarde(verzoek.email)
    _send(msg)
