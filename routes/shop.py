"""
routes/shop.py
---------------
De webshop: productoverzicht, productdetail, tickets voor wedstrijden,
winkelmandje (met optionele bedrukking per stuk), afrekenen via Stripe
Checkout (incl. gratis verzending vanaf een drempelbedrag), en de Stripe
webhook.

Cart-structuur in de sessie:
    session["cart"] = {
        "<cart_item_id (uuid)>": {
            "variant_id": int, "quantity": int,
            "print_front": str | None, "print_back": str | None,
        },
        "<cart_item_id (uuid)>": {
            "ticket_type_id": int, "quantity": int,
        },
        ...
    }
Elke combinatie van variant + bedrukking krijgt een eigen regel, zodat je
bv. twee T-shirts met elk een andere opdruk apart kan bestellen. Tickets
krijgen één regel per tickettype.

Tickets en producten kunnen samen in één bestelling. Bevat de bestelling
enkel tickets, dan vraagt Stripe geen verzendadres en zijn er geen
verzendkosten; de drempel voor gratis verzending telt enkel producten.
"""

import time
from collections import defaultdict
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, g
import stripe

from extensions import db, csrf
from models import (
    Product, ProductVariant, Order, OrderLine, TicketWedstrijd, TicketType, TicketLijn, nu_belgisch,
)
from utils.auth import login_required
from utils.mail import send_order_confirmation_mail, send_admin_cancellation_mail

shop_bp = Blueprint("shop", __name__)


def line_unit_price(base_price, print_front, print_back):
    """Prijs per stuk: basisprijs van de variant + €5 per bedrukte zijde."""
    printing_sides = (1 if print_front else 0) + (1 if print_back else 0)
    return base_price + printing_sides * current_app.config["PRINTING_COST_PER_SIDE"]


def get_shipping_rate():
    """
    Haalt de 'Verzendingskosten' shipping rate rechtstreeks op via zijn ID.
    Geeft None terug als het ID niet ingesteld is, niet meer bestaat, of niet
    actief is - de checkout crasht dan niet, maar rekent gewoon geen
    verzendkosten aan (beter dan een kapotte checkout).
    """
    rate_id = current_app.config["STRIPE_SHIPPING_RATE_ID"]
    if not rate_id:
        current_app.logger.warning("STRIPE_SHIPPING_RATE_ID is niet ingesteld in .env")
        return None

    stripe.api_key = current_app.config["STRIPE_API_KEY"]
    try:
        rate = stripe.ShippingRate.retrieve(rate_id)
    except stripe.error.InvalidRequestError:
        current_app.logger.exception(f"Shipping rate '{rate_id}' bestaat niet in deze Stripe-omgeving")
        return None
    except stripe.error.StripeError:
        current_app.logger.exception("Kon shipping rate niet ophalen bij Stripe")
        return None

    if not rate.active:
        current_app.logger.warning(f"Shipping rate '{rate_id}' bestaat, maar staat niet actief")
        return None

    return rate


def _stripe_order_id(stripe_object):
    """order_id uit de metadata van een Stripe-object (Checkout Session of
    PaymentIntent), of None. Sinds stripe-python v13 is een StripeObject
    geen dict meer: .get() bestaat niet meer (AttributeError), enkel
    ['sleutel'] en 'sleutel' in obj werken nog."""
    if "metadata" not in stripe_object or not stripe_object["metadata"]:
        return None
    metadata = stripe_object["metadata"]
    return metadata["order_id"] if "order_id" in metadata else None


