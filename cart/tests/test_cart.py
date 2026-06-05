from decimal import Decimal

from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from cart.cart import CART_SESSION_KEY, Cart
from cart.context_processors import cart as cart_context_processor
from catalog.models import Book, Category


class CartTests(TestCase):
    def setUp(self):
        self.session = SessionStore()
        self.session.create()
        self.cart = Cart(self.session)
        self.category = Category.objects.create(name="Ficción", slug="ficcion")
        self.book = Book.objects.create(
            title="Libro de prueba",
            author="Autor Test",
            price=Decimal("25000"),
            condition=Book.Condition.BUENO,
            category=self.category,
            slug="libro-prueba",
        )

    def test_add_increments_quantity(self):
        self.assertTrue(self.cart.add(self.book, qty=2))
        self.assertEqual(self.cart.get_quantity(self.book), 2)
        self.assertEqual(len(self.cart), 2)

    def test_add_returns_false_when_already_in_cart(self):
        self.cart.add(self.book)
        self.assertFalse(self.cart.add(self.book))

    def test_update_changes_quantity(self):
        self.cart.add(self.book, qty=1)
        self.cart.update(self.book, 3)
        self.assertEqual(self.cart.get_quantity(self.book), 3)

    def test_update_zero_removes_item(self):
        self.cart.add(self.book)
        self.cart.update(self.book, 0)
        self.assertNotIn(self.book, self.cart)
        self.assertEqual(len(self.cart), 0)

    def test_remove_deletes_item(self):
        self.cart.add(self.book)
        self.cart.remove(self.book)
        self.assertNotIn(self.book, self.cart)

    def test_total_price_sums_line_subtotals(self):
        self.cart.add(self.book, qty=2, override=True)
        self.assertEqual(self.cart.total_price, Decimal("50000"))

    def test_len_returns_total_units(self):
        self.cart.add(self.book, qty=2, override=True)
        self.assertEqual(len(self.cart), 2)

    def test_tolerates_nonexistent_book_in_session(self):
        self.session[CART_SESSION_KEY] = {"99999": 1}
        self.cart = Cart(self.session)
        items = list(self.cart)
        self.assertEqual(items, [])
        self.assertEqual(self.session[CART_SESSION_KEY], {})

    def test_context_processor_exposes_count(self):
        self.cart.add(self.book, qty=2, override=True)
        request = RequestFactory().get("/")
        request.session = self.session
        context = cart_context_processor(request)
        self.assertEqual(context["cart_item_count"], 2)
        self.assertEqual(len(context["cart"]), 2)
