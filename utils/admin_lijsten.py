"""
utils/admin_lijsten.py
-----------------------
Gedeelde helpers voor de overzichtslijsten in het adminpaneel (bestellingen,
inschrijvingen, gebruikers, GDPR-verzoeken): zoeken, pagineren, de
geselecteerde rijen van een bulkactie en de "terug naar de lijst"-link van
een fiche. De bijhorende templatemacro's staan in
templates/admin/_lijst_macros.html.

Filters staan bewust in de URL (GET-parameters): zo kan je een gefilterde
lijst bookmarken, en brengt de fiche je terug naar exact dezelfde lijst.
"""

from flask import request

PER_PAGINA = 50


def zoekterm():
    """De zoekterm uit het zoekveld ('q'), zonder witruimte rond."""
    return (request.args.get("q") or "").strip()


def zoek_filter(term, *kolommen):
    """OR-filter dat 'term' (hoofdletterongevoelig) zoekt in de kolommen.
    % en _ in de zoekterm worden letterlijk genomen, niet als wildcard."""
    from sqlalchemy import or_

    patroon = "%" + term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    return or_(*(kolom.ilike(patroon, escape="\\") for kolom in kolommen))


def pagineer(query):
    """Pagina 'pagina' (1, 2, ...) van de query, PER_PAGINA rijen per pagina.
    Een te hoog of ongeldig paginanummer geeft een lege pagina i.p.v. een 404."""
    pagina = max(request.args.get("pagina", 1, type=int) or 1, 1)
    return query.paginate(page=pagina, per_page=PER_PAGINA, error_out=False)


def geselecteerde_ids():
    """De id's van de aangevinkte rijen van een bulkactie (veld 'ids')."""
    ids = []
    for waarde in request.form.getlist("ids"):
        try:
            ids.append(int(waarde))
        except ValueError:
            continue
    return ids


def terug_url(standaard):
    """De lijst-URL (met filters) waar de admin vandaan kwam - meegegeven als
    'terug' door de lijst - of anders 'standaard'. Enkel adminpagina's van
    deze site, zodat 'terug' geen open redirect wordt."""
    terug = request.values.get("terug") or ""
    if terug.startswith("/admin/") and not terug.startswith("//"):
        return terug
    return standaard
