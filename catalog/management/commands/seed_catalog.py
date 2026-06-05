from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Book, Category


CATEGORIES = [
    {"name": "Académicos", "slug": "academicos"},
    {"name": "Ficción", "slug": "ficcion"},
    {"name": "No ficción", "slug": "no-ficcion"},
    {"name": "Infantil", "slug": "infantil"},
]

BOOKS = [
    {
        "title": "Cien años de soledad",
        "author": "Gabriel García Márquez",
        "editorial": "Sudamericana",
        "year": 1967,
        "isbn": "9788497592208",
        "price": Decimal("45000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "ficcion",
        "description": "La saga de la familia Buendía en el pueblo ficticio de Macondo.",
    },
    {
        "title": "El amor en los tiempos del cólera",
        "author": "Gabriel García Márquez",
        "editorial": "Oveja Negra",
        "year": 1985,
        "isbn": "9789580600147",
        "price": Decimal("38000"),
        "condition": Book.Condition.BUENO,
        "category_slug": "ficcion",
        "description": "Historia de amor entre Fermina Daza y Florentino Ariza.",
    },
    {
        "title": "La vorágine",
        "author": "José Eustasio Rivera",
        "editorial": "Ministerio de Educación",
        "year": 1924,
        "isbn": "9789584201234",
        "price": Decimal("28000"),
        "condition": Book.Condition.ACEPTABLE,
        "category_slug": "ficcion",
        "description": "Novela sobre la selva colombiana y la explotación del caucho.",
    },
    {
        "title": "Delirio",
        "author": "Laura Restrepo",
        "editorial": "Alfaguara",
        "year": 2004,
        "isbn": "9789587041234",
        "price": Decimal("32000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "ficcion",
        "description": "Una mujer busca entender la enfermedad mental de su esposo.",
    },
    {
        "title": "Sapiens: De animales a dioses",
        "author": "Yuval Noah Harari",
        "editorial": "Debate",
        "year": 2014,
        "isbn": "9788499926223",
        "price": Decimal("52000"),
        "condition": Book.Condition.NUEVO,
        "category_slug": "no-ficcion",
        "description": "Breve historia de la humanidad desde la evolución hasta la actualidad.",
    },
    {
        "title": "Hablar en público sin miedo",
        "author": "Dale Carnegie",
        "editorial": "Debolsillo",
        "year": 2010,
        "isbn": "9788499081234",
        "price": Decimal("22000"),
        "condition": Book.Condition.BUENO,
        "category_slug": "no-ficcion",
        "description": "Guía práctica para mejorar las habilidades de oratoria.",
    },
    {
        "title": "Breve historia del tiempo",
        "author": "Stephen Hawking",
        "editorial": "Crítica",
        "year": 1988,
        "isbn": "9788483061234",
        "price": Decimal("35000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "no-ficcion",
        "description": "Introducción accesible a la cosmología y la física moderna.",
    },
    {
        "title": "Cálculo diferencial e integral",
        "author": "Granville & Smith",
        "editorial": "Limusa",
        "year": 2001,
        "isbn": "9789681812345",
        "price": Decimal("65000"),
        "condition": Book.Condition.BUENO,
        "category_slug": "academicos",
        "description": "Texto clásico de cálculo para estudiantes universitarios.",
    },
    {
        "title": "Introducción al análisis de sistemas",
        "author": "Kendall & Kendall",
        "editorial": "Pearson",
        "year": 2011,
        "isbn": "9786073212345",
        "price": Decimal("78000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "academicos",
        "description": "Fundamentos de análisis y diseño de sistemas de información.",
    },
    {
        "title": "Diseño de proyectos de software",
        "author": "Roger Pressman",
        "editorial": "McGraw-Hill",
        "year": 2010,
        "isbn": "9786071501234",
        "price": Decimal("85000"),
        "condition": Book.Condition.NUEVO,
        "category_slug": "academicos",
        "description": "Ingeniería del software: metodologías y buenas prácticas.",
    },
    {
        "title": "El principito",
        "author": "Antoine de Saint-Exupéry",
        "editorial": "Salamandra",
        "year": 1943,
        "isbn": "9788498381234",
        "price": Decimal("18000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "infantil",
        "description": "Fábula poética sobre la amistad, el amor y la responsabilidad.",
    },
    {
        "title": "Matilda",
        "author": "Roald Dahl",
        "editorial": "Alfaguara Infantil",
        "year": 1988,
        "isbn": "9788420412345",
        "price": Decimal("24000"),
        "condition": Book.Condition.BUENO,
        "category_slug": "infantil",
        "description": "Una niña prodigio enfrenta a una directora de escuela tiránica.",
    },
    {
        "title": "Don Quijote de la Mancha",
        "author": "Miguel de Cervantes",
        "editorial": "Real Academia Española",
        "year": 1605,
        "isbn": "9788467031234",
        "price": Decimal("42000"),
        "condition": Book.Condition.ACEPTABLE,
        "category_slug": "ficcion",
        "description": "Las aventuras del ingenioso hidalgo y su fiel escudero Sancho Panza.",
    },
    {
        "title": "Rayuela",
        "author": "Julio Cortázar",
        "editorial": "Alfaguara",
        "year": 1963,
        "isbn": "9789870401234",
        "price": Decimal("36000"),
        "condition": Book.Condition.BUENO,
        "category_slug": "ficcion",
        "description": "Novela experimental que puede leerse en múltiples órdenes.",
    },
    {
        "title": "El olvido que seremos",
        "author": "Héctor Abad Faciolince",
        "editorial": "Alfaguara",
        "year": 2006,
        "isbn": "9789587045678",
        "price": Decimal("30000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "no-ficcion",
        "description": "Memoria del asesinato del padre del autor en la Colombia de los 80.",
    },
    {
        "title": "Álgebra lineal y sus aplicaciones",
        "author": "David C. Lay",
        "editorial": "Pearson",
        "year": 2016,
        "isbn": "9780321982384",
        "price": Decimal("92000"),
        "condition": Book.Condition.NUEVO,
        "category_slug": "academicos",
        "description": "Texto universitario de álgebra lineal con aplicaciones prácticas.",
    },
    {
        "title": "El monstruo de colores",
        "author": "Anna Llenas",
        "editorial": "Tundra",
        "year": 2012,
        "isbn": "9788494431234",
        "price": Decimal("26000"),
        "condition": Book.Condition.NUEVO,
        "category_slug": "infantil",
        "description": "Cuento ilustrado para ayudar a los niños a entender sus emociones.",
    },
    {
        "title": "Historia mínima de Colombia",
        "author": "Jorge Orlando Melo",
        "editorial": "Planeta",
        "year": 2018,
        "isbn": "9789584234567",
        "price": Decimal("48000"),
        "condition": Book.Condition.COMO_NUEVO,
        "category_slug": "academicos",
        "description": "Síntesis accesible de la historia política y social de Colombia.",
    },
]


class Command(BaseCommand):
    help = "Carga categorías y libros de demostración (idempotente)."

    def handle(self, *args, **options):
        categories_created = 0
        for cat_data in CATEGORIES:
            _, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={"name": cat_data["name"]},
            )
            if created:
                categories_created += 1

        books_created = 0
        for book_data in BOOKS:
            category = Category.objects.get(slug=book_data.pop("category_slug"))
            lookup = {
                "title": book_data["title"],
                "author": book_data["author"],
            }
            _, created = Book.objects.get_or_create(
                **lookup,
                defaults={**book_data, "category": category},
            )
            if created:
                books_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completado: {categories_created} categorías nuevas, "
                f"{books_created} libros nuevos "
                f"(total: {Category.objects.count()} categorías, "
                f"{Book.objects.count()} libros)."
            )
        )