def _get_cart_items():
    """Zet de sessie-cart om naar een lijst met volledige variant/product-info."""
    items = []
    cart = session.get("cart", {})

    for cart_item_id, line in cart.items():
        if "ticket_type_id" in line:
            ticket_type = TicketType.query.get(line["ticket_type_id"])
            if ticket_type is None:
                continue
            items.append({
                "cart_item_id": cart_item_id,
                "type": "ticket",
                "ticket_type": ticket_type,
                "wedstrijd": ticket_type.wedstrijd,
                "product": None,
                "variant": None,
                "quantity": line["quantity"],
                "price": ticket_type.prijs,
                "subtotal": ticket_type.prijs * line["quantity"],
                "print_front": None,
                "print_back": None,
            })
            continue

        variant = ProductVariant.query.get(line["variant_id"])
        if variant is None:
            continue

        print_front = line.get("print_front")
        print_back = line.get("print_back")
        price = line_unit_price(variant.price, print_front, print_back)

        items.append({
            "cart_item_id": cart_item_id,
            "type": "product",
            "product": variant.product,
            "variant": variant,
            "quantity": line["quantity"],
            "price": price,
            "subtotal": price * line["quantity"],
            "print_front": print_front,
            "print_back": print_back,
        })

    return items


@shop_bp.route("/webshop-gesloten")
def gesloten():
    """Bereikbaar voor iedereen, ook als de webshop dicht staat - zie
    app.py: check_webshop_actief stuurt bezoekers hier naartoe.

    503 + Retry-After i.p.v. de standaard 200, zelfde aanpak als
    onderhoud.html in app.py: zonder dit zag Google elke (al geïndexeerde)
    product-/categoriepagina redirecten naar een inhoudsarme 200-pagina
    zodra de webshop dichtgezet werd, en beoordeelde dat als "Soft 404" in
    Search Console - een 503 zegt expliciet dat dit tijdelijk is, zodat die
    productpagina's hun plek in de index behouden tot de shop heropent."""
    return render_template("shop/gesloten.html"), 503, {"Retry-After": "3600"}


def _komende_ticket_wedstrijden():
    """Actieve wedstrijden met open verkoop en minstens één actief tickettype."""
    wedstrijden = (
        TicketWedstrijd.query
        .filter(TicketWedstrijd.is_active.is_(True), TicketWedstrijd.datum_tijd > nu_belgisch())
        .order_by(TicketWedstrijd.datum_tijd.asc())
        .all()
    )
    return [w for w in wedstrijden if w.actieve_ticket_types and not w.verkoop_gesloten]


@shop_bp.route("/producten")
def products():
    all_products = Product.query.filter_by(is_active=True).all()
    return render_template(
        "shop/products.html", products=all_products,
        ticket_wedstrijden=_komende_ticket_wedstrijden(),
    )


@shop_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    from flask import session as flask_session
    product = Product.query.get(product_id)
    if product is None:
        return redirect(url_for("shop.products"))

    if not product.is_active:
        # inactieve producten blijven zichtbaar voor admins (bv. om terug te activeren),
        # maar niet voor gewone bezoekers
        user_id = flask_session.get("user_id")
        from models import User
        user = User.query.get(user_id) if user_id else None
        if not user or not user.is_admin:
            return redirect(url_for("shop.products"))

    variants = ProductVariant.query.filter_by(product_id=product_id, is_active=True).all()
    return render_template("shop/product_detail.html", product=product, variants=variants)


def _render_cart(items, **extra):
    total_price = sum(item["subtotal"] for item in items)
    # Gratis verzending hangt enkel af van de producten: tickets worden niet
    # verzonden, en een duur ticket mag geen gratis verzending opleveren.
    product_subtotal = sum(item["subtotal"] for item in items if item["type"] == "product")
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    remaining_for_free_shipping = max(0, threshold - product_subtotal)
    return render_template(
        "shop/cart.html", items=items, total_price=total_price,
        heeft_producten=any(item["type"] == "product" for item in items),
        free_shipping_threshold=threshold, remaining_for_free_shipping=remaining_for_free_shipping,
        **extra,
    )


@shop_bp.route("/cart")
def cart():
    error = request.args.get("error")
    return _render_cart(_get_cart_items(), errors=[error] if error else None)


