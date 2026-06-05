"""Helpers de sesión para el flujo de checkout (pasos 1–3)."""

CHECKOUT_SESSION_KEY = "checkout"


def _get_checkout(session):
    checkout = session.get(CHECKOUT_SESSION_KEY)
    if checkout is None:
        checkout = session[CHECKOUT_SESSION_KEY] = {}
    return checkout


def get_checkout_address(request):
    return _get_checkout(request.session).get("address")


def set_checkout_address(request, address_data):
    checkout = _get_checkout(request.session)
    checkout["address"] = address_data
    request.session.modified = True


def get_checkout_payment(request):
    return _get_checkout(request.session).get("payment")


def set_checkout_payment(request, payment_data):
    checkout = _get_checkout(request.session)
    checkout["payment"] = payment_data
    request.session.modified = True


def clear_checkout(request):
    if CHECKOUT_SESSION_KEY in request.session:
        del request.session[CHECKOUT_SESSION_KEY]
        request.session.modified = True


def address_to_dict(address):
    """Convierte un modelo Address a dict para sesión."""
    return {
        "line1": address.line1,
        "city": address.city,
        "department": address.department,
        "postal_code": address.postal_code,
        "phone": address.phone,
        "instructions": address.instructions or "",
    }
