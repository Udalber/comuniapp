import random
import string
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    line1 = models.CharField("Dirección", max_length=255)
    city = models.CharField("Ciudad", max_length=100)
    department = models.CharField("Departamento", max_length=100)
    postal_code = models.CharField("Código postal", max_length=20)
    phone = models.CharField("Teléfono de contacto", max_length=30)
    instructions = models.TextField("Instrucciones adicionales", blank=True)
    is_saved = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    def __str__(self):
        return f"{self.line1}, {self.city}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CONFIRMED = "confirmed", "Confirmado"
        SHIPPED = "shipped", "Enviado"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Cancelado"

    class PaymentMethod(models.TextChoices):
        PSE = "pse", "PSE"
        NEQUI = "nequi", "Nequi"
        DAVIPLATA = "daviplata", "Daviplata"
        CARD = "card", "Tarjeta crédito/débito"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    number = models.CharField("Número de pedido", max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)

    shipping_line1 = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=100)
    shipping_department = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_phone = models.CharField(max_length=30)
    shipping_instructions = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.DateField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return self.number

    @classmethod
    def generate_number(cls):
        while True:
            suffix = "".join(random.choices(string.digits, k=6))
            number = f"CMA-{suffix}"
            if not cls.objects.filter(number=number).exists():
                return number

    @property
    def payment_method_display(self):
        return self.get_payment_method_display()

    @property
    def shipping_summary(self):
        parts = [
            self.shipping_line1,
            self.shipping_city,
            self.shipping_department,
            self.shipping_postal_code,
        ]
        return ", ".join(parts)

    @property
    def status_css_class(self):
        return {
            self.Status.PENDING: "order-status--pending",
            self.Status.CONFIRMED: "order-status--confirmed",
            self.Status.SHIPPED: "order-status--shipped",
            self.Status.DELIVERED: "order-status--delivered",
            self.Status.CANCELLED: "order-status--cancelled",
        }.get(self.status, "order-status--pending")


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    book = models.ForeignKey(
        "catalog.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title_snapshot = models.CharField(max_length=255)
    unit_price_snapshot = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        verbose_name = "Ítem del pedido"
        verbose_name_plural = "Ítems del pedido"

    def __str__(self):
        return f"{self.title_snapshot} x{self.quantity}"


def default_estimated_delivery():
    return (timezone.now() + timedelta(days=7)).date()
