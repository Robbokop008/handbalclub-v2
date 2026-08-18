"""
utils/site_text.py
-------------------
Admin-bewerkbare tekstfragmenten die verspreid over de site in templates
gebruikt worden - zie models.SiteText.

De teksten zijn gegroepeerd per pagina (SITE_TEXT_PAGINAS) zodat de admin-
omgeving per pagina kan bewerken i.p.v. één lange lijst met alle velden
door elkaar - zie routes/admin.py (site_teksten / edit_site_tekst).

Elk veld heeft een type ("text" - kort, één regel, platte tekst - of
"html" - langere/rijkere tekst met opmaak, opgeslagen als gesaniteerde
HTML en bewerkt via de Quill-editor, zie templates/admin/site_tekst_form.html)
en een standaardwaarde. Zolang een admin niets aangepast heeft, of als een
veld leeggelaten wordt bij het opslaan, valt de site terug op die
standaardtekst - zo kan een lege admin-invoer nooit een kapotte/lege
sectie opleveren.
"""

from extensions import db
from models import SiteText


def _tekst(sleutel, omschrijving, standaard):
    """Kort, éénregelig platte-tekstveld (titels, labels, ...)."""
    return (sleutel, omschrijving, standaard, "text")


def _html(sleutel, omschrijving, standaard):
    """Langer/rijker tekstveld (meerdere paragrafen, opsommingen, links) -
    bewerkt via de Quill rich-text-editor, gesaniteerd bij opslaan (zie
    utils/sanitize.sanitize_html) en gerenderd met |safe."""
    return (sleutel, omschrijving, standaard, "html")


