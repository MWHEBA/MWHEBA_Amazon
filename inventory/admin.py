from django.contrib import admin
from .models import Product, StockMovement, ProductCategory, ProductUnit

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """
    إدارة نموذج فئة المنتج في لوحة الإدارة
    """
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    """
    إدارة نموذج وحدة المنتج في لوحة الإدارة
    """
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    إدارة نموذج المنتج في لوحة الإدارة
    """
    list_display = ('title', 'local_sku', 'amazon_sku', 'quantity', 'is_fbm', 'category', 'unit', 'updated_at')
    list_filter = ('is_fbm', 'category', 'updated_at')
    search_fields = ('title', 'local_sku', 'amazon_sku')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('معلومات المنتج الأساسية', {
            'fields': ('title', 'local_sku', 'amazon_sku', 'category', 'unit')
        }),
        ('معلومات المخزون', {
            'fields': ('quantity', 'is_fbm')
        }),
        ('معلومات الوقت', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class StockMovementInline(admin.TabularInline):
    """
    عرض حركات المخزون المرتبطة بالمنتج
    """
    model = StockMovement
    extra = 0
    readonly_fields = ('timestamp',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """
    إدارة نموذج حركة المخزون في لوحة الإدارة
    """
    list_display = ('product', 'movement_type', 'quantity', 'timestamp')
    list_filter = ('movement_type', 'timestamp')
    search_fields = ('product__title', 'product__local_sku', 'product__amazon_sku', 'notes')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('معلومات الحركة', {
            'fields': ('product', 'movement_type', 'quantity')
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'timestamp')
        }),
    ) 