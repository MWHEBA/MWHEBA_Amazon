import os
import logging
import requests
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .services import fetch_fbm_products, sync_quantity_to_amazon, get_sp_api_client
from inventory.models import Product
from .models import AmazonSettings, AppSettings
from .forms import AmazonSettingsForm, AppSettingsForm
from sp_api.api import Products

logger = logging.getLogger(__name__)

@login_required
def app_settings(request):
    """
    عرض وتعديل إعدادات التطبيق الثابتة
    """
    # محاولة الحصول على الإعدادات الحالية
    app_settings = AppSettings.objects.filter(is_active=True).first()
    
    if request.method == 'POST':
        # تعديل الإعدادات الحالية أو إنشاء إعدادات جديدة
        if app_settings:
            form = AppSettingsForm(request.POST, instance=app_settings)
        else:
            form = AppSettingsForm(request.POST)
        
        if form.is_valid():
            # حفظ الإعدادات
            app_settings = form.save()
            
            # تحديث متغيرات البيئة في ذاكرة التطبيق الحالي
            os.environ['AWS_ACCESS_KEY'] = app_settings.aws_access_key
            os.environ['AWS_SECRET_KEY'] = app_settings.aws_secret_key
            os.environ['ROLE_ARN'] = app_settings.role_arn
            os.environ['LWA_CLIENT_ID'] = app_settings.lwa_client_id
            os.environ['LWA_CLIENT_SECRET'] = app_settings.lwa_client_secret
            
            # تحديث إعدادات جانجو
            settings.AWS_ACCESS_KEY = app_settings.aws_access_key
            settings.AWS_SECRET_KEY = app_settings.aws_secret_key
            settings.ROLE_ARN = app_settings.role_arn
            settings.LWA_CLIENT_ID = app_settings.lwa_client_id
            settings.LWA_CLIENT_SECRET = app_settings.lwa_client_secret
            
            messages.success(request, "تم حفظ إعدادات التطبيق بنجاح.")
            return redirect('app_settings')
    else:
        # عرض نموذج جديد أو النموذج الحالي
        if app_settings:
            form = AppSettingsForm(instance=app_settings)
        else:
            form = AppSettingsForm()
    
    context = {
        'form': form,
        'app_settings': app_settings,
        'title': 'إعدادات التطبيق الثابتة'
    }
    
    return render(request, 'amazon_integration/app_settings.html', context)

@login_required
def auth_callback(request):
    """
    معالجة استجابة Amazon OAuth بعد تسجيل الدخول
    """
    try:
        # الحصول على رمز التفويض من العنوان
        auth_code = request.GET.get('spapi_oauth_code')
        
        if not auth_code:
            messages.error(request, "لم يتم استلام رمز التفويض من أمازون.")
            return redirect('amazon_settings')
        
        # تبادل رمز التفويض بـ refresh token
        refresh_token = exchange_auth_code_for_refresh_token(auth_code)
        
        if not refresh_token:
            messages.error(request, "فشل في تبادل رمز التفويض بـ refresh token.")
            return redirect('amazon_settings')
        
        # الحصول على الإعدادات الحالية أو إنشاء إعدادات جديدة
        try:
            amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
            if amazon_settings:
                # تحديث refresh_token فقط
                amazon_settings.refresh_token = refresh_token
                amazon_settings.save()
                messages.success(request, "تم تحديث رمز التفويض بنجاح.")
            else:
                # إنشاء إعدادات جديدة
                amazon_settings = AmazonSettings(
                    refresh_token=refresh_token,
                    is_active=True
                )
                amazon_settings.save()
                messages.success(request, "تم إنشاء إعدادات جديدة بنجاح.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حفظ رمز التفويض: {str(e)}")
        
        return redirect('amazon_settings')
        
    except Exception as e:
        logger.error(f"خطأ في معالجة استجابة OAuth: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء معالجة استجابة أمازون: {str(e)}")
        return redirect('amazon_settings')