# Elke pagina: een slug (gebruikt in de admin-URL), een leesbaar label, het
# endpoint om "Bekijk pagina" naartoe te linken (None als de pagina niet
# rechtstreeks te bezoeken is, bv. een bedankt-/bevestigingspagina), een
# optionele opmerking daarover, en de tekstvelden (zie _tekst/_html
# hierboven) die op die pagina gebruikt worden.
SITE_TEXT_PAGINAS = [
    {
        "slug": "home",
        "label": "Homepage",
        "endpoint": "main.home",
        "opmerking": "De hero (foto + kalender-/nieuwskaart) is vaste opmaak; enkel de 3 promotiekaarten eronder zijn hier bewerkbaar.",
        "velden": [
            _tekst("promo_ballenbaasjes_titel", "Ballenbaasjes-kaart: titel", "sporten op maat van onze kleinste vriendjes"),
            _tekst("promo_ballenbaasjes_subtitel", "Ballenbaasjes-kaart: ondertitel", "3-6 jaar"),
            _tekst("promo_flanders_titel", "Flanders Trophy-kaart: titel", "grootste handbaltornooi in BeNeLux"),
            _tekst("promo_flanders_subtitel", "Flanders Trophy-kaart: ondertitel", "tijdens het Paasweekend"),
            _tekst("promo_fit_titel", "FIT-Handbal-kaart: titel", "sporten op maat van onze grootste vrienden"),
            _tekst("promo_fit_subtitel", "FIT-Handbal-kaart: ondertitel", "enthousiaste sportievelingen, niet-handballers en ex-spelers"),
        ],
    },
    {
        "slug": "club",
        "label": "Club",
        "endpoint": "club.overzicht",
        "velden": [
            _tekst("club_hero_titel", "Hero-titel", "Passie met ambitie!"),
            _tekst("club_missie_titel", "Missie-kaart: titel", "Onze missie"),
            _html("club_missie_tekst", "Missie-kaart: tekst", (
                '<p>Handbal Sint-Truiden is een <strong>familiale club</strong> die kinderen, jongeren, senioren, recreanten en sympathisanten de mogelijkheid biedt om handbal op een <strong>positieve, kwaliteitsvolle en sfeervolle</strong> manier te beleven.</p>'
                '<p>We zijn een familiale club met ambitieus karakter!</p>'
            )),
            _tekst("club_visie_titel", "Visie-kaart: titel", "Onze visie"),
            _html("club_visie_tekst", "Visie-kaart: tekst", (
                '<p>De kwaliteitsvolle jeugdwerking van onze club streeft naar goede handballers met focus op twee essentiële waarde: <strong>"respect en inzet"</strong></p>'
                '<p>Dames- en herenploeg grotendeels op basis van de <strong>eigen jeugdwerking</strong> laten werken binnen een kwaliteitsvolle omkadering.</p>'
                '<p>Het Fit-Handbal wil recreanten laten <strong>genieten van onze mooie sport</strong> waarbij fysieke fitheid, sociale contacten en amusement centraal staan.</p>'
                '<p>In G-handbal bieden wij <strong>bijzondere sporters de mogelijkheid om te handballen</strong> en dit voor iedereen vanaf 6 jaar met een mentale en/of lichte fysieke beperking.</p>'
                '<p>De clubwerking wordt gedragen door <strong>vrijwilligers</strong> uit alle groepen van de club.</p>'
            )),
            _html("club_contact_tekst", "Accordion 'Contact': tekst", '<p>Heb je een vraag voor het bestuur, de jeugdwerking of iemand anders binnen de club? Stuur ons een bericht via het <a href="/contact">contactformulier</a>.</p>'),
            _html("club_bestuur_tekst", "Accordion 'Bestuur': tekst", "<p>Binnenkort meer over de samenstelling van het bestuur van Handbal Sint-Truiden.</p>"),
            _html("club_historiek_tekst", "Accordion 'Historiek': tekst", "<p>Binnenkort meer over de geschiedenis van Handbal Sint-Truiden.</p>"),
            _html("club_api_tekst", "Accordion 'API': tekst", (
                '<p>Als club vinden we het enorm belangrijk dat je in een veilige omgeving van onze prachtige sport kan genieten.</p>'
                '<p>Binnen onze club hebben we ook een Aanspreekpunt voor je persoonlijke integriteit (API). Zij kent de hele club, is heel toegankelijk, maar maakt geen deel uit van het Bestuur en kan autonoom problemen behandelen in alle discretie.</p>'
                '<p>Voor Handbal Sint-Truiden is dit Mary Verlinden, <a href="mailto:mary.verlinden@gmail.com">mary.verlinden@gmail.com</a> (0473 209 435).</p>'
                '<p><strong>1. Als je een acute situatie van ernstig grensoverschrijdend gedrag wil melden:</strong></p>'
                '<ul>'
                '<li>LET OP! Bel in een levensbedreigende situatie de politie of medische hulp via het noodnummer 112.</li>'
                '<li>Neem contact op met de politie, of consulteer de <a href="https://1712.be" target="_blank" rel="noopener">Hulplijn 1712</a>.</li>'
                '<li>Je kan in alle vertrouwen terecht bij een arts.</li>'
                '</ul>'
                '<p><strong>2. Ben je slachtoffer van grensoverschrijdend gedrag bij een handbalactiviteit</strong> of heb je als betrokkene (docent, cursusverantwoordelijke, (mede)cursist, ouder, enz.) iets gehoord, gezien of meegemaakt, een vermoeden, vaststelling of onthulling over grensoverschrijdend gedrag?</p>'
                '<ul><li>Contacteer onze API: Mary Verlinden, <a href="mailto:mary.verlinden@gmail.com">mary.verlinden@gmail.com</a> (0473 209 435).</li></ul>'
                '<p>De API bekijkt eerst de melding intern en legt zo snel mogelijk het eerste contact met de melder. Er wordt geluisterd naar de verwachtingen en informatie gegeven over wat mogelijke verdere stappen zijn. Elke vraag/melding wordt discreet behandeld en verloopt in voortdurende afstemming met de melder.</p>'
                '<p><strong>Sport Vlaanderen: Richtlijn API</strong></p>'
                '<ul>'
                '<li>Wanneer je als sporter, trainer, vrijwilliger, bestuurder, ouder, aanspreekpersoon, … betrokken bent bij een case grensoverschrijdend gedrag in een sportclub, kan je in eerste instantie terecht bij de club-API (vertrouwenspersoon van de sportclub) voor advies en ondersteuning.</li>'
                '<li>Voel je je onzeker om de gekende (vertrouwde) structuren/personen iets te melden en heb je toch nood aan een luisterend oor? Heb je iets gehoord, gezien of meegemaakt, en weet je niet hoe hiermee omgaan? Bij een vraag, verontrusting, vermoeden, vaststelling of onthulling van grensoverschrijdend gedrag … kan je in vertrouwen terecht bij onderstaande professionele instanties: de <a href="https://1712.be" target="_blank" rel="noopener">Hulplijn 1712</a>. Ervaren hulpverleners staan je bij. Ze geven je informatie en advies of verwijzen je door naar verdere hulp. Je kan hen bellen, mailen of chatten. Je kan kinderen en jongeren doorverwijzen naar <a href="https://awel.be" target="_blank" rel="noopener">Awel</a>. Zij kunnen Awel elke dag telefonisch bereiken, chatten, mailen of hun vraag op het forum stellen. Kinderen en jongeren hebben ook de chatmogelijkheid. Men kan anoniem chatten met een gespecialiseerde medewerker op maandag-, woensdag- en donderdagavond. Naast deze kanalen en openingsuren, kan men terecht op het nummer 106, 24 uur op 24 uur of via chat.</li>'
                '</ul>'
                '<p>Stop it Now! wil preventieve hulp bieden aan mensen met pedofiele gevoelens of hun naasten. Maak je je zorgen over eigen gevoelens of gedrag of maak je je zorgen over de gevoelens of het gedrag van iemand in je directe sociale omgeving? Neem vertrouwelijk, anoniem en gratis contact op met <a href="https://www.stopitnow.be" target="_blank" rel="noopener">Stop it Now!</a> op het nummer 0800 200 50 of chat of mail naar <a href="mailto:vragen@stopitnow.be">vragen@stopitnow.be</a>.</p>'
            )),
            _html("club_verzekering_intro", "Accordion 'Verzekeringsformulier': intro (boven de infographic)", (
                '<p>Heb je een (sport)ongeval opgelopen tijdens een handbalactiviteit? Download dan het Ethias verzekeringsformulier!</p>'
                '<p>Hieronder vind je alvast wat je moet doen:</p>'
            )),
            _tekst("club_verzekering_download_label", "Accordion 'Verzekeringsformulier': downloadlink-tekst", "Download het verzekeringsformulier"),
        ],
    },
    {
        "slug": "kalender",
        "label": "Kalender",
        "endpoint": "kalender.overzicht",
        "opmerking": "De wedstrijdenkalender zelf komt rechtstreeks van Spond en is hier niet bewerkbaar.",
        "velden": [
            _html("kalender_trainingen_ghandbal", "Trainingen > G-Handbal: uren", '<ul><li>&lt;12 jaar: zondag 10:00u - 11:00u, sporthal Trudo</li><li>&gt;12 jaar: zondag 11:00u - 12:00u, sporthal Trudo</li></ul>'),
            _html("kalender_trainingen_ballenbaasjes", "Trainingen > De Ballenbaasjes: uren", (
                '<ul>'
                '<li>1e kleuterklas: woensdag 16:15u - 17:15u, mattenzaal sporthal Trudo</li>'
                '<li>2e kleuterklas: woensdag 17:30u - 18:30u, sporthal Trudo</li>'
                '<li>3e kleuterklas: woensdag 17:30u - 18:30u*, sporthal Trudo</li>'
                '<li>*met aansluitend kleuterhandbal voor de 3e kleuterklas: 18:30u - 19:00u, sporthal Trudo</li>'
                '</ul>'
            )),
            _html("kalender_trainingen_jm0810", "Trainingen > JM08 & JM10: uren", "<p>Binnenkort meer over de trainingsuren van JM08 &amp; JM10.</p>"),
            _html("kalender_trainingen_jm12", "Trainingen > JM12: uren", "<p>Binnenkort meer over de trainingsuren van JM12.</p>"),
            _tekst("kalender_trainingen_cta_titel", "Trainingen: titel van het gele kaartje", "Wil je handbal eens proberen?"),
            _html("kalender_trainingen_cta_tekst", "Trainingen: tekst van het gele kaartje", (
                '<p>Train <strong>1 maand gratis</strong> mee en ontdek welke talenten jij hebt op het veld!</p>'
                '<p>Voor meer info: <a href="mailto:jeugd@handbalsint-truiden.be">jeugd@handbalsint-truiden.be</a></p>'
                '<p>Check de trainingsuren en kom eens langs.</p>'
            )),
            _html("kalender_evenementen_tekst", "Evenementen: tekst", (
                '<p>Onze club is jaarlijks aanwezig op verschillende evenementen. Op die manier houden we club financieel gezond! We rekenen hiervoor ook op de hulp van onze vrijwilligers.</p>'
                '<p>Wil je zelf ook eens komen helpen? Laat het ons weten!</p>'
                '<p>Voor meer info: <a href="mailto:evenementen@handbalsint-truiden.be">evenementen@handbalsint-truiden.be</a></p>'
                '<p>Hier is alvast een overzicht van onze vaste afspraken:</p>'
                '<p><strong>26 december - 30 december: JUMPING (Mechelen)</strong><br>Beleef de internationale jumping van vlak bij de wedstrijdpistes! We werken elke dag met 2 shiften.</p>'
                '<p><strong>Februari: Karnaval Tongeren</strong><br>Kom mee achter de toog tijdens de geweldige karnavalsfeer van Tongeren (zaterdagavond op Alaaf of zondag op de kidsday).</p>'
                '<p><strong>Maart: het Schlagerfestival in de Trixxo-arena</strong><br>Elk jaar mag onze club de toog doen tijdens het schlagerfestival. Ga mee los achter de toog, met onze heren en dames! Wees snel, want de plaatsen zijn beperkt!</p>'
            )),
            _tekst("kalender_evenementen_cta_titel", "Evenementen: titel van het gele kaartje", "Flanders Handball Trophy"),
            _html("kalender_evenementen_cta_tekst", "Evenementen: tekst van het gele kaartje", (
                '<p>Elke jaar tijdens het paasweekend organiseert onze club het <strong>grootste handbaltornooi van de BeNeLux</strong>.</p>'
                '<p>Een uniek evenement met een ongeëvenaarde sfeer, waarbij uiteraard elke helpende hand welkom is.</p>'
                '<p>Mis dit niet en wees onder de indruk van onze clubprestatie!</p>'
            )),
        ],
    },
    {
        "slug": "jeugd",
        "label": "Jeugd",
        "endpoint": "jeugd.overzicht",
        "velden": [
            _tekst("jeugd_beleidsplan_titel", "'Beleidsplan Jeugd'-kaart: titel", "Beleidsplan Jeugd"),
            _html("jeugd_beleidsplan_tekst", "'Beleidsplan Jeugd'-kaart: tekst", (
                '<p>De jeugdafdeling van HB Sint-Truiden wil zoveel mogelijk kinderen kennis laten maken met de handbalsport.</p>'
                '<p>Het wil daarbij ook jongeren van 3-18 jaar opleiden en begeleiden in functie van doorstroming naar de eerste ploeg. De jongeren die uit onze jeugdwerking komen zullen blijk geven van een kwalitatief sterke handbalopleiding en dragen waarden zoals Inzet en Respect hoog in het vaandel.</p>'
            )),
            _tekst("jeugd_interesse_titel", "'Interesse?'-kaart: titel", "Interesse?"),
            _html("jeugd_interesse_tekst", "'Interesse?'-kaart: tekst", (
                '<p>Wat fijn dat jij (of je kind) interesse hebt in handbal!</p>'
                '<p>Via <a href="/jeugd/inschrijving">dit inschrijvingsformulier</a> kan je je gegevens doorgeven waardoor je automatisch geregistreerd bent voor de gratis promotie-verzekering (<strong>1 maand gratis meetrainen</strong>)!</p>'
            )),
            _tekst("jeugd_ballenbaasjes_titel", "Ballenbaasjes-kaart: titel", "sporten op maat van onze kleinste vriendjes"),
            _tekst("jeugd_ballenbaasjes_subtitel", "Ballenbaasjes-kaart: ondertitel", "verhalend bewegen voor kinderen van 3-6 jaar"),
            _html("jeugd_jm0810_tekst", "Accordion 'JM08 & JM10': tekst", (
                '<p>Jongens en meisjes van het 1e - 4e leerjaar, spelen tot 2x per maand een tornooitje.</p>'
                '<p>Trainingen zijn op de volgende momenten:</p>'
                '<ul><li>woensdag: 17:30u - 19:00u (Trudohal, Sint-Jansstraat)</li><li>zaterdag: 11:00u - 12:30u (Lago, Olympialaan)</li></ul>'
            )),
            _html("jeugd_jm12_tekst", "Accordion 'JM12': tekst", (
                '<p>Jongens en meisjes van het 5e - 6e leerjaar.</p>'
                '<p>Trainingen zijn op de volgende momenten:</p>'
                '<ul><li>maandag: 18:00u - 19:30u (Trudohal, Sint-Jansstraat)</li><li>woensdag: 17:30u - 19:00u (Trudohal, Sint-Jansstraat)</li><li>donderdag: 17:30u - 19:30u (sporthal Jodenstraat)</li></ul>'
            )),
            _html("jeugd_jm14_tekst", "Accordion 'JM14': tekst", (
                '<p>Jongens en meisjes van het 1e - 2e middelbaar.</p>'
                '<p>Trainingen zijn op de volgende momenten:</p>'
                '<ul><li>maandag: 18:00u - 19:30u (sporthal Jodenstraat)</li><li>donderdag: 17:30u - 19:30u (Lago, Olympialaan)</li></ul>'
            )),
            _html("jeugd_welzijn_tekst", "Accordion 'Het welzijn van de speler': tekst", "<p>Via onderstaande link vind je meer info over gezond sport, verzekering, API, ethisch verantwoord sporten en het antidopingbeleid van de VHV.</p>"),
            _tekst("jeugd_welzijn_link_label", "Accordion 'Het welzijn van de speler': linktekst", "VHV: Het welzijn van de speler"),
        ],
    },
    {
        "slug": "ghandbal",
        "label": "G-Handbal",
        "endpoint": "ghandbal.index",
        "velden": [
            _tekst("ghandbal_hero_titel", "Hero-titel", "Handbal voor iedereen!"),
            _tekst("ghandbal_card_titel", "Kaart: titel", "handbal voor buitenGewone spelers"),
            _html("ghandbal_card_tekst", "Kaart: tekst", (
                '<p>Sinds 21 oktober 2018 startte HB Sint-Truiden als eerste Limburgse club met G-handbal.</p>'
                '<p>Onze doelgroep zijn bijzondere sporters vanaf 6 jaar met ASS of een lichte fysieke of mentale beperking en die graag in ploegverband een balsport willen doen.</p>'
                '<p>Zij trainen wekelijks onder professionele begeleiding van een kinesiste en Licenciate LO. Sommige bijzondere sporters spelen handbal onder begeleiding van een persoonlijke buddy.</p>'
                '<p>Sinds 2024 is er een vrijblijvende competitie opgestart met Vlaanderen en Nederlands Limburg.</p>'
                '<p>Meer info? Contacteer ons via: <a href="mailto:ghandbal@handbalsint-truiden.be">ghandbal@handbalsint-truiden.be</a></p>'
            )),
            _tekst("ghandbal_inschrijving_label", "Kaart: inschrijvingslink-tekst", "Inschrijven voor G-Handbal"),
            _tekst("ghandbal_training_titel", "Trainingssectie: titel", "Eens komen kijken of meespelen?"),
            _html("ghandbal_training_tekst", "Trainingssectie: tekst", (
                '<p>Dat kan! Onze buitenGewone sporters trainen elke zondag in de Trudohal (Sint-Jansstraat).</p>'
                '<ul><li>&lt;12 jaar: 10:00u - 11:00u</li><li>&gt;12 jaar: 11:00u - 12:00u</li></ul>'
            )),
        ],
    },
    {
        "slug": "fithandbal",
        "label": "FIT-Handbal",
        "endpoint": "fithandbal.index",
        "velden": [
            _tekst("fithandbal_hero_titel", "Hero-titel", "Handbal voor iedereen!"),
            _tekst("fithandbal_card_titel", "Kaart: titel", "handbal voor 30-plussers"),
            _html("fithandbal_card_tekst", "Kaart: tekst", (
                '<p>Fithandbal is een nieuw concept, uitgewerkt door de Vlaamse Handbalvereniging i.s.m. de Vlaamse Overheid, om 30-plussers de kans te geven om één keer per week recreatief aan handbal te doen.</p>'
                '<p>Het fithandbalaanbod: wekelijks een sportieve activiteit die verdeeld zal zijn in drie blokken:</p>'
                '<p><strong>PULSE</strong>: cardiovasculaire training</p>'
                '<p><strong>POWER</strong>: stabilisatie- en krachtcircuit</p>'
                '<p><strong>PLAY</strong>: handbaloefeningen en wedstrijdvormen</p>'
                '<p>Met deze activiteit willen we dus een nieuwe vorm van handbalbeleving op de kaart zetten. Het is niet alleen vernieuwend omdat we ons richten op een andere leeftijdsgroep, maar ook omdat we ons concentreren op de aspecten: <strong>fysieke fitheid, sociale contacten en amusement</strong>.</p>'
                '<p>Dames en heren trainen en spelen gemengd en er is de mogelijkheid om een aantal keren per jaar met je fithandbalploeg vrijblijvend te kunnen deelnemen aan een (driehoeks)tornooi, waarbij je speelt tegen ploegen die hetzelfde concept uitvoeren. Tijdens deze tornooien staan amusement en fair-play centraal.</p>'
            )),
            _tekst("fithandbal_training_titel", "Trainingssectie: titel", "Eens komen kijken of meespelen?"),
            _html("fithandbal_training_tekst", "Trainingssectie: tekst", (
                '<p>Dat kan! Onze FIT-handballers trainen elke woensdag in de Trudohal (Sint-Jansstraat)<br>20:30u - 21:45u</p>'
                '<p>Aansluitend kunnen we dan met zijn allen nog gezellig wat drinken, de zogenaamde 3e helft.<br>Voor meer info: <a href="mailto:fithandbal@handbalsint-truiden.be">fithandbal@handbalsint-truiden.be</a></p>'
            )),
        ],
    },
    {
        "slug": "contact",
        "label": "Contact",
        "endpoint": "main.contact",
        "velden": [
            _tekst("contact_hero_titel", "Hero-titel", "Contacteer ons"),
            _tekst("contact_hero_intro", "Hero-intro", "Heb je vragen of hulp nodig? Stuur ons een bericht en we nemen binnenkort contact met je op."),
        ],
    },
    {
        "slug": "inschrijving",
        "label": "Inschrijving nieuwe speler",
        "endpoint": "jeugd.inschrijving",
        "velden": [
            _tekst("inschrijving_hero_titel", "Hero-titel", "Inschrijving nieuwe speler"),
            _tekst("inschrijving_hero_intro", "Hero-intro", "Vul onderstaand formulier in om je (of je kind) in te schrijven. We nemen zo snel mogelijk contact met je op."),
        ],
    },
    {
        "slug": "inschrijving-bedankt",
        "label": "Inschrijving nieuwe speler — bedanktpagina",
        "endpoint": None,
        "opmerking": "Deze pagina is enkel zichtbaar na een echte inschrijving, en kan dus niet rechtstreeks bezocht worden.",
        "velden": [
            _tekst("inschrijving_bedankt_titel", "Titel", "Bedankt voor je inschrijving!"),
        ],
    },
    {
        "slug": "login",
        "label": "Inloggen",
        "endpoint": "auth.login",
        "velden": [
            _tekst("login_hero_titel", "Hero-titel", "Veilig inloggen op uw account"),
            _tekst("login_hero_subtitel", "Hero-subtekst", "Log in om verder te gaan."),
        ],
    },
    {
        "slug": "register",
        "label": "Registreren",
        "endpoint": "auth.register",
        "velden": [
            _tekst("register_hero_titel", "Hero-titel", "Start je avontuur met Handbal Sint-Truiden"),
            _tekst("register_hero_subtitel", "Hero-subtekst", "Registreer nu om onze webshop te ontdekken en bestellingen te plaatsen."),
        ],
    },
    {
        "slug": "profiel",
        "label": "Profiel",
        "endpoint": "auth.profile",
        "velden": [
            _tekst("profiel_hero_titel", "Hero-titel", "Jouw profiel, verfijnd"),
            _tekst("profiel_hero_subtitel", "Hero-subtekst", "Beheer je account, bekijk recente aankopen en houd je lidmaatschapsgegevens up-to-date in één elegant controlecentrum."),
        ],
    },
    {
        "slug": "account-instellingen",
        "label": "Accountinstellingen",
        "endpoint": "auth.account_settings",
        "velden": [
            _tekst("account_instellingen_hero_titel", "Hero-titel", "Accountinstellingen"),
            _tekst("account_instellingen_hero_subtitel", "Hero-subtekst", "Update uw accountgegevens hier."),
        ],
    },
    {
        "slug": "webshop-producten",
        "label": "Webshop — productoverzicht",
        "endpoint": "shop.products",
        "velden": [
            _tekst("shop_hero_titel", "Hero-titel", "Ontdek onze collectie"),
        ],
    },
    {
        "slug": "webshop-winkelmandje",
        "label": "Webshop — winkelmandje",
        "endpoint": "shop.cart",
        "velden": [
            _tekst("cart_hero_titel", "Hero-titel (winkelmandje gevuld)", "Je winkelmandje"),
            _tekst("cart_hero_subtitel", "Hero-subtekst (winkelmandje gevuld)", "Beoordeel je geselecteerde items, pas aantallen aan en ga naar de checkout wanneer je klaar bent."),
            _tekst("cart_leeg_hero_titel", "Hero-titel (winkelmandje leeg)", "Je winkelmandje is leeg"),
            _tekst("cart_leeg_hero_subtitel", "Hero-subtekst (winkelmandje leeg)", "Bekijk onze producten en voeg items toe aan je winkelmandje."),
        ],
    },
    {
        "slug": "webshop-checkout-success",
        "label": "Webshop — bestelling geplaatst",
        "endpoint": None,
        "opmerking": "Deze pagina is enkel zichtbaar na een echte bestelling, en kan dus niet rechtstreeks bezocht worden.",
        "velden": [
            _tekst("checkout_success_hero_titel", "Hero-titel", "Bedankt!"),
            _tekst("checkout_success_hero_subtitel", "Hero-subtekst", "Uw bestelling is succesvol geplaatst. Een bevestigingsmail is naar u verzonden met de bestelgegevens. Wij zullen uw artikelen zo spoedig mogelijk verwerken en verzenden."),
        ],
    },
    {
        "slug": "footer",
        "label": "Footer",
        "endpoint": "main.home",
        "opmerking": "Verschijnt onderaan elke pagina van de site.",
        "velden": [
            _tekst("footer_over_ons_tekst", "Tekst onder 'Over ons'", "Leer meer over onze club en onze waarden"),
        ],
    },
]


def vind_pagina(slug):
    """Geeft het paginadict met dit slug terug, of None als het niet bestaat."""
    for pagina in SITE_TEXT_PAGINAS:
        if pagina["slug"] == slug:
            return pagina
    return None


def _alle_velden():
    for pagina in SITE_TEXT_PAGINAS:
        for sleutel, omschrijving, standaard_waarde, veld_type in pagina["velden"]:
            yield sleutel, omschrijving, standaard_waarde, veld_type


DEFAULT_VALUES = {sleutel: waarde for sleutel, _omschrijving, waarde, _veld_type in _alle_velden()}


def get_site_teksten():
    """Geeft een dict {sleutel: waarde} terug voor gebruik in templates, met fallback op de standaardwaarde."""
    rijen = {r.sleutel: r.waarde for r in SiteText.query.all()}
    ontbrekend = [(s, o, w) for s, o, w, _t in _alle_velden() if s not in rijen]
    if ontbrekend:
        for sleutel, omschrijving, waarde in ontbrekend:
            db.session.add(SiteText(sleutel=sleutel, omschrijving=omschrijving, waarde=waarde))
            rijen[sleutel] = waarde
        db.session.commit()
    return {**DEFAULT_VALUES, **rijen}
