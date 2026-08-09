"""
utils/sanitize.py
-------------------
Saniteert rich-text HTML (van de pagina-editor) vóór opslag in de database.
Enkel admins kunnen pagina's schrijven, maar we filteren toch server-side
tegen stored-XSS - clientside filtering (de editor) is geen garantie.
"""

import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s",
    "h2", "h3", "h4",
    "ul", "ol", "li",
    "a", "img",
    "blockquote",
    "table", "thead", "tbody", "tr", "th", "td",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "target", "rel"],
    "img": ["src", "alt"],
    "td": ["data-row"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(raw_html):
    """Geeft een veilige subset van de opgegeven HTML terug (lege string als raw_html leeg is)."""
    if not raw_html:
        return ""

    cleaned = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return cleaned
