"""
scripts/seed_legal_pages.py
-----------------------------
Eenmalig seed-script: zet de wettelijk verplichte webshop-informatie
(bedrijfsgegevens, herroepingsrecht/retourbeleid, privacyverklaring) om in
twee Page-rijen ("algemene-voorwaarden" en "privacybeleid"), zodat
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

from extensions import db
from models import Page, PageBlock
from scripts._common import get_app
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
        "slug": "privacybeleid",
        "title": "Privacyverklaring",
        "html": """
            <p>HB Sint-Truiden hecht belang aan de bescherming van uw persoonsgegevens. Deze verklaring geldt voor de volledige website handbalsint-truiden.be (niet enkel de webshop) en legt uit welke gegevens we verzamelen, waarom, en welke rechten u heeft. Persoonsgegevens worden verwerkt in overeenstemming met de toepasselijke privacywetgeving, waaronder de Algemene Verordening Gegevensbescherming (AVG/GDPR).</p>

            <h2>Wie is verantwoordelijk voor de verwerking?</h2>
            <p>
                HB Sint-Truiden jm vzw<br>
                Kortenbosstraat 58<br>
                3800 Sint-Truiden<br>
                <a href="mailto:info@handbalsint-truiden.be">info@handbalsint-truiden.be</a><br>
                Ondernemingsnummer en BTW-nummer (vzw): BE 0430.144.817
            </p>

            <h2>Welke gegevens verwerken wij, en waarom?</h2>

            <h3>Contactformulier</h3>
            <p>Wanneer u het contactformulier invult, verwerken wij uw naam, e-mailadres en bericht om uw vraag te kunnen beantwoorden.</p>

            <h3>Inschrijving Jeugd, G-Handbal of FIT-Handbal</h3>
            <p>Bij een inschrijving verwerken wij gegevens van de speler (naam, geboortedatum, geboorteplaats, adres) en contactgegevens (e-mailadres, telefoonnummer), en eventueel school en een vrije opmerking. Deze gegevens zijn nodig om de inschrijving te verwerken en de speler bij de juiste ploeg/categorie in te delen.</p>

            <h3>Gebruikersaccount en webshopbestellingen</h3>
            <p>Bij het aanmaken van een account en het plaatsen van een bestelling in onze webshop verwerken wij onder andere: naam, adresgegevens, e-mailadres en eventueel telefoonnummer, bestel- en leveringsgegevens, gegevens die nodig zijn voor personalisatie van artikelen, en betaal- en facturatiegegevens.</p>

            <h3>GDPR "vergeet mij"-verzoeken</h3>
            <p>Wanneer u een verzoek indient om uw gegevens te laten verwijderen, verwerken wij de gegevens die u daarbij zelf opgeeft (naam, e-mailadres, eventueel lidnummer en opmerking), enkel om dat verzoek te kunnen behandelen.</p>

            <p>Uw gegevens worden nooit voor commerciële doeleinden aan derden verkocht.</p>

            <h2>Cookies en Google Analytics</h2>
            <p>Onze website gebruikt zelf enkel strikt noodzakelijke cookies (bijvoorbeeld om u ingelogd te houden). Deze vereisen geen toestemming.</p>
            <p>Daarnaast gebruiken we, enkel met uw toestemming, Google Analytics om anonieme, geaggregeerde bezoekersstatistieken bij te houden (bv. welke pagina's bezocht worden, hoelang, en met welk type toestel) - dit helpt ons de website te verbeteren. IP-adressen worden hierbij geanonimiseerd. Deze gegevens worden verwerkt door Google Ireland Limited/Google LLC, die daarbij als verwerker optreedt; gegevens kunnen worden doorgegeven naar de Verenigde Staten in overeenstemming met de daarvoor geldende Europese waarborgen.</p>
            <p>Bij uw eerste bezoek vraagt een banner onderaan de pagina om uw toestemming. Zolang u niet expliciet akkoord gaat, wordt er geen Analytics-script geladen en worden er geen trackingcookies geplaatst. U kan uw keuze op elk moment wijzigen via de link "Cookie-instellingen" onderaan elke pagina.</p>

            <h2>Delen met derden</h2>
            <p>Wanneer dit noodzakelijk is voor de uitvoering van een bestelling of inschrijving, kunnen bepaalde persoonsgegevens worden gedeeld met dienstverleners die voor ons optreden, zoals onze betalingsprovider, leverancier of drukker, hostingprovider, en (enkel na toestemming) Google Analytics. Wij delen daarbij uitsluitend de gegevens die noodzakelijk zijn voor de betreffende dienstverlening.</p>

            <h2>Bewaartermijn</h2>
            <p>Persoonsgegevens worden niet langer bewaard dan noodzakelijk voor het doel waarvoor ze werden verzameld, tenzij een langere bewaartermijn wettelijk verplicht is, bijvoorbeeld in het kader van boekhoudkundige verplichtingen.</p>

            <h2>Uw rechten</h2>
            <p>Overeenkomstig de GDPR heeft u onder bepaalde voorwaarden het recht om:</p>
            <ul>
                <li>uw persoonsgegevens in te kijken;</li>
                <li>onjuiste gegevens te laten verbeteren;</li>
                <li>uw gegevens te laten verwijderen (zie ons <a href="/privacy/vergeet-mij">"vergeet mij"-formulier</a>);</li>
                <li>de verwerking van uw gegevens te laten beperken;</li>
                <li>bezwaar te maken tegen bepaalde verwerkingen;</li>
                <li>uw persoonsgegevens over te dragen wanneer dit van toepassing is;</li>
                <li>uw toestemming voor Google Analytics op elk moment in te trekken via "Cookie-instellingen" onderaan de pagina.</li>
            </ul>
            <p>Voor vragen over uw persoonsgegevens of om een van deze rechten uit te oefenen, kunt u contact opnemen via <a href="mailto:info@handbalsint-truiden.be">info@handbalsint-truiden.be</a>.</p>
            <p>Indien u van mening bent dat uw persoonsgegevens niet correct worden verwerkt, heeft u tevens het recht om een klacht in te dienen bij de Gegevensbeschermingsautoriteit (<a href="https://www.gegevensbeschermingsautoriteit.be" target="_blank" rel="noopener">gegevensbeschermingsautoriteit.be</a>).</p>
        """,
    },
]


def run():
    app = get_app()
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
