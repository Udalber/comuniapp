from django.contrib import admin

from .models import Address, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "book",
        "title_snapshot",
        "unit_price_snapshot",
        "quantity",
        "line_subtotal",
    )
    can_delete = False


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "line1", "city", "department", "is_default", "is_saved")
    list_filter = ("is_default", "is_saved")
    search_fields = ("line1", "city", "user__email")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user",
        "status",
        "payment_method",
        "total",
        "created_at",
        "estimated_delivery",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("number", "user__email", "shipping_line1")
    readonly_fields = ("number", "created_at")
    inlines = [OrderItemInline]
