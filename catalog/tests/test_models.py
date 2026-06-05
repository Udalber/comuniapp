from decimal import Decimal

from django.test import TestCase

from catalog.models import Book, Category


class BookModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Ficción", slug="ficcion")

    def test_gallery_returns_at_least_three_without_images(self):
        book = Book.objects.create(
            title="Sin imágenes",
            author="Autor Test",
            price=Decimal("10000"),
            condition=Book.Condition.BUENO,
            category=self.category,
            slug="sin-imagenes",
        )
        gallery = book.gallery()
        self.assertGreaterEqual(len(gallery), 3)
        self.assertTrue(any(item["caption"] == "Portada" for item in gallery))
        self.assertTrue(any(item["caption"] == "Lomo" for item in gallery))
        self.assertTrue(any(item["caption"] == "Interior" for item in gallery))

    def test_get_condition_display_class_maps_four_states(self):
        mapping = {
            Book.Condition.NUEVO: "book-card__badge--success",
            Book.Condition.COMO_NUEVO: "book-card__badge--light",
            Book.Condition.BUENO: "book-card__badge--caution",
            Book.Condition.ACEPTABLE: "book-card__badge--warning",
        }
        for condition, expected_class in mapping.items():
            book = Book(
                title=f"Libro {condition}",
                author="Autor",
                price=Decimal("10000"),
                condition=condition,
                category=self.category,
                slug=f"libro-{condition}",
            )
            self.assertEqual(book.get_condition_display_class(), expected_class)
