from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Book, Category

BOOKS_PER_PAGE = 12


def _parse_decimal(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def _filter_books(request):
    """Aplica búsqueda y filtros GET sobre el queryset de libros."""
    qs = Book.objects.select_related("category").all()
    q = request.GET.get("q", "").strip()

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))

    category_slugs = request.GET.getlist("category")
    if category_slugs:
        qs = qs.filter(category__slug__in=category_slugs)

    conditions = request.GET.getlist("condition")
    if conditions:
        valid = {c for c, _ in Book.Condition.choices}
        qs = qs.filter(condition__in=[c for c in conditions if c in valid])

    price_min = _parse_decimal(request.GET.get("price_min"))
    price_max = _parse_decimal(request.GET.get("price_max"))
    if price_min is not None:
        qs = qs.filter(price__gte=price_min)
    if price_max is not None:
        qs = qs.filter(price__lte=price_max)

    sort = request.GET.get("sort", "")
    if sort == "price":
        qs = qs.order_by("price")
    elif sort == "date":
        qs = qs.order_by("-created_at")
    elif sort == "relevance" and q:
        qs = qs.order_by("title")
    else:
        qs = qs.order_by("-created_at")

    return qs, q


def index(request):
    """Catálogo: grid de libros con búsqueda, filtros y paginación."""
    books_qs, q = _filter_books(request)
    total_count = books_qs.count()

    paginator = Paginator(books_qs, BOOKS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    condition_choices = Book.Condition.choices

    selected_categories = request.GET.getlist("category")
    selected_conditions = request.GET.getlist("condition")
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    sort = request.GET.get("sort", "relevance" if q else "date")

    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]
    pagination_query = query_params.urlencode()

    context = {
        "page_obj": page_obj,
        "books": page_obj.object_list,
        "total_count": total_count,
        "q": q,
        "categories": categories,
        "condition_choices": condition_choices,
        "selected_categories": selected_categories,
        "selected_conditions": selected_conditions,
        "price_min": price_min,
        "price_max": price_max,
        "sort": sort,
        "pagination_query": pagination_query,
        "has_filters": bool(
            selected_categories
            or selected_conditions
            or price_min
            or price_max
            or (sort and sort != ("relevance" if q else "date"))
        ),
    }
    return render(request, "catalog/index.html", context)


def suggest(request):
    """Autocompletado JSON para búsqueda (3+ caracteres)."""
    q = request.GET.get("q", "").strip()
    if len(q) < 3:
        return JsonResponse({"results": []})

    books = (
        Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q))
        .order_by("title")[:8]
    )
    results = [
        {
            "title": book.title,
            "author": book.author,
            "url": book.get_absolute_url(),
        }
        for book in books
    ]
    return JsonResponse({"results": results})


def detail(request, slug):
    """Detalle completo del libro: galería, metadatos y gancho carrito (sesión cart)."""
    book = get_object_or_404(
        Book.objects.select_related("category").prefetch_related("images"),
        slug=slug,
    )
    related_books = (
        Book.objects.filter(category=book.category)
        .exclude(pk=book.pk)
        .select_related("category")[:4]
    )
    context = {
        "book": book,
        "gallery": book.gallery(),
        "related_books": related_books,
    }
    return render(request, "catalog/detail.html", context)
