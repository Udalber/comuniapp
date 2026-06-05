from django.contrib import admin

from .models import Book, BookImage, Category


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ("image", "caption", "sort_order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "price", "condition", "created_at")
    list_filter = ("category", "condition")
    search_fields = ("title", "author", "isbn")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)
    inlines = [BookImageInline]
