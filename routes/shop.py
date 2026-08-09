"""
routes/shop.py
---------------
De webshop: productoverzicht, productdetail, winkelmandje (met optionele
bedrukking per stuk), afrekenen via Stripe Checkout (incl. gratis
verzending vanaf een drempelbedrag), en de Stripe webhook.

Cart-structuur in de sessie:
    session["cart"] = {
        "<cart_item_id (uuid)>": {
            "variant_id": int, "quantity": int,
            "print_front": str | None, "print_back": str | None,
        },
        ...
    }
Elke combinatie van variant + bedrukking krijgt een eigen regel, zodat je
bv. twee T-shirts met elk een andere opdruk apart kan bestellen.
"""

from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import stripe

from extensions import db, csrf
from models import Product, ProductVariant, Order, OrderLine
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


def _get_cart_items():
    """Zet de sessie-cart om naar een lijst met volledige variant/product-info."""
    items = []
    cart = session.get("cart", {})

    for cart_item_id, line in cart.items():
        variant = ProductVariant.query.get(line["variant_id"])
        if variant is None:
            continue

        print_front = line.get("print_front")
        print_back = line.get("print_back")
        price = line_unit_price(variant.price, print_front, print_back)

        items.append({
            "cart_item_id": cart_item_id,
            "product": variant.product,
            "variant": variant,
            "quantity": line["quantity"],
            "price": price,
            "subtotal": price * line["quantity"],
            "print_front": print_front,
            "print_back": print_back,
        })

    return items


@shop_bp.route("/producten")
def products():
    all_products = Product.query.filter_by(is_active=True).all()
    return render_template("shop/products.html", products=all_products)


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


@shop_bp.route("/cart")
def cart():
    items = _get_cart_items()
    total_price = sum(item["subtotal"] for item in items)
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    remaining_for_free_shipping = max(0, threshold - total_price)
    return render_template(
        "shop/cart.html", items=items, total_price=total_price,
        free_shipping_threshold=threshold, remaining_for_free_shipping=remaining_for_free_shipping,
    )


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
         if line["variant_id"] == variant_id
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


@shop_bp.route("/adjust_cart", methods=["POST"])
def adjust_cart():
    cart_item_id = request.form["cart_item_id"]
    delta = int(request.form["quantity"])

    cart = session.get("cart", {})
    if cart_item_id in cart:
        new_qty = cart[cart_item_id]["quantity"] + delta
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

    errors = []
    for item in items:
        variant = item["variant"]
        if not variant.is_active:
            errors.append(f"{item['product'].product_name} ({variant.color} / {variant.size}) is niet meer beschikbaar")
        elif variant.stock < item["quantity"]:
            errors.append(f"Onvoldoende voorraad voor {item['product'].product_name} ({variant.color} / {variant.size})")

    subtotal = sum(item["subtotal"] for item in items)

    if errors:
        threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
        remaining_for_free_shipping = max(0, threshold - subtotal)
        return render_template(
            "shop/cart.html", items=items, total_price=subtotal, errors=errors,
            remaining_for_free_shipping=remaining_for_free_shipping,
        )

    # Gratis verzending vanaf de drempel: onder de drempel de shipping rate
    # toevoegen, erboven gewoon geen shipping_options meesturen.
    threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    shipping_rate = None
    shipping_cost = 0.0
    if subtotal < threshold:
        shipping_rate = get_shipping_rate()
        if shipping_rate:
            shipping_cost = shipping_rate.fixed_amount.amount / 100
        else:
            current_app.logger.warning("Geen actieve Stripe shipping rate gevonden voor STRIPE_SHIPPING_RATE_ID")

    # Voorraad afschrijven en order aanmaken
    order = Order(user_id=g.user.user_id, total_price=subtotal, shipping_cost=shipping_cost)
    for item in items:
        item["variant"].stock -= item["quantity"]
        order.lines.append(OrderLine(
            product_id=item["product"].product_id,
            variant_id=item["variant"].variant_id,
            quantity=item["quantity"],
            price=item["price"],
            print_front=item["print_front"],
            print_back=item["print_back"],
        ))
    db.session.add(order)
    db.session.commit()

    # Cart meteen leegmaken (niet pas bij checkout_success): zo maakt een
    # dubbele submit (dubbelklik, terug-knop + opnieuw verzenden) geen tweede
    # order met een tweede voorraadafschrijving voor dezelfde winkelmand aan.
    session["cart"] = {}

    stripe.api_key = current_app.config["STRIPE_API_KEY"]

    line_items = [{
        "price_data": {
            "currency": "eur",
            "product_data": {
                "name": item["product"].product_name + f" ({item['variant'].color} / {item['variant'].size})",
            },
            "unit_amount": round(item["price"] * 100),
        },
        "quantity": item["quantity"],
    } for item in items]

    checkout_session_params = dict(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        shipping_address_collection={"allowed_countries": ["BE", "NL", "LU"]},
        metadata={"user_id": g.user.user_id, "order_id": order.order_id},
        payment_intent_data={"metadata": {"user_id": g.user.user_id, "order_id": order.order_id}},
        success_url=url_for("shop.checkout_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url_for("shop.cart", _external=True),
    )
    if shipping_rate:
        checkout_session_params["shipping_options"] = [{"shipping_rate": shipping_rate.id}]

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
    metadata = data_object.get("metadata", {}) or {}
    order_id = metadata.get("order_id")

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
    newly_paid = False
    try:
        if event_type == "checkout.session.completed":
            if order.payment_status != "paid":
                order.payment_status = "paid"
                db.session.commit()
                newly_paid = True
        elif event_type in (
            "checkout.session.async_payment_failed",
            "payment_intent.payment_failed",
            "checkout.session.expired",
        ):
            if order.payment_status not in ("paid", "failed"):
                order.payment_status = "failed"
                # Betaling mislukt/verlopen -> de bij checkout afgeschreven
                # voorraad terugboeken (zelfde principe als bij handmatige
                # annulatie in het adminpaneel).
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

    order_id = checkout_session.metadata.get("order_id")
    order = Order.query.get(int(order_id)) if order_id else None
    if order is None:
        return redirect(url_for("shop.cart"))

    session["cart"] = {}
    return render_template("shop/checkout_success.html", order=order)
