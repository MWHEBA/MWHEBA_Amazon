#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار صحة LWA Client ID باستخدام مكتبة SP-API المعدلة
"""

import os
import sys
import django
import logging
from pathlib import Path

# إعداد Django للوصول إلى النماذج
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbm_sync_project.settings')
django.setup()

# استيراد النماذج بعد إعداد Django
from amazon_integration.models import AmazonSettings, AppSettings
from amazon_integration.custom_sp_api import test_client_with_modified_keys
from sp_api.api import Sellers
from sp_api.base import Marketplaces

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_lwa_client_id():
    """
    اختبار صحة LWA Client ID باستخدام مكتبة SP-API المعدلة
    """
    logger.info("بدء اختبار LWA Client ID...")
    
    # الحصول على إعدادات التطبيق وأمازون
    app_settings = AppSettings.objects.filter(is_active=True).first()
    amazon_settings = AmazonSettings.objects.filter(is_active=True).first()
    
    if not app_settings or not amazon_settings:
        logger.error("لا توجد إعدادات نشطة")
        return False
    
    # التحقق من وجود المفاتيح
    if not app_settings.lwa_client_id or not app_settings.lwa_client_secret:
        logger.error("LWA Client ID أو LWA Client Secret غير موجود في إعدادات التطبيق")
        return False
    
    if not amazon_settings.refresh_token:
        logger.error("Refresh Token غير موجود في إعدادات أمازون")
        return False
    
    # طباعة معلومات المفاتيح (بدون كشف المفتاح الكامل)
    logger.info(f"LWA Client ID: {app_settings.lwa_client_id[:5]}...{app_settings.lwa_client_id[-3:]}")
    logger.info(f"LWA Client Secret Length: {len(app_settings.lwa_client_secret)}")
    
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
    logger.info("اختبار LWA Client ID...")
    result = test_client_with_modified_keys(
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
    
    # طباعة النتيجة
    if result['success']:
        logger.info(f"اختبار LWA Client ID نجح: {result['message']}")
    else:
        logger.error(f"اختبار LWA Client ID فشل: {result['message']}")
        if result['error']:
            logger.error(f"الخطأ: {result['error']}")
    
    # اختبار LWA Client Secret
    logger.info("اختبار LWA Client Secret...")
    result_secret = test_client_with_modified_keys(
        api_class=Sellers,
        marketplace=marketplace,
        refresh_token=amazon_settings.refresh_token,
        lwa_app_id=app_settings.lwa_client_id,
        lwa_client_secret=app_settings.lwa_client_secret,
        aws_access_key=app_settings.aws_access_key,
        aws_secret_key=app_settings.aws_secret_key,
        role_arn=app_settings.role_arn,
        region='eu',
        modify_key='lwa_client_secret'
    )
    
    # طباعة النتيجة
    if result_secret['success']:
        logger.info(f"اختبار LWA Client Secret نجح: {result_secret['message']}")
    else:
        logger.error(f"اختبار LWA Client Secret فشل: {result_secret['message']}")
        if result_secret['error']:
            logger.error(f"الخطأ: {result_secret['error']}")
    
    return result['success'] and result_secret['success']

if __name__ == "__main__":
    logger.info("بدء برنامج اختبار LWA Client ID و Secret")
    
    if test_lwa_client_id():
        logger.info("اختبار LWA Client ID و Secret نجح!")
        print("✅ LWA Client ID و Secret صالحان ويتم استخدامهما فعليًا.")
        sys.exit(0)
    else:
        logger.error("اختبار LWA Client ID و Secret فشل!")
        print("❌ هناك مشكلة في LWA Client ID أو Secret. راجع السجلات للحصول على مزيد من التفاصيل.")
        sys.exit(1) 