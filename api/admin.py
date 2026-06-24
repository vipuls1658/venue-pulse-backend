from django.contrib import admin

from .models import Product, Staff, Transaction, TransactionItem, Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("venue_code", "venue_name", "venue_type", "city")
    list_filter = ("venue_type",)
    search_fields = ("venue_code", "venue_name")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("staff_code", "staff_name", "venue")
    list_filter = ("venue",)
    search_fields = ("staff_code", "staff_name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_code", "product_name", "current_price")
    search_fields = ("product_code", "product_name")


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_number",
        "venue",
        "transaction_type",
        "total_amount",
        "staff",
        "transaction_time",
    )
    list_filter = ("transaction_type", "venue")
    search_fields = ("transaction_number",)
    date_hierarchy = "transaction_time"
    inlines = [TransactionItemInline]
