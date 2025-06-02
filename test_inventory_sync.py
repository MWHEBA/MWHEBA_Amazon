import os
import django
import time

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbm_sync_project.settings')
django.setup()

from amazon_integration.models import AmazonSettings, AppSettings
from inventory.models import Product
from amazon_integration.services import sync_quantity_to_amazon
from sp_api.base import Marketplaces
from sp_api.api import Inventories
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_update_inventory():
    """
    اختبار عملية تحديث المخزون
    """
    print("بدء اختبار تحديث المخزون...")
    
    # التحقق من الإعدادات
    amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
    app_settings = AppSettings.objects.filter(is_active=True).first()
    
    if not amazon_settings or not app_settings:
        print("لا توجد إعدادات كافية. الرجاء إعداد الإعدادات أولاً.")
        return
    
    if not amazon_settings.location_id:
        print("رقم موقع FBM غير موجود. الرجاء إضافته في إعدادات أمازون.")
        return
    
    print("معلومات الإعدادات:")
    print(f"  - سوق أمازون: {amazon_settings.get_marketplace_id_display()}")
    print(f"  - رقم موقع FBM: {amazon_settings.location_id}")
    
    # إنشاء عميل الـ API مباشرة
    print("\nإنشاء عميل API...")
    try:
        # إعداد بيانات الاعتماد
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
        
        marketplace = None
        if amazon_settings.marketplace_id == 'A1AM78C64UM0Y8':  # مصر
            marketplace = Marketplaces.EG
        elif amazon_settings.marketplace_id == 'A2VIGQ35RCS4UG':  # السعودية
            marketplace = Marketplaces.SA
        elif amazon_settings.marketplace_id == 'A2NGVSA5CAHHU9':  # الإمارات
            marketplace = Marketplaces.AE
        else:
            marketplace = Marketplaces.EG
        
        # إنشاء عميل Inventories
        client = Inventories(
            marketplace=marketplace,
            refresh_token=amazon_settings.refresh_token,
            credentials=credentials_dict
        )
        
        print("تم إنشاء عميل API بنجاح!")
        
        # الحصول على منتج للاختبار
        test_product = Product.objects.filter(is_fbm=True, amazon_sku__isnull=False).first()
        
        if not test_product:
            print("\nلا توجد منتجات FBM مناسبة للاختبار.")
            return
        
        print(f"\nاختبار تحديث منتج: {test_product.title}")
        print(f"  - SKU: {test_product.amazon_sku}")
        print(f"  - الكمية الحالية: {test_product.quantity}")
        
        try:
            print("\nاختبار 1: استدعاء API مباشرة...")
            response = client.update_inventory(
                path_params={'locationId': amazon_settings.location_id, 'skuId': test_product.amazon_sku},
                query_params={'quantity': test_product.quantity}
            )
            
            print("\nالاستجابة من أمازون:")
            print(response.payload)
            
            print("\nاختبار 2: استخدام دالة sync_quantity_to_amazon...")
            result = sync_quantity_to_amazon(test_product)
            print(f"نتيجة الاختبار: {'نجاح' if result else 'فشل'}")
            
            print("\nتم إكمال الاختبار بنجاح!")
            
        except Exception as e:
            print(f"\nحدث خطأ أثناء الاختبار: {str(e)}")
            
    except Exception as e:
        print(f"\nحدث خطأ أثناء إنشاء عميل API: {str(e)}")

if __name__ == "__main__":
    test_update_inventory() 