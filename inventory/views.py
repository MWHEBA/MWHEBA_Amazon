from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, StockMovement
from amazon_integration.services import sync_quantity_to_amazon
from .forms import ProductForm, StockMovementForm
import json

@login_required
def dashboard(request):
    """
    عرض لوحة التحكم الرئيسية مع قائمة المنتجات
    """
    products = Product.objects.all()
    products_fbm_count = Product.objects.filter(is_fbm=True).count()
    products_low_stock_count = Product.objects.filter(quantity__lte=5, quantity__gt=0).count()
    products_out_of_stock_count = Product.objects.filter(quantity=0).count()
    
    return render(request, 'inventory/dashboard.html', {
        'products': products,
        'products_fbm_count': products_fbm_count,
        'products_low_stock_count': products_low_stock_count,
        'products_out_of_stock_count': products_out_of_stock_count,
        'title': 'لوحة التحكم'
    })

@login_required
def product_list(request):
    """
    عرض قائمة المنتجات
    """
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {
        'products': products,
        'title': 'قائمة المنتجات'
    })

@login_required
def product_detail(request, pk):
    """
    عرض تفاصيل منتج محدد
    """
    product = get_object_or_404(Product, pk=pk)
    stock_movements = product.stock_movements.all()[:10]  # آخر 10 حركات فقط
    
    # نموذج إضافة حركة مخزون جديدة
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.product = product
            movement.save()
            
            # مزامنة الكمية مع أمازون إذا كانت حركة بيع
            if movement.movement_type == 'SALE':
                sync_result = sync_quantity_to_amazon(product)
                if sync_result:
                    messages.success(request, 'تم تسجيل الحركة ومزامنة الكمية مع أمازون بنجاح.')
                else:
                    messages.warning(request, 'تم تسجيل الحركة ولكن فشلت مزامنة الكمية مع أمازون.')
            else:
                messages.success(request, 'تم تسجيل حركة المخزون بنجاح.')
                
            return redirect('product_detail', pk=product.pk)
    else:
        form = StockMovementForm(initial={'product': product})
    
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'stock_movements': stock_movements,
        'form': form,
        'title': f'تفاصيل المنتج: {product.title}'
    })

@login_required
def add_product(request):
    """
    إضافة منتج جديد
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'تم إضافة المنتج "{product.title}" بنجاح.')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'title': 'إضافة منتج جديد'
    })

@login_required
def edit_product(request, pk):
    """
    تعديل منتج موجود
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'تم تحديث المنتج "{product.title}" بنجاح.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'product': product,
        'title': f'تعديل المنتج: {product.title}'
    })

@login_required
def record_sale(request):
    """
    تسجيل عملية بيع (AJAX)
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        try:
            product = Product.objects.get(pk=product_id)
            
            # إنشاء حركة بيع جديدة
            movement = StockMovement(
                product=product,
                movement_type='SALE',
                quantity=quantity
            )
            movement.save()
            
            # مزامنة الكمية مع أمازون
            sync_result = sync_quantity_to_amazon(product)
            
            return JsonResponse({
                'success': True,
                'new_quantity': product.quantity,
                'sync_success': sync_result
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'المنتج غير موجود'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'طلب غير صالح'}, status=400)

@login_required
def sync_product(request, pk):
    """
    مزامنة كمية منتج محدد مع أمازون
    """
    product = get_object_or_404(Product, pk=pk)
    
    # مزامنة الكمية مع أمازون
    sync_result = sync_quantity_to_amazon(product)
    
    if sync_result:
        messages.success(request, f'تمت مزامنة كمية المنتج "{product.title}" مع أمازون بنجاح.')
    else:
        messages.error(request, f'فشلت مزامنة كمية المنتج "{product.title}" مع أمازون.')
    
    return redirect('product_detail', pk=product.pk) 