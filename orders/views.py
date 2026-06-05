from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from cart.cart import Cart

from .checkout import (
    clear_checkout,
    get_checkout_address,
    get_checkout_payment,
    set_checkout_address,
    set_checkout_payment,
)
from .forms import AddressForm, PaymentForm
from .models import Address, Order, OrderItem, default_estimated_delivery

PAYMENT_LABELS = dict(Order.PaymentMethod.choices)


def _get_cart(request):
    return Cart(request.session)


def _cart_items_or_redirect(request):
    cart = _get_cart(request)
    items = list(cart)
    if not items:
        messages.warning(request, "Tu carrito está vacío. Añade libros antes de continuar.")
        return None, redirect("cart:detail")
    return items, None


def _require_address_or_redirect(request):
    address = get_checkout_address(request)
    if not address:
        messages.warning(request, "Completa la dirección de envío para continuar.")
        return None, redirect("orders:checkout")
    return address, None


def _require_payment_or_redirect(request):
    payment = get_checkout_payment(request)
    if not payment or not payment.get("method"):
        messages.warning(request, "Selecciona un método de pago para continuar.")
        return None, redirect("orders:payment")
    return payment, None


def _save_address_if_requested(user, form_data):
    if not form_data.get("save_address"):
        return
    Address.objects.create(
        user=user,
        line1=form_data["line1"],
        city=form_data["city"],
        department=form_data["department"],
        postal_code=form_data["postal_code"],
        phone=form_data["phone"],
        instructions=form_data.get("instructions", ""),
        is_saved=True,
        is_default=not Address.objects.filter(user=user).exists(),
    )


def _order_totals(cart):
    subtotal = cart.total_price
    shipping_cost = Decimal(str(settings.SHIPPING_COST))
    total = subtotal + shipping_cost
    return subtotal, shipping_cost, total


