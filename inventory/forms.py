from django import forms
from .models import Product, StockMovement

class ProductForm(forms.ModelForm):
    """
    نموذج إضافة وتعديل المنتج
    """
    class Meta:
        model = Product
        fields = ['title', 'local_sku', 'amazon_sku', 'quantity', 'is_fbm']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان المنتج'}),
            'local_sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رمز المنتج المحلي'}),
            'amazon_sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رمز المنتج على أمازون'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_fbm': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StockMovementForm(forms.ModelForm):
    """
    نموذج إضافة حركة مخزون
    """
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'notes']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'ملاحظات إضافية (اختياري)'}),
        } 