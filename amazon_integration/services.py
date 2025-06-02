import os
import logging
from django.conf import settings
from sp_api.api import Products, Inventories, CatalogItems
from sp_api.base import SellingApiException, Marketplaces
from sp_api.base.credential_provider import CredentialProvider
from .models import AmazonSettings, AppSettings
from typing import List, Dict, Any, Optional, Type, TypeVar
from sp_api.api import Orders, Feeds
from sp_api.base import Client

logger = logging.getLogger(__name__)

# Type variable for the SP-API clients
T = TypeVar('T', bound=Client)

def get_sp_api_client(api_class: Type[T]) -> Optional[T]:
    """
    إنشاء عميل SP-API مع الإعدادات النشطة
    
    Args:
        api_class: فئة واجهة برمجة التطبيقات (Orders, Products, إلخ)
    
    Returns:
        كائن عميل SP-API أو None في حالة عدم وجود إعدادات نشطة
    """
    try:
        # تسجيل بداية محاولة إنشاء العميل
        logger.info(f"بدء محاولة إنشاء عميل {api_class.__name__}")
        
        # جلب الإعدادات النشطة
        amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
        if not amazon_settings:
            logger.error("لا توجد إعدادات نشطة للاتصال بـ Amazon SP-API")
            return None
        
        # التحقق من وجود refresh_token
        if not amazon_settings.refresh_token:
            logger.error("Refresh token غير موجود في إعدادات أمازون")
            return None
        
        # جلب إعدادات التطبيق إذا كانت متوفرة
        app_settings = AppSettings.objects.filter(is_active=True).first()
        if not app_settings:
            logger.error("لا توجد إعدادات تطبيق نشطة")
            return None
        
        # التحقق من اكتمال إعدادات التطبيق
        missing_fields = []
        if not app_settings.aws_access_key:
            missing_fields.append("AWS Access Key")
        if not app_settings.aws_secret_key:
            missing_fields.append("AWS Secret Key")
        if not app_settings.role_arn:
            missing_fields.append("Role ARN")
        if not app_settings.lwa_client_id:
            missing_fields.append("LWA Client ID")
        if not app_settings.lwa_client_secret:
            missing_fields.append("LWA Client Secret")
        
        if missing_fields:
            logger.error(f"إعدادات التطبيق غير مكتملة: {', '.join(missing_fields)}")
            return None
        
        # تسجيل أطوال البيانات للتشخيص
        logger.info(f"طول Refresh Token: {len(amazon_settings.refresh_token)}")
        logger.info(f"طول AWS Access Key: {len(app_settings.aws_access_key)}")
        logger.info(f"طول AWS Secret Key: {len(app_settings.aws_secret_key)}")
        logger.info(f"طول Role ARN: {len(app_settings.role_arn)}")
        logger.info(f"طول LWA Client ID: {len(app_settings.lwa_client_id)}")
        logger.info(f"طول LWA Client Secret: {len(app_settings.lwa_client_secret)}")
        
        # تحديد السوق المناسب
        marketplace_id = amazon_settings.marketplace_id
        marketplace = None
        
        # تسجيل معرف السوق
        logger.info(f"معرف السوق المستخدم: {marketplace_id}")
        
        # التحقق من أن معرف السوق هو أحد الأسواق المدعومة فقط
        if marketplace_id == 'A1AM78C64UM0Y8':  # مصر
            marketplace = Marketplaces.EG
            logger.info("تم اختيار سوق مصر")
        elif marketplace_id == 'A2VIGQ35RCS4UG':  # السعودية
            marketplace = Marketplaces.SA
            logger.info("تم اختيار سوق السعودية")
        elif marketplace_id == 'A2NGVSA5CAHHU9':  # الإمارات
            marketplace = Marketplaces.AE
            logger.info("تم اختيار سوق الإمارات")
        else:
            # إذا كان معرف السوق غير معروف، استخدام مصر كقيمة افتراضية
            logger.warning(f"معرف سوق غير مدعوم: {marketplace_id}، استخدام مصر كقيمة افتراضية")
            # إعادة تعيين معرف السوق إلى مصر
            marketplace_id = 'A1AM78C64UM0Y8'
            marketplace = Marketplaces.EG
            # تحديث الإعدادات في قاعدة البيانات إذا كان ممكنًا
            try:
                amazon_settings.marketplace_id = marketplace_id
                amazon_settings.save(update_fields=['marketplace_id'])
                logger.info("تم تحديث معرف السوق إلى مصر في قاعدة البيانات")
            except Exception as e:
                logger.error(f"فشل تحديث معرف السوق في قاعدة البيانات: {str(e)}")
        
        # التحقق من Role ARN
        if len(app_settings.role_arn) < 20:
            logger.error(f"Role ARN غير صالح (الطول: {len(app_settings.role_arn)}). يجب أن يكون بتنسيق: arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME")
            return None
        
        # إنشاء credentials باستخدام CredentialProvider
        credentials_dict = {
            'refresh_token': amazon_settings.refresh_token,
            'lwa_app_id': app_settings.lwa_client_id,
            'lwa_client_secret': app_settings.lwa_client_secret,
        }
        
        # إعداد متغيرات البيئة المطلوبة للـ SP-API
        os.environ['SP_API_AWS_ACCESS_KEY'] = app_settings.aws_access_key
        os.environ['SP_API_AWS_SECRET_KEY'] = app_settings.aws_secret_key
        os.environ['SP_API_AWS_ROLE_ARN'] = app_settings.role_arn
        os.environ['SP_API_REGION'] = 'eu'  # لأن سوق مصر يستخدم endpoint الخاص بـ EU
        
        # تخزين المفاتيح المستخدمة للتشخيص
        os.environ['SP_API_LWA_APP_ID'] = app_settings.lwa_client_id
        os.environ['SP_API_LWA_CLIENT_SECRET'] = app_settings.lwa_client_secret
        
        # التحقق من صحة المفاتيح إذا كان ذلك مطلوبًا
        if api_class.__name__ in ['Sellers', 'Products'] and os.environ.get('SP_API_VERIFY_KEYS', '').lower() == 'true':
            logger.info("التحقق من صحة مفاتيح AWS...")
            try:
                # محاولة استيراد boto3 - قد لا يكون متوفرًا
                try:
                    # تجاهل أخطاء الاستيراد في Pylance/Pyright
                    # type: ignore
                    import boto3
                    # type: ignore
                    from botocore.exceptions import ClientError, NoCredentialsError
                    
                    # محاولة إنشاء عميل AWS بسيط للتحقق من المفاتيح
                    try:
                        sts_client = boto3.client(
                            'sts',
                            aws_access_key_id=app_settings.aws_access_key,
                            aws_secret_access_key=app_settings.aws_secret_key,
                            region_name='us-east-1'  # استخدام منطقة افتراضية
                        )
                        
                        # محاولة الحصول على معلومات الحساب
                        response = sts_client.get_caller_identity()
                        logger.info(f"تم التحقق من صحة مفاتيح AWS. معرف الحساب: {response.get('Account', 'غير معروف')}")
                    except (ClientError, NoCredentialsError) as e:
                        logger.error(f"فشل التحقق من صحة مفاتيح AWS: {str(e)}")
                        return None
                except ImportError:
                    logger.warning("لم يتم العثور على مكتبة boto3. لا يمكن التحقق من صحة مفاتيح AWS.")
            except Exception as e:
                logger.error(f"خطأ أثناء التحقق من صحة المفاتيح: {str(e)}")
                # نستمر في التنفيذ حتى لو فشل التحقق من المفاتيح
        
        # تسجيل محاولة إنشاء العميل
        logger.info(f"محاولة إنشاء عميل {api_class.__name__} لسوق {marketplace.name}")
        
        try:
            # إنشاء العميل
            client = api_class(
                marketplace=marketplace,
                refresh_token=amazon_settings.refresh_token,
                credentials=credentials_dict
            )
            
            # اختبار الاتصال للتأكد من أن العميل يعمل بشكل صحيح
            # هذا يساعد في اكتشاف مشاكل مثل "'list' object has no attribute 'get'"
            if api_class.__name__ == 'Sellers':
                try:
                    # محاولة استدعاء دالة بسيطة للتحقق من صحة العميل
                    logger.info("اختبار عميل Sellers API")
                    # استخدام try/except لتجنب الأخطاء المحتملة
                    try:
                        test_response = client.get_marketplace_participation()
                        logger.info("تم اختبار عميل Sellers API بنجاح")
                    except AttributeError as attr_error:
                        if "'list' object has no attribute 'get'" in str(attr_error):
                            logger.error("تم اكتشاف خطأ معروف: 'list' object has no attribute 'get'")
                            logger.error("هذا يشير إلى مشكلة في استجابة API أو في مكتبة SP-API")
                            return None
                        else:
                            # إعادة رمي الخطأ إذا كان غير معروف
                            raise
                except Exception as test_error:
                    logger.error(f"فشل اختبار عميل Sellers API: {str(test_error)}")
                    # نستمر بدون إرجاع None لأن الخطأ قد يكون فقط في دالة الاختبار
            
            logger.info(f"تم إنشاء عميل {api_class.__name__} بنجاح")
            return client
        except Exception as client_error:
            logger.error(f"خطأ في إنشاء عميل {api_class.__name__}: {str(client_error)}")
            # تسجيل المزيد من التفاصيل للتشخيص
            if hasattr(client_error, 'response') and hasattr(client_error.response, 'text'):
                logger.error(f"تفاصيل الخطأ: {client_error.response.text}")
            return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إنشاء عميل SP-API: {str(e)}")
        return None