@shop_bp.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    variant_id = int(request.form["variant_id"])
    quantity = int(request.form.get("quantity", 1))
    print_front = (request.form.get("print_front") or "").strip() or None
    print_back = (request.form.get("print_back") or "").strip() or None

    # Nooit blindelings op de UI vertrouwen: een inactieve of niet-bestaande
    # variant mag hoe dan ook niet toegevoegd kunnen worden.
    variant = ProductVariant.query.get(variant_id)
    if not variant or not variant.is_active:
        return redirect(url_for("shop.products"))

    cart = session.get("cart", {})

    # Zelfde variant MET exact dezelfde bedrukking -> aantal optellen.
    # Andere (of geen) bedrukking -> altijd een nieuwe regel.
    existing_key = next(
        (key for key, line in cart.items()
         if line.get("variant_id") == variant_id
         and line.get("print_front") == print_front
         and line.get("print_back") == print_back),
        None
    )

    if existing_key:
        cart[existing_key]["quantity"] += quantity
    else:
        cart[uuid4().hex] = {
            "variant_id": variant_id,
            "quantity": quantity,
            "print_front": print_front,
            "print_back": print_back,
        }

    session["cart"] = cart
    return redirect(url_for("shop.cart"))


def _tickets_in_cart_per_wedstrijd(cart):
    """{wedstrijd_id: aantal tickets} voor de ticketregels in de sessie-cart."""
    aantallen = defaultdict(int)
    for line in cart.values():
        if "ticket_type_id" not in line:
            continue
        ticket_type = TicketType.query.get(line["ticket_type_id"])
        if ticket_type is not None:
            aantallen[ticket_type.wedstrijd_id] += line["quantity"]
    return aantallen


@shop_bp.route("/tickets")
def tickets():
    """Komende wedstrijden waarvoor tickets te koop zijn."""
    return render_template("shop/tickets.html", wedstrijden=_komende_ticket_wedstrijden())


@shop_bp.route("/tickets/<int:wedstrijd_id>")
def ticket_detail(wedstrijd_id):
    wedstrijd = TicketWedstrijd.query.get(wedstrijd_id)
    if wedstrijd is None or not wedstrijd.is_active:
        return redirect(url_for("shop.tickets"))
    return render_template(
        "shop/ticket_detail.html", wedstrijd=wedstrijd,
        beschikbaar=wedstrijd.aantal_beschikbaar(), error=request.args.get("error"),
    )


@shop_bp.route("/add_tickets_to_cart", methods=["POST"])
def add_tickets_to_cart():
    """Voegt in één keer tickets van één of meerdere types voor dezelfde
    wedstrijd toe (formuliervelden 'aantal_<ticket_type_id>')."""
    wedstrijd = TicketWedstrijd.query.get(request.form.get("wedstrijd_id", type=int) or 0)
    if wedstrijd is None or not wedstrijd.is_koopbaar:
        return redirect(url_for("shop.tickets"))

    gekozen = []
    for ticket_type in wedstrijd.actieve_ticket_types:
        aantal = request.form.get(f"aantal_{ticket_type.id}", type=int) or 0
        if aantal > 0:
            gekozen.append((ticket_type, aantal))

    if not gekozen:
        return redirect(url_for("shop.ticket_detail", wedstrijd_id=wedstrijd.id, error="Kies minstens één ticket."))

    cart = session.get("cart", {})
    al_in_mandje = _tickets_in_cart_per_wedstrijd(cart)[wedstrijd.id]
    nieuw_totaal = al_in_mandje + sum(aantal for _, aantal in gekozen)
    if wedstrijd.max_per_bestelling is not None and nieuw_totaal > wedstrijd.max_per_bestelling:
        return redirect(url_for(
            "shop.ticket_detail", wedstrijd_id=wedstrijd.id,
            error=f"Je kan maximaal {wedstrijd.max_per_bestelling} tickets per bestelling kopen voor deze wedstrijd"
                  + (f" (waarvan je er al {al_in_mandje} in je winkelmandje hebt)." if al_in_mandje else "."),
        ))
    beschikbaar = wedstrijd.aantal_beschikbaar()
    if beschikbaar is not None and nieuw_totaal > beschikbaar:
        return redirect(url_for(
            "shop.ticket_detail", wedstrijd_id=wedstrijd.id,
            error=f"Er zijn nog maar {beschikbaar} tickets beschikbaar (waarvan je er al {al_in_mandje} in je winkelmandje hebt).",
        ))

    for ticket_type, aantal in gekozen:
        existing_key = next(
            (key for key, line in cart.items() if line.get("ticket_type_id") == ticket_type.id),
            None
        )
        if existing_key:
            cart[existing_key]["quantity"] += aantal
        else:
            cart[uuid4().hex] = {"ticket_type_id": ticket_type.id, "quantity": aantal}

    session["cart"] = cart
    return redirect(url_for("shop.cart"))


