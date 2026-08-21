"""
scripts/seed_legal_pages.py
-----------------------------
Eenmalig seed-script: zet de wettelijk verplichte webshop-informatie
(bedrijfsgegevens, herroepingsrecht/retourbeleid, privacyverklaring) om in
twee Page-rijen ("algemene-voorwaarden" en "privacybeleid-webshop"), zodat
ze via /pagina/<slug> getoond worden en nadien via de admin bewerkbaar
zijn. De inhoud is 1-op-1 overgenomen uit het document met de wettelijke
verplichtingen dat de club heeft aangeleverd.

In tegenstelling tot scripts/seed_pages.py (dat enkel het legacy
body_html-veld vulde) maakt dit script meteen ook een PageBlock aan, want
templates/pages/view.html toont page.blocks - body_html wordt niet meer
gerenderd sinds de blokken-page-builder er is (zie models.Page-docstring).

Idempotent: bestaande blokken van deze twee pagina's worden vervangen door
de inhoud hieronder in plaats van dubbels aan te maken.

Gebruik:
    python scripts/seed_legal_pages.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import Page, PageBlock
from utils.sanitize import sanitize_html


PAGES = [
    {
        "slug": "algemene-voorwaarden",
        "title": "Algemene voorwaarden webshop",
        "html": """
            <h2>Bedrijfsgegevens</h2>
            <p>
                HB Sint-Truiden jm vzw<br>
                Kortenbosstraat 58<br>
                3800 Sint-Truiden<br>
                <a href="mailto:info@handbalsint-truiden.be">info@handbalsint-truiden.be</a><br>
                Ondernemingsnummer en BTW-nummer (vzw): BE 0430.144.817
            </p>

            <h2>Herroepingsrecht en annulering</h2>

            <h3>Niet-gepersonaliseerde artikelen</h3>
            <p>Voor niet-gepersonaliseerde artikelen beschikt u als consument over een wettelijk herroepingsrecht van 14 kalenderdagen, te rekenen vanaf de dag waarop u de goederen ontvangt.</p>
            <p>U kunt binnen deze termijn uw aankoop herroepen zonder hiervoor een reden te moeten opgeven.</p>
            <p>Om gebruik te maken van het herroepingsrecht kunt u ons een e-mail sturen via <a href="mailto:webshop@handbalsint-truiden.be">webshop@handbalsint-truiden.be</a>. Vermeld hierbij steeds duidelijk uw ordernummer en de artikelen die u wenst te retourneren.</p>
            <p>Na uw melding heeft u nog 14 kalenderdagen om de betreffende artikelen aan ons terug te bezorgen.</p>
            <p>De artikelen dienen, voor zover redelijkerwijs mogelijk, in hun oorspronkelijke staat te worden terugbezorgd. Indien een artikel meer werd gebruikt dan nodig is om de aard, kenmerken en werking ervan vast te stellen, kan een eventuele waardevermindering in rekening worden gebracht.</p>

            <h3>Gepersonaliseerde artikelen</h3>
            <p>Voor artikelen die volgens uw specificaties worden vervaardigd of gepersonaliseerd worden, bijvoorbeeld door middel van een naam, nummer, logo of andere persoonlijke bedrukking, is het wettelijke herroepingsrecht niet van toepassing.</p>
            <p>HB Sint-Truiden biedt evenwel vrijwillig de mogelijkheid om een bestelling van een gepersonaliseerd artikel tot 48 uur na het plaatsen van de bestelling te annuleren, op voorwaarde dat de productie of personalisatie nog niet werd aangevat.</p>
            <p>Een annulering moet binnen deze termijn per e-mail worden aangevraagd via <a href="mailto:webshop@handbalsint-truiden.be">webshop@handbalsint-truiden.be</a>, met duidelijke vermelding van het ordernummer.</p>
            <p>Deze vrijwillige annulatiemogelijkheid doet geen afbreuk aan uw wettelijke rechten wanneer een geleverd artikel beschadigd is, een productiefout bevat of niet overeenstemt met de geplaatste bestelling.</p>
        """,
    },
    {
        "slug": "privacybeleid-webshop",
        "title": "Privacyverklaring webshop",
        "html": """
            <p>HB Sint-Truiden hecht belang aan de bescherming van uw persoonsgegevens. Persoonsgegevens die via onze webshop worden verzameld, worden verwerkt in overeenstemming met de toepasselijke privacywetgeving, waaronder de Algemene Verordening Gegevensbescherming (AVG/GDPR).</p>

            <h2>Welke gegevens verwerken wij?</h2>
            <p>Bij het plaatsen en verwerken van een bestelling kunnen wij onder andere volgende gegevens verwerken:</p>
            <ul>
                <li>naam en voornaam;</li>
                <li>adresgegevens;</li>
                <li>e-mailadres en eventueel telefoonnummer;</li>
                <li>bestel- en leveringsgegevens;</li>
                <li>gegevens die nodig zijn voor personalisatie van artikelen;</li>
                <li>betaal- en facturatiegegevens.</li>
            </ul>

            <h2>Waarvoor gebruiken wij deze gegevens?</h2>
            <p>Uw persoonsgegevens worden uitsluitend verwerkt voor doeleinden die verband houden met onze webshop, waaronder:</p>
            <ul>
                <li>het registreren en uitvoeren van uw bestelling;</li>
                <li>betaling en facturatie;</li>
                <li>levering of afhaling van bestelde artikelen;</li>
                <li>personalisatie van bestelde artikelen;</li>
                <li>communicatie over uw bestelling;</li>
                <li>retourzendingen, klachten en klantenservice;</li>
                <li>het naleven van wettelijke en boekhoudkundige verplichtingen.</li>
            </ul>
            <p>Uw gegevens worden niet voor commerciële doeleinden aan derden verkocht.</p>

            <h2>Delen met derden</h2>
            <p>Wanneer dit noodzakelijk is voor de uitvoering van uw bestelling, kunnen bepaalde persoonsgegevens worden gedeeld met dienstverleners die voor ons optreden, zoals onze betalingsprovider, leverancier of drukker, webshop-/hostingprovider en eventuele bezorgdiensten.</p>
            <p>Wij delen daarbij uitsluitend de gegevens die noodzakelijk zijn voor de betreffende dienstverlening.</p>

            <h2>Bewaartermijn</h2>
            <p>Persoonsgegevens worden niet langer bewaard dan noodzakelijk voor het doel waarvoor ze werden verzameld, tenzij een langere bewaartermijn wettelijk verplicht is, bijvoorbeeld in het kader van boekhoudkundige verplichtingen.</p>

            <h2>Uw rechten</h2>
            <p>Overeenkomstig de GDPR heeft u onder bepaalde voorwaarden het recht om:</p>
            <ul>
                <li>uw persoonsgegevens in te kijken;</li>
                <li>onjuiste gegevens te laten verbeteren;</li>
                <li>uw gegevens te laten verwijderen;</li>
                <li>de verwerking van uw gegevens te laten beperken;</li>
                <li>bezwaar te maken tegen bepaalde verwerkingen;</li>
                <li>uw persoonsgegevens over te dragen wanneer dit van toepassing is.</li>
            </ul>
            <p>Voor vragen over uw persoonsgegevens of om een van deze rechten uit te oefenen, kunt u contact opnemen via <a href="mailto:webshop@handbalsint-truiden.be">webshop@handbalsint-truiden.be</a>.</p>
            <p>Indien u van mening bent dat uw persoonsgegevens niet correct worden verwerkt, heeft u tevens het recht om een klacht in te dienen bij de bevoegde toezichthoudende autoriteit.</p>
        """,
    },
]


def run():
    app = create_app("development")
    with app.app_context():
        for entry in PAGES:
            page = Page.query.filter_by(slug=entry["slug"]).first()
            if page is None:
                page = Page(slug=entry["slug"], title=entry["title"], is_published=True)
                db.session.add(page)
                db.session.flush()
                print(f"aangemaakt: {entry['slug']}")
            else:
                page.title = entry["title"]
                page.is_published = True
                PageBlock.query.filter_by(page_id=page.id).delete()
                print(f"bijgewerkt: {entry['slug']}")

            blok = PageBlock(
                page_id=page.id, block_type="rich_text", position=1,
                data={"html": sanitize_html(entry["html"])},
            )
            db.session.add(blok)

        db.session.commit()
        print(f"klaar - {len(PAGES)} pagina's verwerkt.")


if __name__ == "__main__":
    run()
