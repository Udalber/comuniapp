from django.shortcuts import render


def home(request):
    """Landing / Home — hero, buscador y categorías placeholder."""
    categories = [
        {"name": "Académicos", "slug": "academicos"},
        {"name": "Ficción", "slug": "ficcion"},
        {"name": "No ficción", "slug": "no-ficcion"},
        {"name": "Infantil", "slug": "infantil"},
        {"name": "Arte y diseño", "slug": "arte-diseno"},
        {"name": "Ciencia", "slug": "ciencia"},
    ]
    return render(
        request,
        "core/home.html",
        {"categories": categories},
    )
