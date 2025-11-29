from django.contrib import admin
from .models import Category, Warehouse, Product, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location']
    search_fields = ['name', 'location']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'quantity', 'price', 'is_low_stock']
    list_filter = ['category', 'warehouse']
    search_fields = ['sku', 'name']
    list_per_page = 20

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'date', 'user']
    list_filter = ['transaction_type', 'date']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['date']
