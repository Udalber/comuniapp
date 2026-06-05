from .cart import Cart


def cart(request):
    """Expone el carrito y el contador para el badge del navbar."""
    cart_obj = Cart(request.session)
    return {
        "cart": cart_obj,
        "cart_item_count": len(cart_obj),
    }