@shop_bp.route("/adjust_cart", methods=["POST"])
def adjust_cart():
    cart_item_id = request.form["cart_item_id"]
    delta = int(request.form["quantity"])

    cart = session.get("cart", {})
    if cart_item_id in cart:
        line = cart[cart_item_id]
        ticket_type = TicketType.query.get(line["ticket_type_id"]) if "ticket_type_id" in line else None
        if ticket_type is not None and delta > 0:
            limiet = ticket_type.wedstrijd.max_per_bestelling
            if limiet is not None and _tickets_in_cart_per_wedstrijd(cart)[ticket_type.wedstrijd_id] + delta > limiet:
                return redirect(url_for(
                    "shop.cart",
                    error=f"Je kan maximaal {limiet} tickets per bestelling kopen voor {ticket_type.wedstrijd.titel}.",
                ))
        new_qty = line["quantity"] + delta
        if new_qty <= 0:
            del cart[cart_item_id]
        else:
            cart[cart_item_id]["quantity"] = new_qty
    session["cart"] = cart

    return redirect(url_for("shop.cart"))


@shop_bp.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    cart_item_id = request.form["cart_item_id"]
    cart = session.get("cart", {})
    cart.pop(cart_item_id, None)
    session["cart"] = cart
    return redirect(url_for("shop.cart"))


@shop_bp.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("shop.cart"))


