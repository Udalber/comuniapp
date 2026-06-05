from django.db.models import Count
from django.shortcuts import render

from catalog.models import Category


def home(request):
    """Landing / Home — hero, buscador y categorías desde BD."""
    categories = (
        Category.objects.annotate(book_count=Count("books"))
        .filter(book_count__gt=0)
        .order_by("name")
    )
    return render(
        request,
        "core/home.html",
        {"categories": categories},
    )
