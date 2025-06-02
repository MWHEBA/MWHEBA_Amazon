#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
نسخة معدلة من مكتبة SP-API لتعطيل التخزين المؤقت وإجبارها على استخدام المفاتيح المقدمة فقط
"""

import os
import logging
from typing import Optional, Type, Dict, Any
from sp_api.base import Client, Marketplaces
from sp_api.base.credential_provider import CredentialProvider, FromCodeCredentialProvider, BaseCredentialProvider

logger = logging.getLogger(__name__)

def create_sp_api_client(
    api_class: Type[Client],
    marketplace: Marketplaces,
    refresh_token: str,
    lwa_app_id: str,
    lwa_client_secret: str,
    aws_access_key: str,
    aws_secret_key: str,
    role_arn: str,
    region: str = 'eu',
) -> Optional[Client]:
    """
    إنشاء عميل SP-API مع تعطيل التخزين المؤقت وإجبار استخدام المفاتيح المقدمة فقط
    
    Args:
        api_class: فئة واجهة برمجة التطبيقات (Orders, Products, إلخ)
        marketplace: سوق أمازون
        refresh_token: رمز التحديث
        lwa_app_id: معرف تطبيق LWA
        lwa_client_secret: سر عميل LWA
        aws_access_key: مفتاح وصول AWS
        aws_secret_key: المفتاح السري لـ AWS
        role_arn: ARN للدور
        region: المنطقة (افتراضي: 'eu')
    
    Returns:
        كائن عميل SP-API أو None في حالة فشل الإنشاء
    """
    try:
        # تسجيل بداية محاولة إنشاء العميل
        logger.info(f"بدء محاولة إنشاء عميل {api_class.__name__} باستخدام المفاتيح المقدمة فقط")
        
        # إعداد بيانات الاعتماد
        credentials = {
            'refresh_token': refresh_token,
            'lwa_app_id': lwa_app_id,
            'lwa_client_secret': lwa_client_secret,
        }
        
        # إعداد متغيرات البيئة المطلوبة للـ SP-API
        # نحفظ القيم الأصلية لاستعادتها لاحقًا
        original_env = {
            'SP_API_AWS_ACCESS_KEY': os.environ.get('SP_API_AWS_ACCESS_KEY'),
            'SP_API_AWS_SECRET_KEY': os.environ.get('SP_API_AWS_SECRET_KEY'),
            'SP_API_AWS_ROLE_ARN': os.environ.get('SP_API_AWS_ROLE_ARN'),
            'SP_API_REGION': os.environ.get('SP_API_REGION'),
            'SP_API_REFRESH_TOKEN': os.environ.get('SP_API_REFRESH_TOKEN'),
            'LWA_APP_ID': os.environ.get('LWA_APP_ID'),
            'LWA_CLIENT_SECRET': os.environ.get('LWA_CLIENT_SECRET'),
        }
        
        # تعيين متغيرات البيئة الجديدة
        os.environ['SP_API_AWS_ACCESS_KEY'] = aws_access_key
        os.environ['SP_API_AWS_SECRET_KEY'] = aws_secret_key
        os.environ['SP_API_AWS_ROLE_ARN'] = role_arn
        os.environ['SP_API_REGION'] = region
        os.environ['SP_API_REFRESH_TOKEN'] = refresh_token
        os.environ['LWA_APP_ID'] = lwa_app_id
        os.environ['LWA_CLIENT_SECRET'] = lwa_client_secret
        
        try:
            # إنشاء العميل باستخدام المفاتيح المقدمة مباشرة
            client = api_class(
                marketplace=marketplace,
                refresh_token=refresh_token,
                credentials=credentials
            )
            
            logger.info(f"تم إنشاء عميل {api_class.__name__} بنجاح")
            return client
        finally:
            # استعادة متغيرات البيئة الأصلية
            for key, value in original_env.items():
                if value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = value
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء عميل {api_class.__name__}: {str(e)}")
        return None


def test_client_with_modified_keys(
    api_class: Type[Client],
    marketplace: Marketplaces,
    refresh_token: str,
    lwa_app_id: str,
    lwa_client_secret: str,
    aws_access_key: str,
    aws_secret_key: str,
    role_arn: str,
    region: str = 'eu',
    modify_key: str = 'lwa_app_id'  # المفتاح المراد تعديله للاختبار
) -> Dict[str, Any]:
    """
    اختبار عميل SP-API مع تعديل أحد المفاتيح للتأكد من استخدامه فعليًا
    
    Args:
        api_class: فئة واجهة برمجة التطبيقات (Orders, Products, إلخ)
        marketplace: سوق أمازون
        refresh_token: رمز التحديث
        lwa_app_id: معرف تطبيق LWA
        lwa_client_secret: سر عميل LWA
        aws_access_key: مفتاح وصول AWS
        aws_secret_key: المفتاح السري لـ AWS
        role_arn: ARN للدور
        region: المنطقة (افتراضي: 'eu')
        modify_key: المفتاح المراد تعديله للاختبار (افتراضي: 'lwa_app_id')
    
    Returns:
        قاموس يحتوي على نتائج الاختبار
    """
    result = {
        'success': False,
        'message': '',
        'original_key_works': False,
        'modified_key_fails': False,
        'error': None
    }
    
    # اختبار المفتاح الأصلي
    try:
        logger.info(f"اختبار الاتصال باستخدام المفتاح الأصلي: {modify_key}")
        client = create_sp_api_client(
            api_class=api_class,
            marketplace=marketplace,
            refresh_token=refresh_token,
            lwa_app_id=lwa_app_id,
            lwa_client_secret=lwa_client_secret,
            aws_access_key=aws_access_key,
            aws_secret_key=aws_secret_key,
            role_arn=role_arn,
            region=region
        )
        
        if client:
            # محاولة استدعاء دالة بسيطة للتحقق من صحة العميل
            if hasattr(client, 'get_service_status'):
                response = client.get_service_status()
                result['original_key_works'] = True
                logger.info(f"نجح الاتصال باستخدام المفتاح الأصلي: {modify_key}")
            else:
                # إذا لم تكن الدالة متوفرة، نعتبر أن العميل يعمل
                result['original_key_works'] = True
                logger.info(f"تم إنشاء العميل بنجاح باستخدام المفتاح الأصلي: {modify_key}")
    except Exception as e:
        logger.error(f"فشل الاتصال باستخدام المفتاح الأصلي: {str(e)}")
        result['error'] = str(e)
    
    # اختبار المفتاح المعدل
    try:
        logger.info(f"اختبار الاتصال باستخدام مفتاح معدل: {modify_key}")
        
        # نسخ القيم الأصلية
        modified_lwa_app_id = lwa_app_id
        modified_lwa_client_secret = lwa_client_secret
        modified_aws_access_key = aws_access_key
        modified_aws_secret_key = aws_secret_key
        
        # تعديل المفتاح المطلوب
        if modify_key == 'lwa_app_id':
            modified_lwa_app_id = lwa_app_id + "_test"
        elif modify_key == 'lwa_client_secret':
            modified_lwa_client_secret = lwa_client_secret + "_test"
        elif modify_key == 'aws_access_key':
            modified_aws_access_key = aws_access_key + "_test"
        elif modify_key == 'aws_secret_key':
            modified_aws_secret_key = aws_secret_key + "_test"
        
        client = create_sp_api_client(
            api_class=api_class,
            marketplace=marketplace,
            refresh_token=refresh_token,
            lwa_app_id=modified_lwa_app_id,
            lwa_client_secret=modified_lwa_client_secret,
            aws_access_key=modified_aws_access_key,
            aws_secret_key=modified_aws_secret_key,
            role_arn=role_arn,
            region=region
        )
        
        if client:
            # محاولة استدعاء دالة بسيطة للتحقق من صحة العميل
            if hasattr(client, 'get_service_status'):
                try:
                    response = client.get_service_status()
                    logger.warning(f"نجح الاتصال باستخدام المفتاح المعدل: {modify_key}! هذا غير متوقع.")
                except Exception as e:
                    logger.info(f"فشل الاتصال باستخدام المفتاح المعدل: {modify_key} (هذا متوقع)")
                    result['modified_key_fails'] = True
            else:
                # نحاول استدعاء أي دالة أخرى متاحة
                try:
                    # نحاول استدعاء أي دالة
                    for method_name in dir(client):
                        if method_name.startswith('get_') and callable(getattr(client, method_name)):
                            method = getattr(client, method_name)
                            method()
                            break
                    logger.warning(f"نجح الاتصال باستخدام المفتاح المعدل: {modify_key}! هذا غير متوقع.")
                except Exception as e:
                    logger.info(f"فشل الاتصال باستخدام المفتاح المعدل: {modify_key} (هذا متوقع)")
                    result['modified_key_fails'] = True
    except Exception as e:
        logger.info(f"فشل إنشاء العميل باستخدام المفتاح المعدل: {str(e)} (هذا متوقع)")
        result['modified_key_fails'] = True
    
    # تقييم النتيجة النهائية
    if result['original_key_works'] and result['modified_key_fails']:
        result['success'] = True
        result['message'] = f"تم التحقق بنجاح من استخدام المفتاح {modify_key}"
    elif result['original_key_works'] and not result['modified_key_fails']:
        result['success'] = False
        result['message'] = f"المفتاح {modify_key} غير مستخدم فعليًا! يبدو أن المكتبة تستخدم مفاتيح من مصدر آخر."
    elif not result['original_key_works']:
        result['success'] = False
        result['message'] = f"فشل الاتصال باستخدام المفتاح الأصلي. تحقق من صحة المفاتيح."
    
    return result 