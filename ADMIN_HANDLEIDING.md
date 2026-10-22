# Adminhandleiding website HB Sint-Truiden

In deze handleiding lees je hoe je als admin de website van HB Sint-Truiden beheert: pagina's, nieuws, evenementen, teams, sponsors, affiches, de webshop, ledeninschrijvingen en GDPR-verzoeken. Je hebt er geen technische kennis voor nodig, enkel een browser.

## Inhoud

1. [Inloggen en het dashboard](#1-inloggen-en-het-dashboard)
2. [Mijn account](#2-mijn-account)
3. [Pagina's beheren](#3-paginas-beheren)
4. [Navigatie beheren](#4-navigatie-beheren)
5. [Nieuws](#5-nieuws)
6. [Evenementen](#6-evenementen)
7. [Teams](#7-teams)
8. [Sponsors](#8-sponsors)
9. [Affiches op de homepage](#9-affiches-op-de-homepage)
10. [Webshop](#10-webshop)
11. [Leden & inschrijvingen](#11-leden--inschrijvingen)
12. [GDPR-verzoeken](#12-gdpr-verzoeken)
13. [Veelgestelde vragen & tips](#13-veelgestelde-vragen--tips)

## Algemeen

Wijzigingen worden niet automatisch opgeslagen. Klik altijd op de knop onderaan (meestal **"Opslaan"** of **"Toevoegen"**) voor je een pagina verlaat, anders ben je je wijziging kwijt.

Rode knoppen ("Verwijderen", "Deactiveren", "Site in onderhoud zetten" ...) hebben gevolgen voor de live site of zijn niet ongedaan te maken. Bij de belangrijkste vraagt de site eerst om te bevestigen.

Producten en bestellingen worden nooit echt verwijderd, enkel gedeactiveerd (zie [hoofdstuk 10](#10-webshop)). Pagina's, nieuws, teams, sponsors, evenementen enzovoort verdwijnen wel definitief zodra je op "Verwijderen" klikt.

Afbeeldingen upload je overal met een "Bestand kiezen"-knop. Je kan JPG, PNG, GIF en WEBP gebruiken.

De overzichtslijsten (bestellingen, inschrijvingen, gebruikers, GDPR-verzoeken) werken allemaal op dezelfde manier:

- Bovenaan staat een filterbalk met een zoekveld en keuzelijsten. Als je een keuzelijst wijzigt, wordt meteen gefilterd. Na het zoekveld druk je op Enter of op **"Filteren"**. Met **"Wis filters"** zet je alles terug.
- Elke rij staat op één lijn. Klik ergens op de rij om de fiche met alle gegevens te openen. Met **"Terug naar de lijst"** kom je terug in dezelfde gefilterde lijst.
- Lange lijsten worden verdeeld over pagina's van 50, met "Vorige" en "Volgende".
- Met de vinkjes voor de rijen handel je meerdere items tegelijk af (bv. archiveren of als verwerkt markeren). Het vinkje in de kolomkop selecteert alles op de pagina.
- Een gefilterde lijst kan je als bladwijzer bewaren, want de filters staan in het adres van de pagina.

## 1. Inloggen en het dashboard

Ga naar `/login` op de website en meld je aan met je gebruikersnaam en wachtwoord. Na het inloggen zie je de site zoals een gewone bezoeker. Het adminpaneel open je via `/admin`.

Links in het adminpaneel staat een menu met vier groepen:

| Menugroep | Wat je er beheert |
|---|---|
| **Content** | Pagina's, Nieuws, Evenementen, Sponsors, Teams, Affiches, Navigatie |
| **Leden & inschrijvingen** | Gebruikers, Inschrijvingen, Inschrijvingsformulier |
| **Webshop** | Producten, Tickets, Acties, Bestellingen, Instellingen |
| **Beheer** | GDPR-verzoeken, Mijn account |

### Het dashboard

De eerste pagina van het adminpaneel (`/admin`) toont drie dingen.

Met de schakelaar **Onderhoudsmodus** zet je de hele website tijdelijk offline. Bezoekers zien dan enkel een "even geduld"-pagina, jij kan als admin overal nog aan. Gebruik dit enkel tijdens een grote update en zet het uit zodra je klaar bent, anders blijft de site voor iedereen offline.

De **Actiepunten** zijn tegels met een aantal. Ze brengen je meteen naar de plek waar iets moet gebeuren: onverwerkte GDPR-verzoeken, onverwerkte inschrijvingen, bestellingen die opvolging nodig hebben en pagina's die nog niet gepubliceerd zijn.

Onder **Waarschuwingen** staat wat onvolledig is of niet klopt, bv. een team zonder foto, een actief product zonder koopbare variant of een navigatie-item dat verwijst naar iets wat niet meer bestaat. De site blijft gewoon werken, maar los het best toch op.

## 2. Mijn account

Via **Beheer → Mijn account** wijzig je je eigen wachtwoord. Vul je huidige wachtwoord in en daarna twee keer je nieuwe wachtwoord. Een nieuw wachtwoord moet minstens 8 tekens lang zijn en minstens 1 cijfer en 1 speciaal teken bevatten.

Nieuwe admins voeg je toe via **Leden & inschrijvingen → Gebruikers** (zie [hoofdstuk 11](#11-leden--inschrijvingen)).

Er is geen "wachtwoord vergeten"-link, en een andere admin kan je wachtwoord ook niet resetten via het adminpaneel. Bewaar je wachtwoord dus op een veilige plek, bv. in een wachtwoordmanager. Raak je toch niet meer binnen, dan moet iemand technisch tussenkomen (zie [hoofdstuk 13](#13-veelgestelde-vragen--tips)).

## 3. Pagina's beheren

Via **Content → Pagina's** zie je alle bewerkbare pagina's van de site samen. Er zijn twee soorten, die je herkent aan de badge in de kolom "Type":

| Type | Herkenbaar aan | Hoe bewerk je ze |
|---|---|---|
| **Contentpagina** | badge "Contentpagina" | Je bouwt de pagina zelf op uit blokken (zie 3.1) |
| **Vaste pagina** | badge "Vaste pagina" | De opbouw ligt vast (bv. Homepage, Club, Contact), je past enkel de teksten en afbeeldingen aan (zie 3.2) |

### 3.1 Contentpagina's (blokken-editor)

Contentpagina's bouw je zelf volledig op, bv. voor een los project of een speciale actie. Klik op **"Nieuwe contentpagina toevoegen"** om te beginnen.

**Pagina-instellingen** (bovenaan het bewerkscherm, in te klappen):

- **Titel**: de titel van de pagina.
- **Slug**: het stuk van de link na `/pagina/`, bv. `over-ons` geeft `/pagina/over-ons`. Vul je niets in, dan wordt de slug uit de titel gemaakt. Als je de slug van een pagina wijzigt die al gedeeld is, verandert de link en werken oude links (bv. op sociale media) niet meer.
- **Afbeelding bovenaan (hero)**: optioneel, een grote afbeelding boven de inhoud.
- **Omschrijving voor Google (meta-description)**: de korte tekst (max. ongeveer 155 tekens) die Google onder de titel toont in de zoekresultaten. Laat je dit leeg, dan gebruikt de site een algemene standaardtekst.
- **Gepubliceerd**: aangevinkt betekent zichtbaar voor bezoekers. Een nieuwe pagina staat standaard uit (concept), zodat je ze rustig kan opbouwen voor ze online komt.

**Blokken toevoegen en ordenen**

Onder de instellingen staat een rij knoppen, één per bloktype. Klik op een knop om zo'n blok toe te voegen. De inhoud van de pagina is een lijst van blokken die je kan verslepen om de volgorde te wijzigen (neem het handvat links van een blok vast).

| Bloktype | Waarvoor |
|---|---|
| **Tekstblok** | Vrije tekst met opmaak (vet, links, lijsten, tabellen ...) in een editor zoals een tekstverwerker |
| **Afbeelding(en)** | Eén grote afbeelding of meerdere in een raster, per afbeelding een alt-tekst (omschrijving voor schermlezers en Google) |
| **Kolommen** | 2 tot 4 kolommen naast elkaar, elk met een eigen titel, tekst en afbeelding |
| **Video** | Een YouTube- of Vimeo-video, plak gewoon de link van de video |
| **Knop** | Een opvallende knop met een link, bv. naar een andere pagina of een externe site |
| **Citaat** | Een uitgelicht citaat, eventueel met auteur en functie |
| **Veelgestelde vragen** | Een lijst met vragen en antwoorden (1 tot 6) |
| **Statistieken** | Een rij kerncijfers (bv. "500+ leden"), 1 tot 4 stuks |
| **HTML/embed** | Bv. voor een Google Maps-kaart, wordt automatisch opgeschoond tot veilige, eenvoudige HTML |

Onderaan elk blok staat een sectie **"Weergave"** met vier keuzes: uitlijning (links, midden, rechts), achtergrond (geen, licht, blauw, donker), breedte (smal, normaal, breed) en witruimte rond het blok (compact, normaal, ruim).

Klaar met een blok? Klik op **"Opslaan"**. Een blok verwijderen doe je met het prullenbakje in de werkbalk boven het blok.

Zolang een pagina niet gepubliceerd is, kan je via **"Voorbeeld bekijken"** (bovenaan het bewerkscherm) al zien hoe ze eruit zal zien. Dat voorbeeld zie enkel jij als ingelogde admin, bezoekers niet.

Een pagina verwijderen kan enkel als er geen navigatie-item meer naar verwijst. Is dat wel zo, dan krijg je een melding welk item je eerst moet aanpassen op de Navigatie-pagina (zie hoofdstuk 4).

### 3.2 Vaste pagina's (site-teksten)

Pagina's zoals Homepage, Club, Kalender, Jeugd, G-Handbal, FIT-Handbal en Contact en een aantal ondersteunende schermen (login, profiel, de stappen van de webshop, footer ...) hebben een vaste lay-out die in de code ligt. Je kan er geen blokken toevoegen of verwijderen, maar je kan wel alle teksten en afbeeldingen aanpassen.

Klik in de lijst met pagina's op **"Bewerken"** bij zo'n pagina. Je krijgt een formulier met een veld voor elk stuk tekst op die pagina (titels, intro's, teksten op knoppen, langere teksten met opmaak ...). Pas aan en klik op **"Opslaan"**. Met **"Bekijk deze pagina"** naast de titel controleer je meteen het resultaat.

## 4. Navigatie beheren

Via **Content → Navigatie** stel je het menu bovenaan de site samen.

**Nieuw item toevoegen** (bovenaan de pagina):

1. **Label**: de tekst die in het menu verschijnt.
2. **Type**: waar het item naartoe leidt.
   - **Categorie (dropdown)**: geen link, maar de kop van een submenu. Kan enkel op het hoofdniveau staan.
   - **Groepslabel**: een label binnen een categorie waarop je niet kan klikken, om items te groeperen.
   - **Pagina**: verwijst naar een van je contentpagina's.
   - **Vaste route**: verwijst naar een vast onderdeel van de site (bv. de webshop of een teampagina). Hiervoor heb je een technische "route-naam" nodig, dus dit is vooral iets voor wie de code kent.
   - **Externe URL**: een link naar een andere website.
3. **Plaats onder**: "Hoofdniveau" of een bestaande categorie, zodat het item in dat submenu komt.
4. **Nieuw tabblad**: vink aan als de link in een nieuw tabblad moet openen (handig bij externe links).

**Herordenen:** sleep een item naar zijn nieuwe plaats (neem het handvat links vast) of gebruik de pijltjes omhoog en omlaag. Door te slepen kan je een item ook naar een andere categorie verplaatsen. Een categorie moet op het hoofdniveau blijven, de site laat niet toe dat je ze in een submenu sleept.

Elk item bewerk of verwijder je rechtstreeks in de lijst. Als je een item verwijdert, worden ook alle items in zijn submenu verwijderd.

Verwijst een navigatie-item naar een pagina of team dat later verwijderd wordt, dan verschijnt er een waarschuwing op het dashboard ("verwijst naar iets dat niet meer bestaat"). Pas het item dan hier aan.

## 5. Nieuws

Via **Content → Nieuws** beheer je de nieuwsberichten. De eerste 3 berichten in de lijst verschijnen op de homepage bij "Laatste nieuws". Alle berichten staan in dezelfde volgorde op de nieuwspagina. De volgorde wijzig je met de pijltjes omhoog en omlaag.

Bij **"Nieuw bericht toevoegen"**:

- **Titel** en **Inhoud** (in de editor) zijn verplicht.
- **Categorie**: kies een van de beschikbare categorieën.
- **Gepubliceerd op**: de datum en het uur die bij het bericht staan. Laat je dit leeg, dan wordt het nu.
- **Groot formaat**: het bericht neemt meer plaats in op de overzichten.
- **Afbeelding**: optioneel.
- **Samenvatting**: de korte tekst op de overzichten. Laat je dit leeg, dan wordt automatisch het begin van het bericht getoond.

Bij het opslaan wordt de tekst automatisch opgeschoond. Enkel eenvoudige, veilige opmaak (vet, links, lijsten ...) blijft behouden.

## 6. Evenementen

Via **Content → Evenementen** beheer je de lijst met evenementen. Toekomstige evenementen verschijnen op de homepage bij "Volgende event". Voorbije evenementen blijven in dit overzicht staan (met de badge "Verlopen"), maar verdwijnen vanzelf van de publieke site.

De velden zijn **Titel**, **Datum**, **Locatie** (optioneel) en **Tekst**. Je kan per evenement geen aparte inschrijvingen openen, die lopen via het algemene inschrijvingsformulier (zie hoofdstuk 11).

## 7. Teams

Via **Content → Teams** beheer je alle ploegen. Elk team krijgt automatisch een eigen pagina op `/teams/<slug>`.

Velden bij een team:

- **Naam**, **Sectie** (Dames, Heren, Jeugd, G-Handbal, FIT-Handbal), **Categorie** (vrij tekstveld, bv. "Eerste ploeg", "Beloften") en **Trainer**. Enkel naam en sectie zijn verplicht.
- **Slug**: het stuk van de link. Laat je dit leeg, dan wordt de slug uit de naam gemaakt.
- **Ploegfoto** en **Omschrijving**: optioneel, maar het dashboard waarschuwt je als een team geen foto of omschrijving heeft.
- **Prestatiebadges** (aantal bekers, landstitels en Europese wedstrijden): laat je een veld leeg, dan toont de site "X" (nog niet ingevuld) in plaats van een getal. Heeft het team nooit Europees gespeeld, laat "Europese wedstrijden" dan leeg. Die badge wordt dan niet getoond in plaats van "0".

Een team verwijderen kan enkel als er geen navigatie-item meer naar verwijst. Net als bij pagina's krijg je anders een melding welk menu-item je eerst moet aanpassen.

## 8. Sponsors

Via **Content → Sponsors** beheer je de logo's van de sponsors.

De eerste 2 actieve sponsors (in de volgorde van de lijst) staan als hoofdsponsors naast het menu bovenaan de site. Zijn er meer dan 2 actief, dan staan alle actieve sponsors ook in de sponsorlijst in de footer.

Een sponsor voeg je toe met een **Naam**, eventueel een **Website**, en een **Logo** (verplicht). De volgorde wijzig je met de pijltjes omhoog en omlaag, en die bepaalt dus ook wie als hoofdsponsor getoond wordt. Een sponsor kan je **deactiveren** (hij blijft in de lijst maar verdwijnt van de site) of definitief **verwijderen**.

## 9. Affiches op de homepage

Via **Content → Affiches** zet je een affiche bovenaan de homepage, bv. voor een actie of een tornooi. De affiche komt boven de teamfoto, in een band over de volledige breedte van het scherm, en wordt nooit bijgesneden. De affiche zelf staat in het midden en is maximaal 640 px hoog (op kleinere schermen 60% van de schermhoogte). Aan de zijkanten vult een wazige, vergrote versie van dezelfde affiche de ruimte op. Vraag daarom altijd een liggende affiche, want een staande of vierkante neemt bovenaan veel te veel plaats in. Kies je toch een afbeelding die niet liggend is, dan krijg je een waarschuwing, maar je kan wel opslaan.

Bij een affiche vul je in:

- **Titel**: enkel voor jezelf in de admin.
- **Affiche**: de liggende afbeelding. Het beste formaat is 2400 × 1200 px (verhouding 2:1, 1920 × 1080 kan ook). Minimaal 1200 × 600 px, anders wordt de tekst wazig.
- **Gsm-versie** (optioneel): een vierkante of licht staande versie. Op een gsm wordt een liggende affiche zo klein dat je de tekst niet meer kan lezen. Laad je een gsm-versie op, dan zien smalle schermen die. Anders wordt de liggende verkleind. Het beste formaat is 1080 × 1080 px (1080 × 1350 kan ook), minimaal 800 × 800 px. Een Instagram-post past dus meteen, een story (9:16) is te hoog.
- Gebruik JPG of WEBP, liefst kleiner dan 500 KB, zodat de homepage snel laadt.
- **Wat staat er op de affiche?**: een korte samenvatting van de tekst op de affiche. Die wordt voorgelezen aan blinde en slechtziende bezoekers en gebruikt door Google.
- **Link** (optioneel): waar je terechtkomt als je op de affiche klikt. Kies een actie of webshoppagina in de keuzelijst of typ zelf een adres (een pagina op deze site begint met `/`, een andere website met `https://`). Een andere website opent in een nieuw tabblad.
- **Zichtbaar vanaf / tot** (optioneel): de affiche verschijnt en verdwijnt dan vanzelf. Laat je dit leeg, dan is ze meteen zichtbaar tot je ze deactiveert.

Zijn er meerdere affiches tegelijk zichtbaar, dan wisselen ze automatisch af (met pijltjes en bolletjes) in de volgorde van de lijst. Die volgorde wijzig je met de pijltjes omhoog en omlaag. In de kolom **Status** zie je of een affiche nu **Zichtbaar**, **Gepland**, **Verlopen** of **Inactief** is. Een affiche kan je deactiveren of definitief verwijderen. Is er geen enkele affiche zichtbaar, dan ziet de homepage eruit zoals altijd.

## 10. Webshop

### 10.1 Producten & varianten

Via **Webshop → Producten** beheer je het aanbod.

Producten en varianten (combinaties van kleur en maat) worden nooit echt verwijderd, enkel geactiveerd of gedeactiveerd. Bestaande bestellingen verwijzen naar hun product en variant, zodat je later nog weet welke kleur, maat en prijs iemand bestelde. Zonder die verwijzing zouden oude bestellingen naar niets meer verwijzen. Wil je een product niet meer verkopen, deactiveer het dan.

Bij een product vul je een **Naam**, **Beschrijving** en **Afbeelding** in, en duid je aan of **bedrukking mogelijk** is en of het product **actief** (te koop) is.

Per product beheer je ook de **varianten** (kleur en maat), elk met een eigen **prijs**, **voorraad** en status actief of inactief. Een actief product zonder koopbare variant (voorraad groter dan 0) verschijnt als waarschuwing op het dashboard.

### 10.2 Tickets voor wedstrijden

Via **Webshop → Tickets** verkoop je tickets voor wedstrijden. Supporters kopen ze in de webshop (pagina `/tickets`, ook bereikbaar via een knop op de productpagina) en kunnen ze samen met kledij in hetzelfde winkelmandje afrekenen. Net als bij de rest van de webshop moeten ze daarvoor ingelogd zijn.

1. Klik op **"Nieuwe wedstrijd toevoegen"** en vul de **wedstrijd** (bv. "Heren 1 - HC Tongeren"), de **datum en het aanvangsuur**, eventueel een **einde online verkoop**, de **locatie**, **extra info**, een **maximum aantal tickets** en een **maximum per bestelling** in (beide leeg betekent onbeperkt).
2. Na het opslaan voeg je de **tickettypes** toe, elk met een eigen prijs (bv. Volwassene €8, Kind -12 €4). Zonder minstens één actief tickettype verschijnt de wedstrijd niet in de webshop.

Goed om te weten:

- De online verkoop sluit automatisch op het ingestelde **einde online verkoop**, of bij het aanvangsuur als je dat veld leeg laat. De wedstrijd verdwijnt dan uit de webshop. Wil je onverwacht meteen stoppen, deactiveer de wedstrijd dan.
- Het maximum per bestelling geldt voor alle tickettypes van die wedstrijd samen (bv. max. 6 = 4 volwassenen + 2 kinderen).
- Het maximum aantal tickets telt ook bestellingen die nog op betaling wachten. Wordt een betaling niet afgerond, dan komen die plaatsen na ongeveer een halfuur weer vrij.
- Een prijswijziging geldt enkel voor nieuwe bestellingen.
- Een wedstrijd verwijderen kan enkel zolang er nog geen tickets voor besteld zijn. Daarna kan je ze enkel deactiveren.

**Naamlijst voor aan de ingang:** klik bij een wedstrijd op **"Naamlijst"**. Je ziet alle kopers met een betaalde bestelling, alfabetisch op achternaam, met het aantal tickets per type. Wie op verschillende momenten bestelde, staat er één keer op: de tickets worden opgeteld en alle bestelnummers staan erbij. Met **"Afdrukken"** druk je een lijst af met een vakje om af te vinken per koper. Met **"Download als Excel (CSV)"** krijg je dezelfde lijst als bestand. Aan de ingang toont de koper de bevestigingsmail (met naam en bestelnummer). Geannuleerde of terugbetaalde bestellingen verdwijnen automatisch van de lijst.

### 10.3 Acties (verkoop met afhaling)

Via **Webshop → Acties** verkoop je dingen die kopers op een vast moment komen afhalen, bv. afhaalgerechten van onze chefs, een wafelverkoop of kerstpakketten. Supporters bestellen in de webshop (pagina `/acties`, ook bereikbaar via een knop op de productpagina) met één formulier: ze vullen per artikel een aantal in en kiezen één afhaalmoment voor alles wat ze bij die actie bestellen. Ze rekenen af samen met kledij en tickets in hetzelfde winkelmandje en moeten ook hier ingelogd zijn. Stripe vraagt bij het betalen een telefoonnummer, zodat je de koper kan bellen als er iets misloopt.

1. Klik op **"Nieuwe actie toevoegen"** en vul de **titel** en een **standaard afhaaladres** in, en eventueel een **uitleg**, een **afbeelding**, een datum **"bestellen kan tot"** (die geldt voor alle afhaalmomenten) en de **titel van het opmerkingenveld**. Onderaan het bestelformulier kan de koper vrij iets invullen, bv. een allergie of een aanmoediging voor de ploeg. Laat je de titel leeg, dan heet het veld "Opmerking".
2. Voeg de **artikelen** toe met naam, prijs en voorraad (leeg betekent onbeperkt). Via **"Bewerken"** bij een artikel stel je daarna een **foto**, **omschrijving**, **allergenen** en een **maximum per bestelling** in, en voeg je **varianten** toe (bv. klein en groot, of met vlees en vegetarisch), elk met een eigen prijs en voorraad. Met de pijltjes bepaal je de volgorde op de actiepagina.
3. Voeg de **afhaalmomenten** toe met datum, beginuur en einduur, adres (leeg betekent het standaardadres) en eventueel een **eigen deadline**.

Zonder minstens één actief artikel en één actief afhaalmoment verschijnt de actie niet in de webshop.

Goed om te weten:

- Bestellen voor een afhaalmoment sluit automatisch op het vroegste van deze drie: de deadline van de actie, de eigen deadline van het moment of het begin van het moment. Kan er voor geen enkel moment meer besteld worden, of is alles uitverkocht, dan blijft de actie zichtbaar met die melding tot het laatste afhaalmoment voorbij is. Daarna verdwijnt ze vanzelf.
- De voorraad van een variant is het totaal voor alle afhaalmomenten samen. Ze telt ook bestellingen die nog op betaling wachten. Wordt een betaling niet afgerond, dan komt die voorraad na ongeveer een halfuur weer vrij. Bij een geannuleerde bestelling komt ze meteen vrij.
- Het maximum per bestelling van een artikel geldt voor al zijn varianten samen (bv. max. 6 lasagnes, klein en groot samen).
- Een prijswijziging geldt enkel voor nieuwe bestellingen. Artikelen, varianten, afhaalmomenten en acties verwijderen kan enkel zolang er nog niets voor besteld is. Daarna kan je ze enkel deactiveren.
- Wil je de actie in het menu bovenaan, voeg dan via **Navigatie** een item toe naar de route `shop.acties`.

**Keukenlijst:** klik bij een actie op **"Keukenlijst"**. Je ziet per artikel en per afhaalmoment hoeveel er klaargemaakt moet worden, met totalen. Daaronder staan alle ingevulde opmerkingen. Je kan de lijst afdrukken of de aantallen downloaden als Excel (CSV).

**Afhaallijst:** klik bij een afhaalmoment op **"Afhaallijst"**. Je ziet alle kopers voor dat moment, alfabetisch op achternaam, met hun telefoonnummer, bestelnummers, wat ze komen halen en hun opmerking. Ook deze lijst kan je afdrukken (met een vakje om af te vinken) of downloaden. Op beide lijsten staan enkel betaalde bestellingen die niet geannuleerd zijn.

**Een afhaalmoment wijzigt of gaat niet door?** Open het moment via **"Bewerken"** en pas het uur of het adres aan, of vink **"Actief"** uit als het niet doorgaat. Vink dan **"Kopers na het opslaan mailen"** aan en schrijf eventueel een uitleg. Elke koper met een betaalde bestelling voor dat moment krijgt een mail met het nieuwe moment, het adres en wat er besteld werd, of met de melding dat het moment niet doorgaat. Eén bestelling naar een ander moment verplaatsen doe je op de detailpagina van die bestelling (zie hieronder).

### 10.4 Bestellingen

Via **Webshop → Bestellingen** zie je de geplaatste bestellingen met bestelnummer, klant, totaal, betaling, status en datum. Bestellingen met tickets zijn gemarkeerd met 🎟️, bestellingen met een actie (afhalen) met 🥡. Klik op een bestelling om alles te zien: producten, kleur en maat, de bedrukkingstekst voor en achter, tickets, actieartikelen met hun afhaalmoment, aantallen en prijzen, het e-mailadres en bij acties het telefoonnummer. Bestellingen met enkel tickets of acties moeten niet verzonden worden en tellen niet mee bij "Bestellingen die actie nodig hebben" op het dashboard.

**Filteren:** zoek op bestelnummer (bv. 42 of #42), naam of e-mail, en filter op **status**, **betaling** (openstaand, betaald, mislukt), **soort** (producten, tickets of acties), een bepaalde **wedstrijd of actie** (bij een actie ook op **afhaalmoment**) en de **periode** waarin besteld werd.

**Exporteren:** met **"Download als Excel (CSV)"** download je alle bestellingen die aan de huidige filters voldoen (niet enkel de pagina die je ziet), één rij per bestelling met klant, telefoon, inhoud, bedragen, betaling en status.

**Archiveren:** afgewerkte bestellingen haal je uit de standaardlijst door ze aan te vinken en op **"Archiveren"** te klikken, of met de knop **"Archiveren"** bovenaan een bestelling. Er wordt niets verwijderd. Met het filter **Archief → "Ook gearchiveerde"** of **"Enkel gearchiveerde"** zie je ze terug, en met **"Terugzetten uit archief"** komen ze weer in de gewone lijst. Gearchiveerde bestellingen tellen niet mee bij "Bestellingen die actie nodig hebben" op het dashboard. Op de keuken- en afhaallijsten van acties en de naamlijsten van tickets blijven ze wel staan.

Bij een actie kan je de bestelling via **"Ander afhaalmoment kiezen"** naar een ander moment van dezelfde actie verplaatsen, bv. als de koper belt of als een moment niet doorgaat. Laat **"Koper mailen met het nieuwe moment"** aangevinkt om de koper meteen te verwittigen.

Op de detailpagina wijzig je de **status** van de bestelling (bv. In verwerking → Verzonden). Zet je een bestelling op **"Geannuleerd"**, dan gebeuren er automatisch twee dingen:

1. De voorraad van elke bestelde variant wordt teruggeboekt, en tickets en actievoorraad komen weer vrij.
2. De klant krijgt een mail dat de bestelling geannuleerd is.

### 10.5 Instellingen

Via **Webshop → Instellingen** kan je de hele webshop tijdelijk sluiten. Staat ze dicht, dan verdwijnen de FanShop-link en het winkelmandje overal van de site, en tonen alle webshoppagina's aan bezoekers een melding dat de webshop tijdelijk gesloten is. Enkel ingelogde admins zien de webshop dan nog. De rest van de site blijft gewoon bereikbaar.

## 11. Leden & inschrijvingen

### 11.1 Gebruikers

Via **Leden & inschrijvingen → Gebruikers** zie je alle geregistreerde accounts met naam, gebruikersnaam, e-mail, lid sinds, het aantal bestellingen en of het om een admin gaat. Zoek op naam, gebruikersnaam of e-mail, of filter op **rol** (admins of gewone gebruikers). Klik op een gebruiker om de gegevens en alle bestellingen (ook de gearchiveerde) te zien. Op elke bestelling kan je klikken.

Via **"Nieuwe admin aanmaken"** (bovenaan, in te klappen) maak je een extra admin-account aan. Voornaam, achternaam, gebruikersnaam, e-mail en wachtwoord (minstens 8 tekens, 1 cijfer en 1 speciaal teken) zijn allemaal verplicht. Dit is de enige manier om een admin toe te voegen: een bestaande gewone gebruiker kan je hier niet achteraf admin maken.

### 11.2 Inschrijvingen

Via **Leden & inschrijvingen → Inschrijvingen** zie je alle inschrijvingsaanvragen (Jeugd, G-Handbal, FIT-Handbal) met datum, speler, categorie en status. Zoek op de naam van de speler, het e-mailadres of het gsm-nummer, of filter op **categorie** en **status**. Standaard toont de lijst enkel wat nog **te verwerken** is. Kies bij Status **"Verwerkt"** of **"Alle"** om de rest te zien.

Klik op een inschrijving om de **fiche** met alle ingevulde gegevens te openen: speler, geboortedatum en -plaats, adres, contactgegevens (klik op het e-mailadres of gsm-nummer om te mailen of te bellen), hoe ze de club leerden kennen, school en opmerkingen. Onderaan staat een **interne notitie** die enkel admins zien, bv. "gebeld op 17/10, start volgende week". Inschrijvingen met een notitie krijgen 📝 in de lijst.

Markeer een inschrijving als **verwerkt** zodra je ze hebt opgevolgd (bv. het lid hebt ingeschreven in de ledenadministratie). Dat kan op de fiche, of voor meerdere tegelijk met de vinkjes en **"Markeer als verwerkt"** in de lijst. Dit is enkel administratief, er gebeurt verder niets automatisch.

### 11.3 Inschrijvingsformulier instellen

Via **Leden & inschrijvingen → Inschrijvingsformulier** pas je het formulier aan dat nieuwe leden invullen. Er zijn vier tabbladen:

- **Velden**: per veld van het formulier (naam, adres, school ...) pas je het **label** aan (de tekst die de bezoeker ziet) en duid je aan of het veld **verplicht** is.
- **Categorieën**: de keuzelijst met inschrijvingscategorieën (bv. leeftijds- of afdelingscategorieën).
- **Hoe-gehoord-opties**: de keuzelijst bij "Hoe heb je van ons gehoord?".
- **Scholen**: de keuzelijst met scholen bij het schoolveld van het formulier.

Bij de laatste drie vul je een naam in en klik je op **"Toevoegen"**, of klik je op **"Verwijderen"** bij een bestaand item (je moet dan eerst bevestigen).

## 12. GDPR-verzoeken

Via **Beheer → GDPR-verzoeken** zie je alle "vergeet mij"-verzoeken die bezoekers via de site indienden. Zoek op naam, e-mail of lidnummer, of filter op status. Net als bij de inschrijvingen toont de lijst standaard enkel wat nog **te verwerken** is.

Klik op een verzoek om de **fiche** te openen: naam, e-mail, lidnummer en opmerking, het **account op de website** met hetzelfde e-mailadres (als dat bestaat, met een link) en een **interne notitie** om bij te houden wat je gedaan hebt. Markeer een verzoek als **"verwerkt"** zodra je het echt hebt afgehandeld (de gegevens verwijderd of aangepast in je systemen), op de fiche of met de vinkjes in de lijst. Daarmee registreer je enkel dat je het verzoek hebt opgevolgd. De site verwijdert zelf niets.

GDPR-verzoeken moet je wettelijk tijdig en zorgvuldig opvolgen. Kijk dit overzicht dus regelmatig na. Het aantal onverwerkte verzoeken staat ook als actiepunt op het dashboard.

## 13. Veelgestelde vragen & tips

**Ik zie mijn wijziging niet op de live site.** Controleer of de pagina op **"Gepubliceerd"** staat (bij contentpagina's) en of je wel degelijk op "Opslaan" geklikt hebt. Gebruik bij twijfel de knop "Bekijk pagina" of "Voorbeeld bekijken" in het bewerkscherm.

**Wat is een slug?** Het stuk van het webadres (URL) dat uit de titel of naam gemaakt wordt, bv. "Over ons" → `over-ons` → `/pagina/over-ons`. Je mag de slug zelf aanpassen, maar doe dat liever niet bij een pagina die al gedeeld is, want dan werken de oude links niet meer.

**Waarom kan ik deze pagina of dit team niet verwijderen?** Waarschijnlijk verwijst er nog een navigatie-item naar. De foutmelding zegt welk item je eerst moet aanpassen of verwijderen op de Navigatie-pagina.

**Waarom staat er "X" in plaats van een getal bij een team?** Dat veld (bv. "Aantal bekers") is nog niet ingevuld. Vul het in bij het team, of laat het leeg als het niet van toepassing is (bv. "Europese wedstrijden" voor een team dat nooit Europees speelde). Die badge wordt dan niet getoond.

**Wat gebeurt er met de oude afbeelding als ik ze vervang?** Upload je een nieuwe afbeelding op een plek waar er al een stond, dan wordt de oude automatisch van de server verwijderd. Dat geldt overal: producten, pagina's, teams, nieuws, sponsors ...

**Ik ben mijn wachtwoord vergeten.** Je kan het niet zelf resetten, en een andere admin kan dat ook niet via het adminpaneel. Iemand met technische kennis moet het rechtstreeks in de database aanpassen. Bewaar je wachtwoord dus goed.

**Wanneer gebruik ik de onderhoudsmodus en wanneer sluit ik enkel de webshop?** De onderhoudsmodus (op het dashboard) legt de hele site plat voor bezoekers. Gebruik die enkel bij grote wijzigingen. Als je de webshop sluit (Webshop → Instellingen), stopt enkel de verkoop en blijft de rest van de site (nieuws, pagina's, teams ...) gewoon werken.
