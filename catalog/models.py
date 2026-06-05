from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("nombre", max_length=100)
    slug = models.SlugField("slug", max_length=120, unique=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(models.Model):
    class Condition(models.TextChoices):
        NUEVO = "nuevo", "Nuevo"
        COMO_NUEVO = "como_nuevo", "Como nuevo"
        BUENO = "bueno", "Bueno"
        ACEPTABLE = "aceptable", "Aceptable"

    title = models.CharField("título", max_length=255)
    author = models.CharField("autor", max_length=255)
    editorial = models.CharField("editorial", max_length=255, blank=True)
    year = models.PositiveIntegerField("año", null=True, blank=True)
    isbn = models.CharField("ISBN", max_length=20, blank=True)
    price = models.DecimalField("precio (COP)", max_digits=10, decimal_places=0)
    condition = models.CharField(
        "estado",
        max_length=20,
        choices=Condition.choices,
        default=Condition.BUENO,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="categoría",
    )
    description = models.TextField("descripción", blank=True)
    cover_image = models.ImageField(
        "portada",
        upload_to="covers/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("fecha de publicación", auto_now_add=True)
    slug = models.SlugField("slug", max_length=280, unique=True)

    class Meta:
        verbose_name = "libro"
        verbose_name_plural = "libros"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.author}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.title}-{self.author}")[:250]
            slug = base
            counter = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def cover_or_placeholder(self):
        """URL de portada o None para mostrar placeholder visual en plantilla."""
        if self.cover_image:
            return self.cover_image.url
        return None

    def get_absolute_url(self):
        return reverse("catalog:detail", kwargs={"slug": self.slug})

    def get_condition_display_class(self):
        """Clase CSS del badge según estado del libro (compartida tarjeta + detalle)."""
        mapping = {
            self.Condition.NUEVO: "book-card__badge--success",
            self.Condition.COMO_NUEVO: "book-card__badge--light",
            self.Condition.BUENO: "book-card__badge--caution",
            self.Condition.ACEPTABLE: "book-card__badge--warning",
        }
        return mapping.get(self.condition, "book-card__badge--neutral")

    def gallery(self):
        """
        Imágenes de galería reales o fallback de 3 elementos (portada, lomo, interior).
        Cada ítem: url (str|None), caption (str), is_placeholder (bool).
        """
        images = list(self.images.order_by("sort_order", "pk"))
        if images:
            return [
                {
                    "url": img.image.url,
                    "caption": img.caption or f"Imagen {idx + 1}",
                    "is_placeholder": False,
                }
                for idx, img in enumerate(images)
            ]
        return [
            {
                "url": self.cover_or_placeholder,
                "caption": "Portada",
                "is_placeholder": self.cover_or_placeholder is None,
            },
            {
                "url": None,
                "caption": "Lomo",
                "is_placeholder": True,
            },
            {
                "url": None,
                "caption": "Interior",
                "is_placeholder": True,
            },
        ]


class BookImage(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="libro",
    )
    image = models.ImageField("imagen", upload_to="books/gallery/")
    caption = models.CharField("leyenda", max_length=100, blank=True)
    sort_order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        verbose_name = "imagen del libro"
        verbose_name_plural = "imágenes del libro"
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.caption or f"Imagen {self.pk}"