@shop_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    from flask import g

    items = _get_cart_items()
    if not items:
        return redirect(url_for("shop.cart"))

    akkoord_voorwaarden = request.form.get("akkoord_voorwaarden") == "1"

    errors = []
    if not akkoord_voorwaarden:
        errors.append("Je moet akkoord gaan met de algemene voorwaarden en het privacybeleid om te bestellen.")
    product_items = [item for item in items if item["type"] == "product"]
    ticket_items = [item for item in items if item["type"] == "ticket"]

    for item in product_items:
        variant = item["variant"]
        if not variant.is_active:
            errors.append(f"{item['product'].product_name} ({variant.color} / {variant.size}) is niet meer beschikbaar")
        elif variant.stock < item["quantity"]:
            errors.append(f"Onvoldoende voorraad voor {item['product'].product_name} ({variant.color} / {variant.size})")

    tickets_per_wedstrijd = defaultdict(int)
    for item in ticket_items:
        wedstrijd = item["wedstrijd"]
        if not item["ticket_type"].is_active or not wedstrijd.is_active:
            errors.append(f"Ticket '{item['ticket_type'].naam}' voor {wedstrijd.titel} is niet meer beschikbaar")
        elif wedstrijd.verkoop_gesloten:
            errors.append(f"De ticketverkoop voor {wedstrijd.titel} is gesloten")
        tickets_per_wedstrijd[wedstrijd] += item["quantity"]
    for wedstrijd, aantal in tickets_per_wedstrijd.items():
        if wedstrijd.max_per_bestelling is not None and aantal > wedstrijd.max_per_bestelling:
            errors.append(f"Je kan maximaal {wedstrijd.max_per_bestelling} tickets per bestelling kopen voor {wedstrijd.titel}")
        beschikbaar = wedstrijd.aantal_beschikbaar()
        if beschikbaar is not None and aantal > beschikbaar:
            errors.append(f"Voor {wedstrijd.titel} zijn nog maar {beschikbaar} tickets beschikbaar")

    subtotal = sum(item["subtotal"] for item in items)
    product_subtotal = sum(item["subtotal"] for item in product_items)

    if errors:
        return _render_cart(items, errors=errors, akkoord_voorwaarden=akkoord_voorwaarden)

    # Gratis verzending vanaf de drempel: onder de drempel de shipping rate
    # toevoegen, erboven gewoon geen shipping_options meesturen. Enkel
    # tickets -> niets te verzenden, dus ook geen verzendkosten.
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    shipping_rate = None
    shipping_cost = 0.0
    if product_items and product_subtotal < threshold:
        shipping_rate = get_shipping_rate()
        if shipping_rate:
            shipping_cost = shipping_rate.fixed_amount.amount / 100
        else:
            current_app.logger.warning("Geen actieve Stripe shipping rate gevonden voor STRIPE_SHIPPING_RATE_ID")

    # Voorraad afschrijven en order aanmaken
    order = Order(user_id=g.user.user_id, total_price=subtotal, shipping_cost=shipping_cost)
    for item in product_items:
        item["variant"].stock -= item["quantity"]
        order.lines.append(OrderLine(
            product_id=item["product"].product_id,
            variant_id=item["variant"].variant_id,
            quantity=item["quantity"],
            price=item["price"],
            print_front=item["print_front"],
            print_back=item["print_back"],
        ))
    # Tickets hebben geen voorraadteller: TicketWedstrijd.aantal_verkocht()
    # telt deze regels zolang de bestelling niet mislukt/geannuleerd is.
    for item in ticket_items:
        order.ticket_lines.append(TicketLijn(
            ticket_type_id=item["ticket_type"].id,
            quantity=item["quantity"],
            price=item["price"],
        ))
    db.session.add(order)
    db.session.commit()

    # Cart meteen leegmaken (niet pas bij checkout_success): zo maakt een
    # dubbele submit (dubbelklik, terug-knop + opnieuw verzenden) geen tweede
    # order met een tweede voorraadafschrijving voor dezelfde winkelmand aan.
    session["cart"] = {}

    stripe.api_key = current_app.config["STRIPE_API_KEY"]

    def _line_item_naam(item):
        if item["type"] == "ticket":
            wedstrijd = item["wedstrijd"]
            return f"Ticket {wedstrijd.titel} ({wedstrijd.datum_tijd.strftime('%d/%m/%Y %H:%M')}) - {item['ticket_type'].naam}"
        return item["product"].product_name + f" ({item['variant'].color} / {item['variant'].size})"

    line_items = [{
        "price_data": {
            "currency": "eur",
            "product_data": {"name": _line_item_naam(item)},
            "unit_amount": round(item["price"] * 100),
        },
        "quantity": item["quantity"],
    } for item in items]

    checkout_session_params = dict(
        # "card" omvat ook Apple Pay en Google Pay. Elke methode moet ook in
        # het Stripe-dashboard (Settings -> Payment methods) aan staan.
        payment_method_types=["card", "bancontact"],
        mode="payment",
        line_items=line_items,
        metadata={"user_id": g.user.user_id, "order_id": order.order_id},
        payment_intent_data={"metadata": {"user_id": g.user.user_id, "order_id": order.order_id}},
        success_url=url_for("shop.checkout_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url_for("shop.cart", _external=True),
    )
    if product_items:
        checkout_session_params["shipping_address_collection"] = {"allowed_countries": ["BE", "NL", "LU"]}
    if shipping_rate:
        checkout_session_params["shipping_options"] = [{"shipping_rate": shipping_rate.id}]
    if ticket_items:
        # Een openstaande bestelling houdt haar tickets vast tot de betaling
        # mislukt of de Stripe-sessie verloopt (standaard pas na 24u). Bij een
        # beperkt aantal plaatsen zo snel mogelijk vrijgeven: 30 minuten is
        # het minimum dat Stripe toelaat (+1 minuut marge voor klokverschil).
        checkout_session_params["expires_at"] = int(time.time()) + 31 * 60

    checkout_session = stripe.checkout.Session.create(**checkout_session_params)
    return redirect(checkout_session.url, code=303)


@shop_bp.route("/webhook", methods=["POST"])
@csrf.exempt
def stripe_webhook():
    stripe.api_key = current_app.config["STRIPE_API_KEY"]
    endpoint_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        current_app.logger.error("Webhook: ongeldige payload ontvangen")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        current_app.logger.error("Webhook: signature verification mislukt")
        return "Invalid signature", 400

    event_type = event["type"]
    data_object = event["data"]["object"]
    order_id = _stripe_order_id(data_object)

    if not order_id:
        current_app.logger.warning(f"Webhook event {event_type} ontvangen zonder order_id, genegeerd.")
        return "", 200

    order = Order.query.get(int(order_id))
    if order is None:
        return "", 200

    # Stripe garandeert enkel 'at-least-once' bezorging - hetzelfde event kan
    # meermaals binnenkomen. De payment_status-checks hieronder (en newly_paid
    # voor de mail) zorgen dat een herhaald event geen tweede bevestigingsmail
    # stuurt en de voorraad niet dubbel terugboekt.
    #
    # Enkel events op de Checkout Session zelf zijn definitief. Een losse
    # payment_intent.payment_failed NIET: op de Stripe-betaalpagina kan de
    # klant na een mislukte poging (bv. geannuleerd in de Bancontact-app)
    # gewoon opnieuw proberen. Die bestelling toen al op 'failed' zetten
    # boekte de voorraad terug, terwijl een tweede poging nog kon slagen.
    # Wordt er nooit betaald, dan komt checkout.session.expired vanzelf.
    newly_paid = False
    try:
        # completed = betaalpagina afgerond. Bij trage methodes (bv. SEPA)
        # is het geld dan nog niet binnen (payment_status 'unpaid') en volgt
        # later async_payment_succeeded of async_payment_failed.
        is_betaald = (
            event_type == "checkout.session.completed"
            and "payment_status" in data_object and data_object["payment_status"] == "paid"
        ) or event_type == "checkout.session.async_payment_succeeded"
        if is_betaald:
            if order.payment_status != "paid":
                order.payment_status = "paid"
                db.session.commit()
                newly_paid = True
        elif event_type in (
            "checkout.session.async_payment_failed",
            "checkout.session.expired",
        ):
            if order.payment_status not in ("paid", "failed"):
                order.payment_status = "failed"
                # Betaling mislukt/verlopen -> de bij checkout afgeschreven
                # voorraad terugboeken (zelfde principe als bij handmatige
                # annulatie in het adminpaneel). Tickets komen vanzelf vrij:
                # een 'failed' bestelling telt niet mee in aantal_verkocht().
                for line in order.lines:
                    if line.variant:
                        line.variant.stock += line.quantity
                db.session.commit()
    except Exception:
        current_app.logger.exception(f"Webhook: verwerken van event {event_type} voor order {order_id} is mislukt")
        return "Internal error while processing webhook", 500

    # Bevestigingsmail apart van de betaalstatus-update: een SMTP-fout mag nooit
    # voorkomen dat Stripe een 200 krijgt voor een betaling die wel degelijk
    # correct verwerkt is (anders eindeloze retries van hetzelfde event).
    if newly_paid:
        try:
            send_order_confirmation_mail(order)
        except Exception:
            current_app.logger.exception(f"Bevestigingsmail versturen voor order {order_id} is mislukt")

    return "", 200


@shop_bp.route("/checkout_success")
@login_required
def checkout_success():
    session_id = request.args.get("session_id")
    if session_id is None:
        return redirect(url_for("shop.cart"))

    stripe.api_key = current_app.config["STRIPE_API_KEY"]
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    if checkout_session.payment_status != "paid":
        return redirect(url_for("shop.cart"))

    order_id = _stripe_order_id(checkout_session)
    order = Order.query.get(int(order_id)) if order_id else None
    # Niet enkel op een bestaande order controleren: zonder deze check kan
    # elke ingelogde gebruiker de orderbevestiging van een ANDERE klant zien
    # door enkel een geldig session_id te bemachtigen (bv. via een gedeelde
    # link) - de order moet ook echt van de ingelogde gebruiker zijn.
    if order is None or order.user_id != g.user.user_id:
        return redirect(url_for("shop.cart"))

    session["cart"] = {}
    return render_template("shop/checkout_success.html", order=order)
