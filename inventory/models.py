from django.db import models
from django.core.validators import MinValueValidator

class ProductCategory(models.Model):
    """
    نموذج فئة المنتج
    """
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الفئة")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "فئة منتج"
        verbose_name_plural = "فئات المنتجات"
        ordering = ['name']

class ProductUnit(models.Model):
    """
    نموذج وحدة المنتج
    """
    name = models.CharField(max_length=50, verbose_name="اسم الوحدة")
    abbreviation = models.CharField(max_length=10, verbose_name="اختصار الوحدة")

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

    class Meta:
        verbose_name = "وحدة منتج"
        verbose_name_plural = "وحدات المنتجات"

class Product(models.Model):
    """
    نموذج المنتج الذي يحتفظ بمعلومات المنتج الأساسية
    """
    title = models.CharField(max_length=255, verbose_name="عنوان المنتج")
    local_sku = models.CharField(max_length=100, verbose_name="رمز المنتج المحلي", unique=True)
    amazon_sku = models.CharField(max_length=100, verbose_name="رمز المنتج على أمازون", blank=True, null=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="الكمية")
    is_fbm = models.BooleanField(default=False, verbose_name="FBM")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="الفئة")
    unit = models.ForeignKey(ProductUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="وحدة القياس")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    def __str__(self):
        return f"{self.title} ({self.local_sku})"

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "منتجات"
        ordering = ['title']


class StockMovement(models.Model):
    """
    نموذج حركة المخزون لتتبع المبيعات وإعادة التخزين
    """
    MOVEMENT_TYPES = (
        ('SALE', 'بيع'),
        ('RESTOCK', 'إعادة تخزين'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements', verbose_name="المنتج")
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name="نوع الحركة")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت العملية")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.title} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        """
        تحديث كمية المنتج عند إضافة حركة مخزون جديدة
        """
        if self.pk is None:  # فقط للسجلات الجديدة
            product = self.product
            if self.movement_type == 'SALE':
                product.quantity = max(0, product.quantity - self.quantity)
            elif self.movement_type == 'RESTOCK':
                product.quantity += self.quantity
            product.save()
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "حركة مخزون"
        verbose_name_plural = "حركات المخزون"
        ordering = ['-timestamp'] 