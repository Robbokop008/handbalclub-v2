# Adminhandleiding — website HB Sint-Truiden

Deze handleiding legt uit hoe je als admin de website van HB Sint-Truiden beheert: pagina's, nieuws, evenementen, teams, sponsors, de webshop, ledeninschrijvingen en GDPR-verzoeken. Ze is geschreven voor wie geen technische achtergrond heeft — je hebt enkel een browser nodig.

## Inhoud

1. [Inloggen en het dashboard](#1-inloggen-en-het-dashboard)
2. [Mijn account](#2-mijn-account)
3. [Pagina's beheren](#3-paginas-beheren)
4. [Navigatie beheren](#4-navigatie-beheren)
5. [Nieuws](#5-nieuws)
6. [Evenementen](#6-evenementen)
7. [Teams](#7-teams)
8. [Sponsors](#8-sponsors)
9. [Webshop](#9-webshop)
10. [Leden & inschrijvingen](#10-leden--inschrijvingen)
11. [GDPR-verzoeken](#11-gdpr-verzoeken)
12. [Veelgestelde vragen & tips](#12-veelgestelde-vragen--tips)

---

## Enkele afspraken die overal terugkomen

- **Opslaan gebeurt per pagina/formulier.** Er is geen automatisch opslaan: klik altijd op de knop onderaan (meestal **"Opslaan"** of **"Toevoegen"**) voor je weggaat, anders gaat je wijziging verloren.
- **Rode knoppen zijn gevaarlijk.** Rode knoppen ("Verwijderen", "Deactiveren", "Site in onderhoud zetten"...) hebben impact op de live site of zijn niet ongedaan te maken De site vraagt bij de belangrijkste altijd eerst een bevestiging ("Weet je het zeker?").
- **Producten en bestellingen worden nooit écht verwijderd**, enkel gedeactiveerd — zie [hoofdstuk 9](#9-webshop). Andere zaken (pagina's, nieuws, teams, sponsors evenementen...) verdwijnen wél definitief zodra je op "Verwijderen" klikt.
- **Afbeeldingen** uploaden kan overal via een "Bestand kiezen"-knop. Toegelaten formaten: JPG, PNG, GIF en WEBP.

---

## 1. Inloggen en het dashboard

Ga naar `/login` op de website en meld je aan met je gebruikersnaam en wachtwoord. Na inloggen zie je een gewone bezoeker van de site — het adminpaneel bereik je via `/admin`, of via de link **"Mijn account"** die als ingelogde admin overal bovenaan verschijnt.

Het adminpaneel heeft links een menu met vijf groepen:

| Menugroep | Wat je er beheert |
|---|---|
| **Content** | Pagina's, Nieuws, Evenementen, Sponsors, Teams, Navigatie |
| **Leden & inschrijvingen** | Gebruikers, Inschrijvingen, Inschrijvingsformulier |
| **Webshop** | Producten, Tickets, Bestellingen, Instellingen |
| **Beheer** | GDPR-verzoeken, Mijn account |

### Het dashboard

De eerste pagina na het openen van het adminpaneel (`/admin`) toont:

- **Onderhoudsmodus** — een schakelaar om de hele website tijdelijk offline te zetten. Bezoekers zien dan enkel een "even geduld"-pagina; jij blijft als admin wel overal aan kunnen. Gebruik dit enkel tijdens een grote update. Zet dit **altijd terug uit** zodra je klaar bent — vergeten uitzetten betekent dat de site voor iedereen "offline" blijft staan.
- **Actiepunten** — tegels met een aantal, die je rechtstreeks naar de plek brengen waar actie nodig is: onverwerkte GDPR-verzoeken, onverwerkte inschrijvingen, bestellingen die opvolging nodig hebben, en pagina's die nog niet gepubliceerd zijn.
- **Waarschuwingen** — signalen dat iets onvolledig of kapot staat, bv. een team zonder foto, een actief product zonder koopbare variant, of een navigatie-item dat naar iets verwijst dat niet meer bestaat. De site blijft hierdoor gewoon werken, maar het is de moeite om dit op te lossen.

---

## 2. Mijn account

Via **Beheer → Mijn account** wijzig je je eigen wachtwoord: vul je huidig wachtwoord in, en tweemaal je nieuwe wachtwoord. Een nieuw wachtwoord moet minstens 8 tekens lang zijn en minstens 1 cijfer en 1 speciaal teken bevatten.

Nieuwe admins voeg je toe via **Leden & inschrijvingen → Gebruikers** (zie [hoofdstuk 10](#10-leden--inschrijvingen)).

> **Wachtwoord vergeten?** Er is geen "wachtwoord vergeten"-link, en ook een andere admin kan jouw wachtwoord niet resetten via het adminpaneel. Zorg dus dat je je wachtwoord ergens veilig bewaart (bv. een wachtwoordmanager). Kom je er toch niet meer in, dan is er technische tussenkomst nodig — zie [hoofdstuk 12](#12-veelgestelde-vragen--tips).

---

## 3. Pagina's beheren

Via **Content → Pagina's** zie je alle bewerkbare pagina's van de site op één plek. Er zijn twee soorten, herkenbaar aan het badge in de kolom "Type":

| Type | Herkenbaar aan | Hoe bewerk je ze |
|---|---|---|
| **Contentpagina** | badge "Contentpagina" | Je bouwt de pagina zelf op uit blokken (zie 3.1) |
| **Vaste pagina** | badge "Vaste pagina" | Een vaste opbouw (bv. Homepage, Club, Contact); je past enkel de teksten/afbeeldingen erin aan (zie 3.2) |

### 3.1 Contentpagina's (blokken-editor)

Dit zijn pagina's die je zelf helemaal opbouwt, bv. voor een los project of een speciale actie. Klik op **"Nieuwe contentpagina toevoegen"** om te starten.

**Pagina-instellingen** (bovenaan het bewerkscherm, in te klappen):

- **Titel** — verschijnt als paginatitel.
- **Slug** — het stukje van de link na `/pagina/`, bv. `over-ons` geeft `/pagina/over-ons`. Vul je niets in, dan wordt dit automatisch van de titel afgeleid. Wijzig je de slug van een bestaande, al-gedeelde pagina, dan verandert de link — oude links die her en der staan (bv. gedeeld op sociale media) werken dan niet meer.
- **Afbeelding bovenaan (hero)** — optioneel, een grote afbeelding boven de pagina-inhoud.
- **Omschrijving voor Google (meta-description)** — de korte tekst (max. ~155 tekens) die Google onder de titel toont in zoekresultaten. Laat je dit leeg, dan gebruikt de site een algemene standaardtekst.
- **Gepubliceerd** — vinkje aan = zichtbaar voor bezoekers. Een nieuwe pagina staat standaard **uit** (concept), zodat je rustig kan opbouwen voor je hem live zet.

**Blokken toevoegen en ordenen**

Onder de instellingen staat een rij knoppen, één per bloktype — klik op een knop om zo'n blok toe te voegen. De pagina-inhoud bestaat uit een lijst van blokken die je met de hand kan **verslepen** om te herordenen (grijp het handvat links van een blok).

| Bloktype | Waarvoor |
|---|---|
| **Tekstblok** | Vrije tekst met opmaak (vet, links, lijsten, tabellen...) via een tekstverwerker-achtige editor |
| **Afbeelding(en)** | Eén grote afbeelding, of meerdere als grid; per afbeelding een alt-tekst (omschrijving voor schermlezers/Google) |
| **Kolommen** | 2 tot 4 kolommen naast elkaar, elk met eigen titel, tekst en afbeelding |
| **Video** | Een YouTube- of Vimeo-video: plak gewoon de gewone video-URL |
| **Knop** | Een opvallende link-knop, bv. naar een andere pagina of externe site |
| **Citaat** | Een uitgelicht citaat met optioneel auteur/functie |
| **Veelgestelde vragen** | Een lijst vraag/antwoord (1 tot 6) |
| **Statistieken** | Een rij kerncijfers (bv. "500+ leden"), 1 tot 4 stuks |
| **HTML/embed** | Voor bv. een Google Maps-embed; wordt automatisch opgeschoond tot veilige, eenvoudige HTML |

Elk blok heeft onderaan ook een sectie **"Weergave"** met vier keuzes: uitlijning (links/midden/rechts), achtergrond (geen/licht/blauw/donker), breedte (smal/normaal/breed) en witruimte errond (compact/normaal/ruim). Hiermee geef je een blok net iets meer visuele afwisseling zonder code te moeten schrijven.

Klaar met een blok? Klik **"Opslaan"**. Je kan blokken ook verwijderen via het prullenbak-icoon in de werkbalk boven het blok.

**Bekijken voor je publiceert:** zolang een pagina niet gepubliceerd is, kan je via **"Voorbeeld bekijken"** (bovenaan het bewerkscherm) toch al zien hoe ze er echt uitziet — enkel jij als ingelogde admin ziet dat voorbeeld, bezoekers niet.

**Pagina verwijderen:** kan enkel als geen navigatie-item nog naar die pagina verwijst. Doet een menu-item dat wel, dan krijg je een melding welk item je eerst moet aanpassen op de Navigatie-pagina (zie hoofdstuk 4).

### 3.2 Vaste pagina's (site-teksten)

Pagina's zoals **Homepage, Club, Kalender, Jeugd, G-Handbal, FIT-Handbal, Contact** en een aantal ondersteunende schermen (login, profiel, webshop-stappen, footer...) hebben een vaste lay-out die in de code vastligt. Je kan er dus geen blokken aan toevoegen of verwijderen, maar wel alle teksten en afbeeldingen erin aanpassen.

Klik in de pagina-lijst op **"Bewerken"** bij zo'n pagina. Je krijgt een formulier met één veld per tekststuk op die pagina (titels, intro's, knoppenteksten, langere tekstblokken met opmaak...). Vul aan, klik **"Opslaan"**. Via **"Bekijk deze pagina"** naast de titel controleer je meteen het resultaat.

---

## 4. Navigatie beheren

Via **Content → Navigatie** bouw je het menu boven op de site op.

**Nieuw item toevoegen** (bovenaan de pagina):

1. **Label** — de tekst die in het menu verschijnt.
2. **Type** — kies waar het item naar moet leiden:
   - **Categorie (dropdown)** — geen link, maar een submenu-kop; kan enkel op het hoofdniveau staan.
   - **Groepslabel** — een ongeklikbaar label binnen een categorie, om items te groeperen.
   - **Pagina** — verwijst naar één van je contentpagina's.
   - **Vaste route** — verwijst naar een vast onderdeel van de site (bv. de webshop of een teampagina); dit vraagt een technische "route-naam" en is vooral bedoeld voor wie de code kent.
   - **Externe URL** — een link naar een andere website.
3. **Plaats onder** — "Hoofdniveau", of een bestaande categorie zodat het item in dat submenu terechtkomt.
4. **Nieuw tabblad** — vink aan als de link in een nieuw tabblad moet openen (handig bij externe links).

**Herordenen:** sleep een item naar zijn nieuwe plaats (grijp het handvat links), of gebruik de pijltjes-omhoog/omlaag als alternatief. Slepen werkt ook om een item naar een andere categorie te verplaatsen. Een categorie kan enkel op het hoofdniveau blijven staan — de site voorkomt dat je die per ongeluk in een submenu dropt.

**Bewerken/verwijderen** doe je rechtstreeks op elk item in de lijst. Een item verwijderen verwijdert ook automatisch alle onderliggende items in dat submenu.

> Verwijs je een navigatie-item naar een pagina of team dat nadien verwijderd wordt, dan verschijnt dat als waarschuwing op het dashboard ("verwijst naar iets dat niet meer bestaat") — pas dan het item hier aan.

---

## 5. Nieuws

Via **Content → Nieuws** beheer je de nieuwsberichten. De 3 eerste in de lijst hieronder verschijnen op de homepage bij "Laatste nieuws"; alle berichten samen staan op de nieuwspagina, in dezelfde volgorde. Herorden met de pijltjes-omhoog/omlaag.

Bij **"Nieuw bericht toevoegen"**:

- **Titel** en **Inhoud** (via de tekstverwerker-editor) zijn verplicht.
- **Categorie** — kies uit de beschikbare categorieën.
- **Gepubliceerd op** — datum/tijd die bij het bericht getoond wordt; leeg laten = nu.
- **Groot formaat** — laat dit bericht meer plaats innemen op de overzichten.
- **Afbeelding** — optioneel.
- **Samenvatting** — de korte tekst die op de overzichten getoond wordt; leeg laten toont automatisch een stukje van het volledige bericht.

Tekst wordt bij opslaan automatisch opgeschoond: enkel eenvoudige, veilige opmaak (vet, links, lijsten...) blijft behouden.

---

## 6. Evenementen

Via **Content → Evenementen** beheer je de eventlijst. Toekomstige evenementen (op datum) verschijnen op de homepage bij "Volgende event". Verlopen evenementen blijven hier in het overzicht staan (met badge "Verlopen"), maar verdwijnen automatisch van de publieke site.

Velden: **Titel**, **Datum**, **Locatie** (optioneel) en **Tekst** — allemaal eenvoudige tekst, geen aparte inschrijvingen per evenement (die lopen via het algemene inschrijvingsformulier, zie hoofdstuk 10).

---

## 7. Teams

Via **Content → Teams** beheer je alle ploegen. Elk team krijgt automatisch een eigen pagina op `/teams/<slug>`.

Velden bij een team:

- **Naam**, **Sectie** (Dames/Heren/Jeugd/G-Handbal/FIT-Handbal), **Categorie** (vrij tekstveld, bv. "Eerste ploeg", "Beloften"), **Trainer** — allemaal optioneel behalve naam en sectie.
- **Slug** — interne verwijzing/link-onderdeel; leeg laten leidt hem automatisch van de naam af.
- **Ploegfoto** en **Omschrijving** — optioneel, maar het dashboard waarschuwt je als een team geen foto of omschrijving heeft.
- **Prestatiebadges** (aantal bekers/landstitels/Europese wedstrijden) — laat je een veld leeg, dan toont de site "X" (nog niet ingevuld) in plaats van een getal. Heeft dit team nooit Europees gespeeld, laat "Europese wedstrijden" dan leeg — die badge wordt dan gewoon niet getoond in plaats van "0".

**Verwijderen** kan enkel als geen navigatie-item nog naar dat team verwijst — net als bij pagina's krijg je anders een melding welk menu-item je eerst moet aanpassen.

---

## 8. Sponsors

Via **Content → Sponsors** beheer je de sponsorlogo's.

- De **eerste 2 actieve sponsors** (in de volgorde van de lijst) verschijnen als hoofdsponsor-logo's naast het menu in de header. - Zijn er **meer dan 2** actief, dan verschijnen alle actieve sponsors ook in de sponsorenlijst in de footer.

Voeg een sponsor toe met **Naam**, optioneel een **Website**, en een verplicht **Logo**. Herorden met de pijltjes-omhoog/omlaag — de volgorde bepaalt dus mee wie als hoofdsponsor getoond wordt. Een sponsor kan je **deactiveren** (blijft in de lijst, verdwijnt van de site) of definitief **verwijderen**.

---

## 9. Webshop

### 9.1 Producten & varianten

Via **Webshop → Producten** beheer je het aanbod.

> **Belangrijk:** producten en varianten (kleur/maat-combinaties) worden **nooit echt verwijderd**, enkel geactiveerd/gedeactiveerd. Bestaande bestellingen verwijzen namelijk naar hun product/variant (voor de historiek: welke kleur/maat/prijs iemand destijds bestelde) — zonder dat zouden oude bestellingen naar niets meer verwijzen. Wil je een product niet meer verkopen, **deactiveer** het dan.

Bij een product: **Naam**, **Beschrijving**, **Afbeelding**, of **bedrukking mogelijk** is voor dit artikel, en of het **actief** (koopbaar) is.

Per product beheer je ook de **varianten** (kleur + maat), elk met eigen **prijs**, **voorraad** en actief/inactief-status. Een actief product zonder enige koopbare variant (voorraad > 0) verschijnt als waarschuwing op het dashboard.

### 9.2 Tickets voor wedstrijden

Via **Webshop → Tickets** verkoop je tickets voor wedstrijden. Supporters kopen ze in de webshop (pagina **/tickets**, ook bereikbaar via een knop op de productpagina) en kunnen ze samen met kledij in hetzelfde winkelmandje afrekenen. Net als bij de webshop moeten ze daarvoor ingelogd zijn.

1. Klik op **"Nieuwe wedstrijd toevoegen"** en vul de **wedstrijd** (bv. "Heren 1 - HC Tongeren"), **datum en aanvangsuur**, optioneel een **einde online verkoop**, de **locatie**, **extra info**, een **maximum aantal tickets** en een **maximum per bestelling** in (beide leeg = onbeperkt).
2. Na het opslaan voeg je de **tickettypes** toe, elk met een eigen prijs (bv. Volwassene €8, Kind -12 €4). Zonder minstens één actief tickettype verschijnt de wedstrijd niet in de webshop.

Goed om te weten:

- De online verkoop **sluit automatisch** op het ingestelde **einde online verkoop**, of bij het aanvangsuur als je dat veld leeg laat. De wedstrijd verdwijnt dan uit de webshop. Wil je onverwacht meteen stoppen, **deactiveer** de wedstrijd dan.
- Het **maximum per bestelling** geldt voor alle tickettypes van die wedstrijd samen (bv. max. 6 = 4 volwassenen + 2 kinderen).
- Het maximum aantal tickets telt ook bestellingen die nog op betaling wachten. Wordt een betaling niet afgerond, dan komen die plaatsen na ongeveer een halfuur automatisch weer vrij.
- Een prijswijziging geldt enkel voor nieuwe bestellingen.
- Een wedstrijd verwijderen kan enkel zolang er nog geen tickets voor besteld zijn — daarna kan je ze enkel deactiveren.

**Naamlijst voor aan de ingang:** klik bij een wedstrijd op **"Naamlijst"**. Je ziet alle kopers met een betaalde bestelling, alfabetisch op achternaam, met het aantal tickets per type. Wie op verschillende momenten bestelde, staat er één keer op: de tickets worden opgeteld en alle bestelnummers staan erbij. Met **"Afdrukken"** druk je een lijst af met een afvinkvakje per koper. Met **"Download als Excel (CSV)"** krijg je dezelfde lijst als bestand. De koper toont aan de ingang de bevestigingsmail (met naam en bestelnummer). Geannuleerde of terugbetaalde bestellingen verdwijnen automatisch van de lijst.

### 9.3 Bestellingen

Via **Webshop → Bestellingen** zie je alle geplaatste bestellingen: klant, bedrag, verzendkosten, betaalstatus en status. Bestellingen met tickets zijn gemarkeerd met 🎟️. Klik op **"Bekijken"** voor de volledige inhoud (producten, kleur/maat, bedrukkingstekst voor- en achterkant, tickets, aantallen en prijzen). Bestellingen met enkel tickets hoeven niet verzonden te worden en tellen niet mee bij "Bestellingen die actie nodig hebben" op het dashboard.

Op de detailpagina wijzig je de **status** van de bestelling (bv. In verwerking → Verzonden). Zet je een bestelling op **"Geannuleerd"**, dan gebeurt automatisch twee dingen:

1. De voorraad van elke bestelde variant wordt teruggeboekt, en eventuele tickets komen weer vrij.
2. De klant krijgt automatisch een annulatiemail.

### 9.4 Instellingen

Via **Webshop → Instellingen** kan je de **hele webshop tijdelijk sluiten**. Staat ze dicht, dan verdwijnt de FanShop-link en het winkelmandje-icoon
overal van de site, en tonen alle webshop-pagina's een "tijdelijk gesloten"-melding voor bezoekers. Enkel ingelogde admins zien de webshop dan nog — de rest van de site blijft gewoon normaal bereikbaar.

---

## 10. Leden & inschrijvingen

### 10.1 Gebruikers

Via **Leden & inschrijvingen → Gebruikers** zie je alle geregistreerde accounts (naam, gebruikersnaam, e-mail, lid sinds, en of het een admin is).

Via **"Nieuwe admin aanmaken"** (bovenaan, inklapbaar) maak je een extra admin-account aan: voornaam, achternaam, gebruikersnaam, e-mail en wachtwoord (minstens 8 tekens, 1 cijfer, 1 speciaal teken) zijn allemaal verplicht. Let op: dit is de enige manier om een admin toe te voegen — een gewone gebruiker kan hier niet achteraf tot admin "bevorderd" worden via het scherm.

### 10.2 Inschrijvingen

Via **Leden & inschrijvingen → Inschrijvingen** zie je alle inschrijvingsaanvragen (Jeugd, G-Handbal, FIT-Handbal) met alle ingevulde gegevens: speler, geboortedatum/-plaats, adres, contactgegevens, hoe ze de club leerden kennen, school en opmerkingen.

Standaard toont de lijst enkel de **onverwerkte** inschrijvingen. Klik **"Toon ook verwerkte inschrijvingen"** om alles te zien. Vink een inschrijving af met **"Markeer als verwerkt"** zodra je ze hebt opgevolgd (bv. het lid ingeschreven in je ledenadministratie) — dat vinkje is puur administratief, er gebeurt inhoudelijk niets automatisch.

### 10.3 Inschrijvingsformulier instellen

Via **Leden & inschrijvingen → Inschrijvingsformulier** pas je het inschrijvingsformulier zelf aan (het formulier dat toekomstige leden invullen), via vier tabbladen:

- **Velden** — per veld van het formulier (naam, adres, school, ...) kan je het **label** aanpassen (de tekst die de bezoeker ziet) en aanvinken of het veld **verplicht** is.
- **Categorieën** — de keuzelijst met inschrijvingscategorieën (bv. leeftijds- of afdelingscategorieën). Toevoegen met naam, of verwijderen.
- **Hoe-gehoord-opties** — de keuzelijst voor "Hoe heb je van ons gehoord?".
- **Scholen** — de keuzelijst met scholen in het schoolveld van het formulier.

Elk tabblad werkt als een simpel lijstje: naam invullen, **"Toevoegen"**, of **"Verwijderen"** bij een bestaand item (met bevestiging).

---

## 11. GDPR-verzoeken

Via **Beheer → GDPR-verzoeken** zie je alle "vergeet mij"-verzoeken die bezoekers via de site indienden: naam, e-mail, lidnummer en opmerking.

Zoals bij inschrijvingen toont de lijst standaard enkel de **onverwerkte** verzoeken; klik **"Toon ook verwerkte verzoeken"** voor het volledige overzicht. Markeer een verzoek als **"verwerkt"** zodra je het effectief hebt afgehandeld (de betrokken gegevens verwijderd/aangepast in je systemen) — dit vinkje registreert enkel dat jij het verzoek hebt opgevolgd, de site verwijdert zelf niets automatisch.

> GDPR-verzoeken vragen om tijdig én zorgvuldig opgevolgd te worden — dit is een wettelijke verplichting, geen "nice to have". Bekijk dit overzicht dus regelmatig (het dashboard toont ook het aantal onverwerkte verzoeken als actiepunt).

---

## 12. Veelgestelde vragen & tips

**Ik zie mijn wijziging niet op de live site staan.**
Controleer of de pagina op **"Gepubliceerd"** staat (contentpagina's) en of je écht op "Opslaan" geklikt hebt. Gebruik bij twijfel de knop "Bekijk pagina"/"Voorbeeld bekijken" rechtstreeks vanuit het bewerkscherm.

**Wat is een "slug"?**
Het stukje van de webadres (URL) dat uit de titel/naam wordt afgeleid, bv. "Over ons" → `over-ons` → `/pagina/over-ons`. Je mag dit zelf aanpassen, maar verander de slug van een pagina die al gedeeld is niet zomaar — oude links blijven dan niet werken.

**Waarom kan ik dit product/team/pagina niet verwijderen?**
Waarschijnlijk verwijst er nog een navigatie-item naar. De foutmelding zegt exact welk item je eerst moet aanpassen of verwijderen op de Navigatie-pagina.

**Waarom staat "X" in plaats van een getal bij een team?**
Dat betekent dat dat veld (bv. "Aantal bekers") nog niet ingevuld is. Vul het in via "Teams bewerken", of laat het bewust leeg als het niet van toepassing is (bv. "Europese wedstrijden" voor een team dat nooit Europees speelde) — dan verschijnt die badge gewoon niet.

**Kan ik afbeeldingen kwijt geraken door ze te vervangen?**
Nee: upload je een nieuwe afbeelding op een plek waar al één stond, dan wordt de oude automatisch verwijderd van de server (dat gebeurt overal consistent — producten, pagina's, teams, nieuws, sponsors...).

**Ik ben mijn wachtwoord vergeten.**
Er is geen zelfbedieningsoptie hiervoor, en ook een andere admin kan dit niet voor je oplossen via het adminpaneel — dit vraagt technische tussenkomst (rechtstreeks in de database). Bewaar je wachtwoord dus zorgvuldig.

**Wanneer gebruik ik de onderhoudsmodus, en wanneer sluit ik enkel de webshop?**
Onderhoudsmodus (dashboard) legt de **hele site** plat voor bezoekers — enkel gebruiken bij grote wijzigingen. Webshop sluiten (Webshop → Instellingen) laat de rest van de site (nieuws, pagina's, teams...) gewoon werken, en sluit enkel de verkoop af.