def exchange_auth_code_for_refresh_token(auth_code):
    """
    تبادل رمز التفويض بـ refresh token من Amazon
    
    Args:
        auth_code: رمز التفويض المستلم من عملية OAuth
    
    Returns:
        refresh_token: رمز التحديث أو None في حالة الفشل
    """
    try:
        # استخدام بيانات التطبيق من ملف .env
        lwa_client_id = settings.LWA_CLIENT_ID
        lwa_client_secret = settings.LWA_CLIENT_SECRET
        
        # عنوان طلب تبديل الرمز
        token_url = "https://api.amazon.com/auth/o2/token"
        
        # بيانات الطلب
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": lwa_client_id,
            "client_secret": lwa_client_secret
        }
        
        # إرسال الطلب
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            # استخراج refresh_token من الاستجابة
            response_data = response.json()
            refresh_token = response_data.get("refresh_token")
            
            if refresh_token:
                logger.info("تم الحصول على refresh token بنجاح")
                return refresh_token
            else:
                logger.error("لم يتم العثور على refresh token في الاستجابة")
                return None
        else:
            logger.error(f"فشل طلب الحصول على refresh token، رمز الاستجابة: {response.status_code}")
            logger.error(f"تفاصيل الخطأ: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"خطأ أثناء تبادل رمز التفويض: {str(e)}")
        return None

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
    
    # التحقق من وجود إعدادات نشطة
    has_active_settings = AmazonSettings.objects.filter(is_active=True).exists()
    
    return render(request, 'amazon_integration/import_products.html', {
        'title': 'استيراد منتجات من أمازون',
        'has_active_settings': has_active_settings
    })

# دالة لتنفيذ المزامنة في خلفية النظام
def background_sync(fbm_products):
    """
    مزامنة المنتجات في خلفية النظام
    """
    results = {'success': 0, 'failed': 0}
    for product in fbm_products:
        if sync_quantity_to_amazon(product):
            results['success'] += 1
        else:
            results['failed'] += 1
    logger.info(f"اكتملت مزامنة المنتجات. نجاح: {results['success']}, فشل: {results['failed']}")
    return results

@login_required
def sync_all_products(request):
    """
    مزامنة جميع المنتجات مع أمازون
    """
    # التحقق من وجود إعدادات نشطة
    has_active_settings = AmazonSettings.objects.filter(is_active=True).exists()
    amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
    
    if not has_active_settings:
        messages.error(request, "الرجاء إعداد معلومات الاتصال بأمازون أولاً.")
        return render(request, 'amazon_integration/sync_products.html', {
            'title': 'مزامنة المنتجات مع أمازون',
            'has_active_settings': has_active_settings
        })
    
    # التحقق من وجود رقم موقع FBM
    if not amazon_settings.location_id:
        messages.error(request, "الرجاء إضافة رقم موقع FBM في إعدادات أمازون أولاً.")
        return render(request, 'amazon_integration/sync_products.html', {
            'title': 'مزامنة المنتجات مع أمازون',
            'has_active_settings': True,
            'has_location_id': False
        })
    
    if request.method == 'POST':
        # الحصول على جميع منتجات FBM
        fbm_products = Product.objects.filter(is_fbm=True)
        
        if not fbm_products.exists():
            messages.info(request, 'لا توجد منتجات FBM للمزامنة.')
        else:
            # بدء عملية المزامنة في خلفية النظام
            sync_thread = threading.Thread(target=background_sync, args=(fbm_products,))
            sync_thread.daemon = True
            sync_thread.start()
            
            messages.success(request, f'بدأت عملية مزامنة {fbm_products.count()} منتج في الخلفية.')
    
    # عدد منتجات FBM
    fbm_products_count = Product.objects.filter(is_fbm=True).count()
    
    return render(request, 'amazon_integration/sync_products.html', {
        'title': 'مزامنة المنتجات مع أمازون',
        'has_active_settings': True,
        'has_location_id': amazon_settings.location_id is not None,
        'fbm_products_count': fbm_products_count
    })

# دالة جديدة للحصول على حالة عملية المزامنة (يمكن استخدامها مع AJAX)
@login_required
def sync_status(request):
    """
    الحصول على حالة عملية المزامنة
    """
    # في التطبيق الحقيقي، يمكنك استخدام نظام مهام مثل Celery للحصول على حالة المهمة
    return JsonResponse({
        'status': 'running',
        'message': 'جاري تنفيذ المزامنة...'
    })

@login_required
def amazon_settings(request):
    """
    عرض وتعديل إعدادات الاتصال بـ Amazon SP-API
    """
    # محاولة الحصول على الإعدادات الحالية
    amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
    
    # الحصول على إعدادات التطبيق للحصول على LWA_CLIENT_ID
    app_settings = AppSettings.objects.filter(is_active=True).first()
    lwa_client_id = app_settings.lwa_client_id if app_settings else settings.LWA_CLIENT_ID
    
    if request.method == 'POST':
        # تعديل الإعدادات الحالية أو إنشاء إعدادات جديدة
        if amazon_settings:
            form = AmazonSettingsForm(request.POST, instance=amazon_settings)
        else:
            form = AmazonSettingsForm(request.POST)
        
        if form.is_valid():
            # إذا كان هناك إعدادات نشطة أخرى، نجعلها غير نشطة
            if not amazon_settings and form.cleaned_data.get('is_active'):
                AmazonSettings.objects.filter(is_active=True).update(is_active=False)
            
            amazon_settings = form.save()
            messages.success(request, "تم حفظ إعدادات أمازون بنجاح.")
            return redirect('amazon_settings')
    else:
        # عرض نموذج جديد أو النموذج الحالي
        if amazon_settings:
            form = AmazonSettingsForm(instance=amazon_settings)
        else:
            form = AmazonSettingsForm()
    
    context = {
        'form': form,
        'amazon_settings': amazon_settings,
        'title': 'إعدادات الاتصال بـ Amazon SP-API',
        'settings': settings,  # إعدادات Django
        'lwa_client_id': lwa_client_id  # إضافة client_id من قاعدة البيانات
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
        'data': None,
        'debug_info': None,
        'field_errors': [],
        'status_details': {
            'amazon_settings': {'status': 'error', 'msg': 'لم يتم العثور على إعدادات أمازون.'},
            'app_settings': {'status': 'error', 'msg': 'لم يتم العثور على إعدادات التطبيق.'},
            'settings_complete': {'status': 'error', 'msg': 'الإعدادات غير مكتملة.'},
            'aws_keys_verified': {'status': 'error', 'msg': 'لم يتم التحقق من مفاتيح AWS.'},
            'lwa_keys_verified': {'status': 'error', 'msg': 'لم يتم التحقق من مفاتيح LWA.'}
        }
    }
    
    if request.method == 'POST':
        try:
            amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
            app_settings = AppSettings.objects.filter(is_active=True).first()
            
            # حالة إعدادات أمازون
            if amazon_settings:
                result['status_details']['amazon_settings'] = {'status': 'success', 'msg': 'إعدادات أمازون موجودة.'}
            else:
                result['status_details']['amazon_settings'] = {'status': 'error', 'msg': 'لم يتم العثور على إعدادات أمازون.'}
            
            # حالة إعدادات التطبيق
            if app_settings:
                result['status_details']['app_settings'] = {'status': 'success', 'msg': 'إعدادات التطبيق موجودة.'}
            else:
                result['status_details']['app_settings'] = {'status': 'error', 'msg': 'لم يتم العثور على إعدادات التطبيق.'}
            
            # التحقق من اكتمال البيانات
            missing_fields = []
            if not amazon_settings or not amazon_settings.refresh_token:
                missing_fields.append("Refresh Token")
            if not app_settings or not app_settings.lwa_client_id:
                missing_fields.append("LWA Client ID")
            if not app_settings or not app_settings.lwa_client_secret:
                missing_fields.append("LWA Client Secret")
            if not app_settings or not app_settings.aws_access_key:
                missing_fields.append("AWS Access Key")
            if not app_settings or not app_settings.aws_secret_key:
                missing_fields.append("AWS Secret Key")
            if not app_settings or not app_settings.role_arn:
                missing_fields.append("Role ARN")
            
            if missing_fields:
                result['status_details']['settings_complete'] = {
                    'status': 'warning',
                    'msg': f"الحقول التالية ناقصة أو فارغة: {', '.join(missing_fields)}"
                }
                result['success'] = False
                result['message'] = f"الحقول التالية مفقودة أو فارغة: {', '.join(missing_fields)}"
                return render(request, 'amazon_integration/test_connection.html', get_context(result))
            else:
                result['status_details']['settings_complete'] = {'status': 'success', 'msg': 'الإعدادات مكتملة.'}
            
            # جمع معلومات تصحيح الأخطاء
            debug_info = {
                'marketplace': amazon_settings.get_marketplace_id_display(),
                'marketplace_id': amazon_settings.marketplace_id,
                'refresh_token_length': len(amazon_settings.refresh_token),
                'lwa_client_id_length': len(app_settings.lwa_client_id),
                'lwa_client_secret_length': len(app_settings.lwa_client_secret),
                'aws_access_key_length': len(app_settings.aws_access_key),
                'aws_secret_key_length': len(app_settings.aws_secret_key),
                'role_arn_length': len(app_settings.role_arn)
            }
            result['debug_info'] = debug_info
            
            # التحقق من صحة الحقول
            field_errors = []
            if len(app_settings.role_arn) < 20:
                field_errors.append({
                    'field': 'Role ARN',
                    'error': f"Role ARN غير صالح (الطول: {len(app_settings.role_arn)}). يجب أن يكون بتنسيق: arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME",
                    'value_length': len(app_settings.role_arn)
                })
            if len(app_settings.aws_access_key) < 16:
                field_errors.append({
                    'field': 'AWS Access Key',
                    'error': f"AWS Access Key غير صالح (الطول: {len(app_settings.aws_access_key)}). يجب أن يكون بطول 20 حرفًا على الأقل.",
                    'value_length': len(app_settings.aws_access_key)
                })
            if len(app_settings.aws_secret_key) < 30:
                field_errors.append({
                    'field': 'AWS Secret Key',
                    'error': f"AWS Secret Key غير صالح (الطول: {len(app_settings.aws_secret_key)}). يجب أن يكون بطول 40 حرفًا على الأقل.",
                    'value_length': len(app_settings.aws_secret_key)
                })
            valid_marketplaces = ['A1AM78C64UM0Y8', 'A2VIGQ35RCS4UG', 'A2NGVSA5CAHHU9']
            if amazon_settings.marketplace_id not in valid_marketplaces:
                field_errors.append({
                    'field': 'Marketplace ID',
                    'error': f"معرف السوق ({amazon_settings.marketplace_id}) غير مدعوم. الأسواق المدعومة هي: مصر، السعودية، الإمارات.",
                    'value': amazon_settings.marketplace_id
                })
            if field_errors:
                result['success'] = False
                result['message'] = "هناك أخطاء في بيانات الاتصال. يرجى تصحيحها قبل المتابعة."
                result['field_errors'] = field_errors
                # إذا في أخطاء، خلي اكتمال الإعدادات أصفر
                result['status_details']['settings_complete'] = {
                    'status': 'warning',
                    'msg': 'هناك أخطاء في بعض الحقول. راجع التفاصيل بالأسفل.'
                }
                return render(request, 'amazon_integration/test_connection.html', get_context(result))
            
            # التحقق من صحة مفاتيح AWS باستخدام boto3 مباشرة
            aws_keys_verified = False
            try:
                # محاولة استيراد boto3
                try:
                    # تجاهل أخطاء الاستيراد في Pylance/Pyright
                    # type: ignore
                    import boto3
                    # type: ignore
                    from botocore.exceptions import ClientError, NoCredentialsError
                    
                    logger.info("التحقق من صحة مفاتيح AWS باستخدام boto3...")
                    
                    # إنشاء عميل STS للتحقق من المفاتيح
                    sts_client = boto3.client(
                        'sts',
                        aws_access_key_id=app_settings.aws_access_key,
                        aws_secret_access_key=app_settings.aws_secret_key,
                        region_name='us-east-1'  # استخدام منطقة افتراضية
                    )
                    
                    # محاولة الحصول على معلومات الحساب
                    response = sts_client.get_caller_identity()
                    account_id = response.get('Account', 'غير معروف')
                    logger.info(f"تم التحقق من صحة مفاتيح AWS. معرف الحساب: {account_id}")
                    
                    # تعيين حالة التحقق من المفاتيح
                    aws_keys_verified = True
                    result['status_details']['aws_keys_verified'] = {
                        'status': 'success',
                        'msg': f'تم التحقق من صحة مفاتيح AWS. معرف الحساب: {account_id}'
                    }
                    
                    # إضافة معلومات الحساب إلى معلومات التصحيح
                    debug_info['aws_account_id'] = account_id
                    
                except ImportError:
                    logger.warning("لم يتم العثور على مكتبة boto3. لا يمكن التحقق من صحة مفاتيح AWS.")
                    result['status_details']['aws_keys_verified'] = {
                        'status': 'warning',
                        'msg': 'لم يتم التحقق من مفاتيح AWS (مكتبة boto3 غير متوفرة)'
                    }
                except (ClientError, NoCredentialsError) as e:
                    logger.error(f"فشل التحقق من صحة مفاتيح AWS: {str(e)}")
                    result['status_details']['aws_keys_verified'] = {
                        'status': 'error',
                        'msg': f'فشل التحقق من مفاتيح AWS: {str(e)}'
                    }
            except Exception as e:
                logger.error(f"خطأ أثناء التحقق من صحة مفاتيح AWS: {str(e)}")
                result['status_details']['aws_keys_verified'] = {
                    'status': 'error',
                    'msg': f'خطأ أثناء التحقق من مفاتيح AWS: {str(e)}'
                }

            # التحقق من صحة مفاتيح LWA باستخدام الكلاس المخصص
            try:
                # استيراد الكلاس المخصص
                from amazon_integration.custom_sp_api import test_client_with_modified_keys
                from sp_api.base import Marketplaces
                from sp_api.api import Sellers
                
                # تحديد السوق المناسب
                marketplace = None
                if amazon_settings.marketplace_id == 'A1AM78C64UM0Y8':  # مصر
                    marketplace = Marketplaces.EG
                elif amazon_settings.marketplace_id == 'A2VIGQ35RCS4UG':  # السعودية
                    marketplace = Marketplaces.SA
                elif amazon_settings.marketplace_id == 'A2NGVSA5CAHHU9':  # الإمارات
                    marketplace = Marketplaces.AE
                else:
                    marketplace = Marketplaces.EG
                
                # اختبار LWA Client ID
                lwa_test_result = test_client_with_modified_keys(
                    api_class=Sellers,
                    marketplace=marketplace,
                    refresh_token=amazon_settings.refresh_token,
                    lwa_app_id=app_settings.lwa_client_id,
                    lwa_client_secret=app_settings.lwa_client_secret,
                    aws_access_key=app_settings.aws_access_key,
                    aws_secret_key=app_settings.aws_secret_key,
                    role_arn=app_settings.role_arn,
                    region='eu',
                    modify_key='lwa_app_id'
                )
                
                if lwa_test_result['success']:
                    result['status_details']['lwa_keys_verified'] = {
                        'status': 'success',
                        'msg': 'تم التحقق من صحة مفاتيح LWA.'
                    }
                else:
                    result['status_details']['lwa_keys_verified'] = {
                        'status': 'warning',
                        'msg': lwa_test_result['message']
                    }
            except Exception as e:
                logger.error(f"خطأ أثناء التحقق من صحة مفاتيح LWA: {str(e)}")
                result['status_details']['lwa_keys_verified'] = {
                    'status': 'error',
                    'msg': f'خطأ أثناء التحقق من صحة مفاتيح LWA: {str(e)}'
                }

            # محاولة إنشاء عميل Products API
            client = get_sp_api_client(Products)
            if not client:
                result['success'] = False
                result['message'] = "فشل في إنشاء عميل SP-API. تحقق من سجلات النظام للحصول على مزيد من التفاصيل."
                result['debug_info'] = debug_info
            else:
                try:
                    # استخدام واجهة برمجة تطبيقات أبسط للاختبار
                    from sp_api.api import Sellers
                    
                    # تسجيل محاولة الاتصال
                    logger.info("محاولة الاتصال بـ Amazon Sellers API للتحقق من الاتصال")
                    
                    # إنشاء عميل Sellers API
                    sellers_client = get_sp_api_client(Sellers)
                    
                    # إذا تم إنشاء العميل بنجاح، نحاول الاتصال بالـ API
                    if sellers_client:
                        # استخدام دالة أبسط للاختبار - الحصول على معرف البائع
                        logger.info("محاولة الحصول على معرف البائع")
                        
                        try:
                            response = sellers_client.get_marketplace_participation()
                            # إذا نجح الاتصال، فهذا يعني أن المفاتيح صحيحة
                            result['success'] = True
                            result['message'] = 'تم الاتصال بـ Amazon API بنجاح!'
                            result['connection_verified'] = True
                            logger.info("تم التحقق من صحة الاتصال بنجاح")
                            
                            # تسجيل نجاح الاتصال ونوع البيانات المستلمة
                            logger.info(f"تم الاتصال بنجاح. نوع الاستجابة: {type(response)}")
                            
                            # التحقق من وجود بيانات المشاركة في السوق
                            if hasattr(response, 'payload') and response.payload:
                                # تحليل البيانات المستلمة
                                marketplace_data = []
                                for participation in response.payload:
                                    marketplace_info = {}
                                    if isinstance(participation, dict) and 'marketplace' in participation:
                                        marketplace = participation.get('marketplace', {})
                                        marketplace_info['id'] = marketplace.get('id', 'غير معروف')
                                        marketplace_info['name'] = marketplace.get('name', 'غير معروف')
                                        marketplace_info['country_code'] = marketplace.get('countryCode', 'غير معروف')
                                        marketplace_info['default_currency'] = marketplace.get('defaultCurrencyCode', 'غير معروف')
                                        marketplace_info['default_language'] = marketplace.get('defaultLanguageCode', 'غير معروف')
                                        marketplace_info['domain'] = marketplace.get('domainName', 'غير معروف')
                                    
                                    if isinstance(participation, dict) and 'participation' in participation:
                                        participation_info = participation.get('participation', {})
                                        marketplace_info['is_participating'] = participation_info.get('isParticipating', False)
                                        marketplace_info['has_suspended_listings'] = participation_info.get('hasSuspendedListings', False)
                                    
                                    marketplace_data.append(marketplace_info)
                                
                                result['data'] = {'marketplaces': marketplace_data}
                                
                                # تحديث رسالة النجاح لتشمل معلومات عن الأسواق
                                egypt_marketplace = next((m for m in marketplace_data if m.get('id') == 'A1AM78C64UM0Y8'), None)
                                if egypt_marketplace:
                                    result['message'] = f"تم الاتصال بـ Amazon API بنجاح! تم العثور على سوق مصر ({egypt_marketplace.get('name')})."
                                else:
                                    result['message'] = f"تم الاتصال بـ Amazon API بنجاح! تم العثور على {len(marketplace_data)} سوق."
                            
                            # إضافة تحذير إذا لم يتم التحقق من مفاتيح AWS
                            if not aws_keys_verified:
                                result['message'] += " تنبيه: لم يتم التحقق من صحة مفاتيح AWS بشكل مباشر."
                                
                        except Exception as api_error:
                            result['success'] = False
                            result['message'] = f"فشل في الحصول على بيانات السوق: {str(api_error)}"
                            logger.error(f"خطأ في الحصول على بيانات السوق: {str(api_error)}")
                    else:
                        result['success'] = False
                        result['message'] = "فشل في إنشاء عميل Sellers API. تحقق من سجلات النظام للحصول على مزيد من التفاصيل."
                        logger.error("فشل في إنشاء عميل Sellers API")
                
                except Exception as api_error:
                    result['success'] = False
                    error_str = str(api_error)
                    if "invalid_client" in error_str and "401" in error_str:
                        result['message'] = "فشل مصادقة العميل: معرف العميل (Client ID) أو سر العميل (Client Secret) غير صحيح."
                        logger.error(f"خطأ مصادقة العميل: {error_str}")
                    elif "invalid_grant" in error_str:
                        result['message'] = "خطأ في Refresh Token: قد يكون منتهي الصلاحية أو غير صالح."
                        logger.error(f"خطأ في Refresh Token: {error_str}")
                    elif "access_denied" in error_str:
                        result['message'] = "تم رفض الوصول: تأكد من صحة الأذونات والأدوار."
                        logger.error(f"خطأ في الأذونات: {error_str}")
                    elif "UnrecognizedClientException" in error_str:
                        result['message'] = "خطأ في مفاتيح AWS: مفتاح الوصول أو المفتاح السري غير صحيح."
                        logger.error(f"خطأ في مفاتيح AWS: {error_str}")
                    else:
                        result['message'] = f"فشل الاتصال: {error_str}"
                        logger.error(f"خطأ عام في الاتصال: {error_str}")
                    result['debug_info'] = debug_info
        
        except Exception as e:
            result['success'] = False
            result['message'] = f'فشل الاتصال بسبب خطأ غير متوقع: {str(e)}'
            logger.exception("خطأ غير متوقع أثناء اختبار الاتصال")
    
    return render(request, 'amazon_integration/test_connection.html', get_context(result))

def get_context(result):
    """
    دالة مساعدة للحصول على سياق العرض
    """
    # التحقق من وجود إعدادات نشطة
    has_active_settings = AmazonSettings.objects.filter(is_active=True).exists()
    app_settings_exist = AppSettings.objects.filter(is_active=True).exists()
    
    # التحقق من اكتمال الإعدادات
    settings_complete = False
    if has_active_settings and app_settings_exist:
        amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
        app_settings = AppSettings.objects.filter(is_active=True).first()
        
        settings_complete = (
            amazon_settings.refresh_token and
            app_settings.aws_access_key and
            app_settings.aws_secret_key and
            app_settings.role_arn and
            app_settings.lwa_client_id and
            app_settings.lwa_client_secret
        )
    
    return {
        'title': 'اختبار الاتصال بأمازون',
        'has_active_settings': has_active_settings,
        'app_settings_exist': app_settings_exist,
        'settings_complete': settings_complete,
        'result': result
    } 