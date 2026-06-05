"""
Integración: flujo navegable completo alineado con las 5 misiones MAZE.
"""

from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from cart.cart import Cart
from catalog.models import Book
from orders.models import Order

User = get_user_model()

ADDRESS_DATA = {
    "line1": "Carrera 7 # 45-10",
    "city": "Bogotá",
    "department": "Cundinamarca",
    "postal_code": "110111",
    "phone": "3001234567",
    "instructions": "Dejar en portería",
}

PAYMENT_DATA = {
    "payment_method": "pse",
    "pse_bank": "bancolombia",
    "pse_person_type": "natural",
}


class MazePurchaseFlowTests(TestCase):
    """Flujo completo: registro → catálogo → carrito → checkout → historial."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_catalog")

    def setUp(self):
        self.client = self.client_class()
        self.password = "SecurePass123!"
        self.email = "maze.user@example.com"

    def _register(self):
        """Misión 1 MAZE: registrarse como nuevo usuario."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Usuario MAZE",
                "email": self.email,
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email=self.email).exists())

    def _login(self):
        """Misión 2 MAZE: iniciar sesión con cuenta existente."""
        self.client.logout()
        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": self.email,
                "password": self.password,
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_full_purchase_flow_maze_missions(self):
        # Misión 1: Registro
        self._register()
        self.assertTrue(self.client.session.get("_auth_user_id"))

        # Misión 2: Login (cuenta existente)
        self._login()
        self.assertTrue(self.client.session.get("_auth_user_id"))

        # Misión 3: Buscar García Márquez y ver detalle
        catalog_response = self.client.get(reverse("catalog:index"), {"q": "García"})
        self.assertEqual(catalog_response.status_code, 200)
        self.assertContains(catalog_response, "Cien años de soledad")

        garcia_book = Book.objects.get(title="Cien años de soledad")
        detail_response = self.client.get(garcia_book.get_absolute_url())
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Gabriel García Márquez")

        # Misión 4: Agregar al carrito, ver, actualizar y eliminar
        add_response = self.client.post(
            reverse("cart:add", kwargs={"slug": garcia_book.slug}),
            {"quantity": 1},
        )
        self.assertEqual(add_response.status_code, 302)

        cart_response = self.client.get(reverse("cart:detail"))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Cien años de soledad")

        update_response = self.client.post(
            reverse("cart:update", kwargs={"slug": garcia_book.slug}),
            {"quantity": 2},
        )
        self.assertEqual(update_response.status_code, 302)

        remove_response = self.client.post(
            reverse("cart:remove", kwargs={"slug": garcia_book.slug}),
        )
        self.assertEqual(remove_response.status_code, 302)

        # Volver a agregar para checkout
        self.client.post(
            reverse("cart:add", kwargs={"slug": garcia_book.slug}),
            {"quantity": 1},
        )

        # Misión 5: Checkout completo hasta confirmación
        checkout_get = self.client.get(reverse("orders:checkout"))
        self.assertEqual(checkout_get.status_code, 200)

        checkout_post = self.client.post(reverse("orders:checkout"), ADDRESS_DATA)
        self.assertEqual(checkout_post.status_code, 302)

        payment_get = self.client.get(reverse("orders:payment"))
        self.assertEqual(payment_get.status_code, 200)

        payment_post = self.client.post(reverse("orders:payment"), PAYMENT_DATA)
        self.assertEqual(payment_post.status_code, 302)

        review_response = self.client.get(reverse("orders:review"))
        self.assertEqual(review_response.status_code, 200)
        self.assertContains(review_response, "Cien años de soledad")

        place_response = self.client.post(reverse("orders:place"))
        self.assertEqual(place_response.status_code, 302)

        order = Order.objects.get(user__email=self.email)
        self.assertRegex(order.number, r"^CMA-\d{6}$")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(
            order.total,
            order.subtotal + Decimal(str(settings.SHIPPING_COST)),
        )

        confirmation_response = self.client.get(
            reverse("orders:confirmation", kwargs={"number": order.number})
        )
        self.assertEqual(confirmation_response.status_code, 200)
        self.assertContains(confirmation_response, order.number)

        # Carrito vacío tras confirmar
        session = self.client.session
        cart = Cart(session)
        self.assertEqual(len(cart), 0)

        # Historial y detalle del pedido
        history_response = self.client.get(reverse("orders:history"))
        self.assertEqual(history_response.status_code, 200)
        self.assertContains(history_response, order.number)

        detail_order_response = self.client.get(
            reverse("orders:order_detail", kwargs={"number": order.number})
        )
        self.assertEqual(detail_order_response.status_code, 200)
        self.assertContains(detail_order_response, "Cien años de soledad")

    def test_anonymous_cannot_access_protected_views(self):
        protected_urls = [
            reverse("orders:checkout"),
            reverse("orders:history"),
            reverse("accounts:profile"),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("accounts:login"), response.url)

    def test_user_cannot_view_another_users_order(self):
        self._register()
        garcia_book = Book.objects.get(title="Cien años de soledad")
        self.client.post(
            reverse("cart:add", kwargs={"slug": garcia_book.slug}),
            {"quantity": 1},
        )
        self.client.post(reverse("orders:checkout"), ADDRESS_DATA)
        self.client.post(reverse("orders:payment"), PAYMENT_DATA)
        self.client.post(reverse("orders:place"))
        order = Order.objects.get(user__email=self.email)

        other = User.objects.create_user(
            username="otro@example.com",
            email="otro@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(other)
        response = self.client.get(
            reverse("orders:order_detail", kwargs={"number": order.number})
        )
        self.assertEqual(response.status_code, 404)
