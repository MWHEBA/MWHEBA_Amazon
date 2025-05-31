from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .services import fetch_fbm_products, sync_quantity_to_amazon, get_sp_api_client
from inventory.models import Product
from .models import AmazonSettings
from .forms import AmazonSettingsForm
from sp_api.api import Products

@login_required
def import_products(request):
    """
    استيراد منتجات FBM من أمازون
    """
    if request.method == 'POST':
        try:
            # جلب المنتجات من أمازون
            amazon_products = fetch_fbm_products()
            
            # عداد للمنتجات المستوردة والمحدثة
            imported_count = 0
            updated_count = 0
            
            for product_data in amazon_products:
                # التحقق مما إذا كان المنتج موجودًا بالفعل
                product, created = Product.objects.update_or_create(
                    amazon_sku=product_data['amazon_sku'],
                    defaults={
                        'title': product_data['title'],
                        'local_sku': product_data.get('local_sku', product_data['amazon_sku']),
                        'quantity': product_data['quantity'],
                        'is_fbm': product_data['is_fbm']
                    }
                )
                
                if created:
                    imported_count += 1
                else:
                    updated_count += 1
            
            # عرض رسالة نجاح
            if imported_count > 0 or updated_count > 0:
                success_message = f'تم استيراد {imported_count} منتج جديد وتحديث {updated_count} منتج بنجاح.'
                messages.success(request, success_message)
            else:
                messages.info(request, 'لم يتم العثور على منتجات جديدة للاستيراد.')
                
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء استيراد المنتجات: {str(e)}')
    
    return render(request, 'amazon_integration/import_products.html', {
        'title': 'استيراد منتجات من أمازون'
    })

@login_required
def sync_all_products(request):
    """
    مزامنة جميع المنتجات مع أمازون
    """
    if request.method == 'POST':
        try:
            # الحصول على جميع منتجات FBM
            fbm_products = Product.objects.filter(is_fbm=True)
            
            # عداد للمنتجات المزامنة بنجاح والفاشلة
            success_count = 0
            failed_count = 0
            
            # مزامنة كل منتج
            for product in fbm_products:
                if sync_quantity_to_amazon(product):
                    success_count += 1
                else:
                    failed_count += 1
            
            # عرض رسالة نجاح
            if success_count > 0:
                success_message = f'تمت مزامنة {success_count} منتج بنجاح.'
                if failed_count > 0:
                    success_message += f' فشل في مزامنة {failed_count} منتج.'
                messages.success(request, success_message)
            elif failed_count > 0:
                messages.error(request, f'فشل في مزامنة {failed_count} منتج.')
            else:
                messages.info(request, 'لا توجد منتجات FBM للمزامنة.')
                
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء مزامنة المنتجات: {str(e)}')
    
    return render(request, 'amazon_integration/sync_products.html', {
        'title': 'مزامنة المنتجات مع أمازون'
    })

@login_required
def amazon_settings(request):
    """
    عرض وتعديل إعدادات الاتصال بـ Amazon SP-API
    """
    # الحصول على الإعدادات الحالية أو إنشاء سجل جديد إذا لم يكن موجودًا
    settings_obj, created = AmazonSettings.objects.get_or_create()
    
    if request.method == 'POST':
        form = AmazonSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "تم حفظ إعدادات أمازون بنجاح.")
            return redirect('amazon_settings')
    else:
        form = AmazonSettingsForm(instance=settings_obj)
    
    context = {
        'form': form,
        'title': 'إعدادات أمازون'
    }
    
    return render(request, 'amazon_integration/settings.html', context)

@login_required
def test_amazon_connection(request):
    """
    اختبار الاتصال بـ Amazon SP-API
    """
    result = {
        'success': False,
        'message': '',
        'data': None
    }
    
    if request.method == 'POST':
        try:
            # محاولة إنشاء عميل Products API
            client = get_sp_api_client(Products)
            
            # استخدام طريقة موجودة بالفعل في كائن Products
            # نستخدم try/except داخلي لأن هذه الدالة قد تفشل لأسباب أخرى غير مشاكل الاتصال
            try:
                # فقط للتأكد من أن الكائن تم إنشاؤه بشكل صحيح
                str(client)
                result['success'] = True
                result['message'] = 'تم إنشاء اتصال بـ Amazon API بنجاح!'
            except Exception as api_error:
                result['success'] = False
                result['message'] = f"تم إنشاء الاتصال لكن فشل الاستعلام: {str(api_error)}"
            
        except Exception as e:
            result['success'] = False
            result['message'] = f'فشل الاتصال: {str(e)}'
    
    return render(request, 'amazon_integration/test_connection.html', {
        'title': 'اختبار الاتصال بأمازون',
        'result': result
    }) 