def _send_confirmation_email(request, order):
    user = request.user
    items_text = "\n".join(
        f"  - {item.title_snapshot} x{item.quantity}: ${item.line_subtotal:,.0f}"
        for item in order.items.all()
    )
    body = (
        f"Hola {user.get_full_name() or user.first_name or user.email},\n\n"
        f"Tu pedido {order.number} ha sido confirmado.\n\n"
        f"Dirección de envío:\n"
        f"  {order.shipping_line1}\n"
        f"  {order.shipping_city}, {order.shipping_department} {order.shipping_postal_code}\n"
        f"  Tel: {order.shipping_phone}\n"
        f"{f'  Instrucciones: {order.shipping_instructions}' if order.shipping_instructions else ''}\n\n"
        f"Método de pago: {order.get_payment_method_display()}\n\n"
        f"Artículos:\n{items_text}\n\n"
        f"Subtotal: ${order.subtotal:,.0f}\n"
        f"Envío: ${order.shipping_cost:,.0f}\n"
        f"Total: ${order.total:,.0f}\n\n"
        f"Entrega estimada: {order.estimated_delivery.strftime('%d/%m/%Y')}\n\n"
        f"Gracias por comprar en ComuniApp.\n"
    )
    send_mail(
        subject=f"Confirmación de pedido {order.number} — ComuniApp",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    items, redirect_response = _cart_items_or_redirect(request)
    if redirect_response:
        return redirect_response

    saved_addresses = Address.objects.filter(user=request.user, is_saved=True)
    session_address = get_checkout_address(request)

    if request.method == "POST":
        form = AddressForm(request.user, data=request.POST)
        if form.is_valid():
            data = {
                "line1": form.cleaned_data["line1"],
                "city": form.cleaned_data["city"],
                "department": form.cleaned_data["department"],
                "postal_code": form.cleaned_data["postal_code"],
                "phone": form.cleaned_data["phone"],
                "instructions": form.cleaned_data.get("instructions", ""),
            }
            set_checkout_address(request, data)
            _save_address_if_requested(request.user, form.cleaned_data)
            return redirect("orders:payment")
    else:
        initial = session_address or {}
        form = AddressForm(request.user, initial=initial)

    return render(
        request,
        "orders/address.html",
        {
            "form": form,
            "saved_addresses": saved_addresses,
            "checkout_step": 1,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def payment(request):
    items, redirect_response = _cart_items_or_redirect(request)
    if redirect_response:
        return redirect_response

    address, redirect_response = _require_address_or_redirect(request)
    if redirect_response:
        return redirect_response

    session_payment = get_checkout_payment(request)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            set_checkout_payment(request, form.payment_session_data())
            return redirect("orders:review")
    else:
        initial = {}
        if session_payment:
            initial["payment_method"] = session_payment.get("method", "")
        form = PaymentForm(initial=initial)

    return render(
        request,
        "orders/payment.html",
        {
            "form": form,
            "checkout_step": 2,
        },
    )


@login_required
def review(request):
    items, redirect_response = _cart_items_or_redirect(request)
    if redirect_response:
        return redirect_response

    address, redirect_response = _require_address_or_redirect(request)
    if redirect_response:
        return redirect_response

    payment_data, redirect_response = _require_payment_or_redirect(request)
    if redirect_response:
        return redirect_response

    cart = _get_cart(request)
    subtotal, shipping_cost, total = _order_totals(cart)
    payment_method = payment_data["method"]

    return render(
        request,
        "orders/review.html",
        {
            "cart_items": items,
            "address": address,
            "payment_method": payment_method,
            "payment_method_label": PAYMENT_LABELS.get(payment_method, payment_method),
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "total": total,
            "checkout_step": 3,
        },
    )


@login_required
@require_POST
def place(request):
    items, redirect_response = _cart_items_or_redirect(request)
    if redirect_response:
        return redirect_response

    address, redirect_response = _require_address_or_redirect(request)
    if redirect_response:
        return redirect_response

    payment_data, redirect_response = _require_payment_or_redirect(request)
    if redirect_response:
        return redirect_response

    cart = _get_cart(request)
    subtotal, shipping_cost, total = _order_totals(cart)

    order = Order.objects.create(
        user=request.user,
        number=Order.generate_number(),
        status=Order.Status.CONFIRMED,
        payment_method=payment_data["method"],
        shipping_line1=address["line1"],
        shipping_city=address["city"],
        shipping_department=address["department"],
        shipping_postal_code=address["postal_code"],
        shipping_phone=address["phone"],
        shipping_instructions=address.get("instructions", ""),
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        estimated_delivery=default_estimated_delivery(),
    )

    for item in items:
        book = item["book"]
        OrderItem.objects.create(
            order=order,
            book=book,
            title_snapshot=book.title,
            unit_price_snapshot=item["unit_price"],
            quantity=item["quantity"],
            line_subtotal=item["line_subtotal"],
        )

    cart.clear()
    clear_checkout(request)
    _send_confirmation_email(request, order)

    messages.success(request, f"¡Pedido {order.number} confirmado!")
    return redirect("orders:confirmation", number=order.number)


@login_required
def confirmation(request, number):
    order = get_object_or_404(Order, number=number, user=request.user)
    return render(
        request,
        "orders/confirmation.html",
        {
            "order": order,
            "checkout_step": 4,
        },
    )


def _user_saved_address(request, pk):
    return get_object_or_404(Address, pk=pk, user=request.user, is_saved=True)


@login_required
def history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "orders/history.html", {"orders": orders})


@login_required
def order_detail(request, number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        number=number,
        user=request.user,
    )
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user, is_saved=True)
    return render(
        request,
        "orders/address_list.html",
        {"addresses": addresses},
    )


@login_required
@require_http_methods(["GET", "POST"])
def address_add(request):
    if request.method == "POST":
        form = AddressForm(request.user, manage=True, data=request.POST)
        if form.is_valid():
            Address.objects.create(
                user=request.user,
                line1=form.cleaned_data["line1"],
                city=form.cleaned_data["city"],
                department=form.cleaned_data["department"],
                postal_code=form.cleaned_data["postal_code"],
                phone=form.cleaned_data["phone"],
                instructions=form.cleaned_data.get("instructions", ""),
                is_saved=True,
                is_default=not Address.objects.filter(
                    user=request.user, is_saved=True
                ).exists(),
            )
            messages.success(request, "Dirección guardada correctamente.")
            return redirect("orders:address_list")
    else:
        form = AddressForm(request.user, manage=True)

    return render(
        request,
        "orders/address_form.html",
        {"form": form, "page_title": "Agregar dirección", "is_edit": False},
    )


@login_required
@require_http_methods(["GET", "POST"])
def address_edit(request, pk):
    address = _user_saved_address(request, pk)

    if request.method == "POST":
        form = AddressForm(request.user, manage=True, data=request.POST)
        if form.is_valid():
            address.line1 = form.cleaned_data["line1"]
            address.city = form.cleaned_data["city"]
            address.department = form.cleaned_data["department"]
            address.postal_code = form.cleaned_data["postal_code"]
            address.phone = form.cleaned_data["phone"]
            address.instructions = form.cleaned_data.get("instructions", "")
            address.save()
            messages.success(request, "Dirección actualizada correctamente.")
            return redirect("orders:address_list")
    else:
        form = AddressForm(
            request.user,
            manage=True,
            initial={
                "line1": address.line1,
                "city": address.city,
                "department": address.department,
                "postal_code": address.postal_code,
                "phone": address.phone,
                "instructions": address.instructions,
            },
        )

    return render(
        request,
        "orders/address_form.html",
        {
            "form": form,
            "address": address,
            "page_title": "Editar dirección",
            "is_edit": True,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def address_delete(request, pk):
    address = _user_saved_address(request, pk)

    if request.method == "POST":
        address.delete()
        messages.success(request, "Dirección eliminada correctamente.")
        return redirect("orders:address_list")

    return render(
        request,
        "orders/address_delete.html",
        {"address": address},
    )
