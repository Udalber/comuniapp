from decimal import Decimal

from catalog.models import Book

CART_SESSION_KEY = "cart"


class Cart:
    """Carrito basado en sesión: { "<book_id>": cantidad }."""

    def __init__(self, session):
        self.session = session
        cart = session.get(CART_SESSION_KEY)
        if cart is None:
            cart = session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, book, qty=1, override=False):
        """Añade un libro. Retorna True si se añadió, False si ya estaba."""
        book_id = str(book.pk)
        if book_id in self.cart and not override:
            return False
        if override:
            self.cart[book_id] = qty
        else:
            self.cart[book_id] = self.cart.get(book_id, 0) + qty
        self._save()
        return True

    def remove(self, book):
        book_id = str(book.pk)
        if book_id in self.cart:
            del self.cart[book_id]
            self._save()

    def update(self, book, qty):
        book_id = str(book.pk)
        qty = int(qty)
        if qty <= 0:
            self.remove(book)
        elif book_id in self.cart:
            self.cart[book_id] = qty
            self._save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self._save()

    def contains(self, book):
        return str(book.pk) in self.cart

    def __contains__(self, book):
        if hasattr(book, "pk"):
            return str(book.pk) in self.cart
        return str(book) in self.cart

    def get_quantity(self, book):
        return self.cart.get(str(book.pk), 0)

    def __iter__(self):
        book_ids = []
        for book_id in self.cart:
            try:
                book_ids.append(int(book_id))
            except (TypeError, ValueError):
                continue

        books = Book.objects.filter(pk__in=book_ids).select_related("category")
        book_map = {str(book.pk): book for book in books}

        stale_ids = []
        for book_id, quantity in self.cart.items():
            book = book_map.get(book_id)
            if book is None:
                stale_ids.append(book_id)
                continue
            unit_price = book.price
            yield {
                "book": book,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_subtotal": unit_price * quantity,
            }

        if stale_ids:
            for book_id in stale_ids:
                self.cart.pop(book_id, None)
            self._save()

    def __len__(self):
        return sum(self.cart.values())

    @property
    def total_price(self):
        return sum((item["line_subtotal"] for item in self), Decimal("0"))

    def line_subtotal(self, book):
        qty = self.get_quantity(book)
        if qty <= 0:
            return Decimal("0")
        return book.price * qty

    def _save(self):
        self.session.modified = True
