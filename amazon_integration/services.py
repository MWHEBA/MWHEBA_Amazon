import os
import logging
from django.conf import settings
from sp_api.api import Products, Inventories, CatalogItems
from sp_api.base import SellingApiException
from .models import AmazonSettings

logger = logging.getLogger(__name__)

def get_sp_api_client(api_class):
    """
    إنشاء عميل SP-API بناءً على الإعدادات
    
    Args:
        api_class: فئة API المطلوبة (مثل Products, Inventories, إلخ)
    
    Returns:
        عميل SP-API
    """
    try:
        # محاولة الحصول على إعدادات أمازون من قاعدة البيانات
        try:
            amazon_settings = AmazonSettings.objects.first()
            if amazon_settings:
                client = api_class(
                    credentials=dict(
                        refresh_token=amazon_settings.refresh_token,
                        lwa_app_id=amazon_settings.lwa_client_id,
                        lwa_client_secret=amazon_settings.lwa_client_secret,
                        aws_access_key=amazon_settings.aws_access_key,
                        aws_secret_key=amazon_settings.aws_secret_key,
                        role_arn=amazon_settings.role_arn
                    )
                )
                return client
        except Exception as db_error:
            logger.warning(f"لم يتم العثور على إعدادات في قاعدة البيانات، محاولة استخدام ملف .env: {str(db_error)}")
        
        # استخدام الإعدادات من ملف .env كاحتياطي
        client = api_class(
            credentials=dict(
                refresh_token=settings.REFRESH_TOKEN,
                lwa_app_id=settings.LWA_CLIENT_ID,
                lwa_client_secret=settings.LWA_CLIENT_SECRET,
                aws_access_key=settings.AWS_ACCESS_KEY,
                aws_secret_key=settings.AWS_SECRET_KEY,
                role_arn=settings.ROLE_ARN
            )
        )
        return client
    except Exception as e:
        logger.error(f"فشل في إنشاء عميل SP-API: {str(e)}")
        raise


def sync_quantity_to_amazon(product):
    """
    مزامنة كمية المنتج مع Amazon SP-API
    
    Args:
        product: نموذج المنتج الذي يحتوي على معلومات المنتج
    
    Returns:
        bool: نجاح أو فشل العملية
    """
    # TO DO: Connect to Amazon API
    try:
        # الحصول على عميل Inventories API
        client = get_sp_api_client(Inventories)
        
        # إعداد البيانات للتحديث
        data = {
            "sellerId": "SELLER_ID",  # استبدل بمعرف البائع الخاص بك
            "sku": product.amazon_sku,
            "quantity": product.quantity
        }
        
        # تحديث المخزون على أمازون
        # ملاحظة: هذا مجرد مكان للكود الفعلي، وقد تختلف الطريقة الدقيقة حسب SP-API
        logger.info(f"محاولة تحديث كمية المنتج {product.amazon_sku} إلى {product.quantity}")
        
        # هنا سيتم استدعاء API الفعلي عند الاتصال بأمازون
        # response = client.update_inventory(data)
        
        # في الوقت الحالي، نقوم بمحاكاة استجابة ناجحة
        logger.info(f"تم تحديث كمية المنتج {product.amazon_sku} بنجاح")
        return True
        
    except SellingApiException as e:
        logger.error(f"خطأ في SP-API أثناء تحديث المخزون: {str(e)}")
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