def sync_quantity_to_amazon(product):
    """
    مزامنة كمية المنتج مع Amazon SP-API
    
    Args:
        product: نموذج المنتج الذي يحتوي على معلومات المنتج
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    try:
        # التحقق من وجود amazon_sku
        if not product.amazon_sku:
            logger.error(f"المنتج {product.title} ليس له رمز SKU على أمازون")
            return False
            
        # الحصول على عميل Inventories API
        client = get_sp_api_client(Inventories)
        
        if not client:
            logger.error("فشل في إنشاء عميل SP-API")
            return False
        
        # الحصول على رقم موقع FBM
        amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
        if not amazon_settings or not amazon_settings.location_id:
            logger.error("رقم موقع FBM غير موجود في إعدادات أمازون")
            return False
            
        location_id = amazon_settings.location_id
        
        # تنفيذ طلب تحديث المخزون
        logger.info(f"محاولة تحديث كمية المنتج {product.amazon_sku} إلى {product.quantity}")
        
        try:
            # استدعاء update_inventory مع البارامترات المطلوبة
            response = client.update_inventory(
                path_params={'locationId': location_id, 'skuId': product.amazon_sku},
                query_params={'quantity': product.quantity}
            )
            
            # التحقق من نجاح الاستجابة
            if response and hasattr(response, 'payload'):
                # التحقق من مطابقة الكمية في السوق المستهدف
                marketplaces = response.payload.get('marketplaceChannelInventories', [])
                if marketplaces:
                    sellable_quantity = marketplaces[0].get('sellableQuantity', -1)
                    
                    if sellable_quantity == product.quantity:
                        logger.info(f"تم تحديث كمية المنتج {product.amazon_sku} بنجاح (الكمية: {product.quantity})")
                    else:
                        logger.warning(f"تم الاتصال بنجاح ولكن قد تكون هناك مشكلة في تحديث الكمية. الكمية المتوقعة: {product.quantity}، الكمية المستلمة: {sellable_quantity}")
                
                return True
            
            logger.error(f"استجابة غير متوقعة من API أمازون")
            return False
            
        except SellingApiException as api_error:
            # التعامل مع أخطاء الـ Rate Limits
            if hasattr(api_error, 'code') and api_error.code == 429:
                logger.warning(f"تم تجاوز حد الطلبات (Rate Limit). سيتم إعادة المحاولة لاحقًا.")
                # هنا يمكن تنفيذ آلية Retry بتأخير تصاعدي
                return False
                
            # التعامل مع أخطاء التوثيق
            if hasattr(api_error, 'code') and api_error.code in (401, 403):
                logger.error(f"خطأ في التوثيق. يرجى إعادة تفويض التطبيق أو تعديل صلاحيات IAM.")
                return False
                
            logger.error(f"خطأ في SP-API أثناء تحديث المخزون: {str(api_error)}")
            return False
        
    except Exception as e:
        logger.error(f"خطأ غير متوقع أثناء تحديث المخزون: {str(e)}")
        return False


def fetch_fbm_products():
    """
    جلب منتجات FBM من Amazon SP-API
    
    Returns:
        list: قائمة المنتجات من أمازون
    """
    # TO DO: Connect to Amazon API
    try:
        # الحصول على عميل Products API
        client = get_sp_api_client(Products)
        
        if not client:
            logger.error("فشل في إنشاء عميل SP-API")
            return []
            
        # في الوقت الحالي، نقوم بإرجاع بيانات وهمية
        # في التطبيق الفعلي، سيتم استبدال هذا بمكالمة API حقيقية
        logger.info("محاولة جلب منتجات FBM من أمازون")
        
        # مثال على البيانات المرجعة
        dummy_products = [
            {
                "title": "منتج تجريبي 1",
                "amazon_sku": "AMZSKU001",
                "quantity": 10,
                "is_fbm": True
            },
            {
                "title": "منتج تجريبي 2",
                "amazon_sku": "AMZSKU002",
                "quantity": 5,
                "is_fbm": True
            }
        ]
        
        return dummy_products
        
    except SellingApiException as e:
        logger.error(f"خطأ في SP-API أثناء جلب المنتجات: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"خطأ غير متوقع أثناء جلب المنتجات: {str(e)}")
        return [] 