from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.models import Book, Category
from orders.models import Order, OrderItem

User = get_user_model()


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="comprador@example.com",
            email="comprador@example.com",
            password="SecurePass123!",
        )
        self.category = Category.objects.create(name="Ficción", slug="ficcion")
        self.book = Book.objects.create(
            title="Libro pedido",
            author="Autor",
            price=Decimal("30000"),
            condition=Book.Condition.BUENO,
            category=self.category,
            slug="libro-pedido",
        )

    def test_generate_number_is_unique_and_formatted(self):
        numbers = {Order.generate_number() for _ in range(20)}
        self.assertEqual(len(numbers), 20)
        for number in numbers:
            self.assertRegex(number, r"^CMA-\d{6}$")

    def test_order_total_equals_subtotal_plus_shipping(self):
        subtotal = Decimal("30000")
        shipping = Decimal(str(settings.SHIPPING_COST))
        order = Order.objects.create(
            user=self.user,
            number=Order.generate_number(),
            payment_method=Order.PaymentMethod.PSE,
            shipping_line1="Calle 1",
            shipping_city="Bogotá",
            shipping_department="Cundinamarca",
            shipping_postal_code="110111",
            shipping_phone="3001234567",
            subtotal=subtotal,
            shipping_cost=shipping,
            total=subtotal + shipping,
            estimated_delivery="2026-06-12",
        )
        self.assertEqual(order.total, subtotal + shipping)

    def test_order_item_stores_snapshots(self):
        order = Order.objects.create(
            user=self.user,
            number=Order.generate_number(),
            payment_method=Order.PaymentMethod.NEQUI,
            shipping_line1="Calle 1",
            shipping_city="Bogotá",
            shipping_department="Cundinamarca",
            shipping_postal_code="110111",
            shipping_phone="3001234567",
            subtotal=Decimal("30000"),
            shipping_cost=Decimal("8000"),
            total=Decimal("38000"),
            estimated_delivery="2026-06-12",
        )
        item = OrderItem.objects.create(
            order=order,
            book=self.book,
            title_snapshot=self.book.title,
            unit_price_snapshot=self.book.price,
            quantity=2,
            line_subtotal=Decimal("60000"),
        )
        self.book.title = "Título modificado"
        self.book.price = Decimal("1")
        self.book.save()
        item.refresh_from_db()
        self.assertEqual(item.title_snapshot, "Libro pedido")
        self.assertEqual(item.unit_price_snapshot, Decimal("30000"))

    def test_status_css_class_maps_statuses(self):
        order = Order(
            user=self.user,
            number="CMA-000001",
            payment_method=Order.PaymentMethod.PSE,
            shipping_line1="Calle",
            shipping_city="Bogotá",
            shipping_department="Cundinamarca",
            shipping_postal_code="110111",
            shipping_phone="3001234567",
            subtotal=Decimal("0"),
            shipping_cost=Decimal("8000"),
            total=Decimal("8000"),
            estimated_delivery="2026-06-12",
        )
        for status, expected in [
            (Order.Status.PENDING, "order-status--pending"),
            (Order.Status.CONFIRMED, "order-status--confirmed"),
            (Order.Status.SHIPPED, "order-status--shipped"),
            (Order.Status.DELIVERED, "order-status--delivered"),
            (Order.Status.CANCELLED, "order-status--cancelled"),
        ]:
            order.status = status
            self.assertEqual(order.status_css_class, expected)
