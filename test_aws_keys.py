#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار صحة مفاتيح AWS باستخدام boto3 مباشرة
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
from amazon_integration.models import AppSettings

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_aws_keys():
    """
    اختبار صحة مفاتيح AWS باستخدام boto3 مباشرة
    """
    logger.info("بدء اختبار مفاتيح AWS...")
    
    # الحصول على إعدادات التطبيق
    app_settings = AppSettings.objects.filter(is_active=True).first()
    if not app_settings:
        logger.error("لا توجد إعدادات تطبيق نشطة")
        return False
    
    # التحقق من وجود المفاتيح
    if not app_settings.aws_access_key or not app_settings.aws_secret_key:
        logger.error("مفاتيح AWS غير موجودة في إعدادات التطبيق")
        return False
    
    # طباعة معلومات المفاتيح (بدون كشف المفتاح الكامل)
    logger.info(f"AWS Access Key: {app_settings.aws_access_key[:5]}...{app_settings.aws_access_key[-3:]}")
    logger.info(f"AWS Secret Key Length: {len(app_settings.aws_secret_key)}")
    
    try:
        # استيراد boto3
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            logger.info(f"تم استيراد boto3 بنجاح (الإصدار: {boto3.__version__})")
        except ImportError:
            logger.error("فشل استيراد boto3. تأكد من تثبيته باستخدام: pip install boto3")
            return False
        
        # اختبار 1: استخدام المفاتيح الصحيحة
        logger.info("اختبار 1: استخدام المفاتيح الصحيحة...")
        try:
            # إنشاء عميل STS (Secure Token Service) للتحقق من المفاتيح
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=app_settings.aws_access_key,
                aws_secret_access_key=app_settings.aws_secret_key,
                region_name='us-east-1'  # استخدام منطقة افتراضية
            )
            
            # محاولة الحصول على معلومات الحساب
            response = sts_client.get_caller_identity()
            account_id = response.get('Account', 'غير معروف')
            logger.info(f"اختبار 1 نجح! معرف الحساب: {account_id}")
            logger.info(f"تفاصيل الاستجابة: {response}")
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"اختبار 1 فشل: {str(e)}")
            return False
        
        # اختبار 2: استخدام مفتاح وصول غير صالح
        logger.info("اختبار 2: استخدام مفتاح وصول غير صالح...")
        try:
            # إنشاء عميل STS مع مفتاح وصول غير صالح
            invalid_access_key = app_settings.aws_access_key + "_test"
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=invalid_access_key,
                aws_secret_access_key=app_settings.aws_secret_key,
                region_name='us-east-1'
            )
            
            # محاولة الحصول على معلومات الحساب
            response = sts_client.get_caller_identity()
            logger.warning("اختبار 2 نجح بشكل غير متوقع! هذا يعني أن المفتاح غير الصالح تم قبوله.")
            return False
        except (ClientError, NoCredentialsError) as e:
            logger.info(f"اختبار 2 نجح (كما هو متوقع): {str(e)}")
        
        # اختبار 3: استخدام مفتاح سري غير صالح
        logger.info("اختبار 3: استخدام مفتاح سري غير صالح...")
        try:
            # إنشاء عميل STS مع مفتاح سري غير صالح
            invalid_secret_key = app_settings.aws_secret_key + "_test"
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=app_settings.aws_access_key,
                aws_secret_access_key=invalid_secret_key,
                region_name='us-east-1'
            )
            
            # محاولة الحصول على معلومات الحساب
            response = sts_client.get_caller_identity()
            logger.warning("اختبار 3 نجح بشكل غير متوقع! هذا يعني أن المفتاح السري غير الصالح تم قبوله.")
            return False
        except (ClientError, NoCredentialsError) as e:
            logger.info(f"اختبار 3 نجح (كما هو متوقع): {str(e)}")
        
        logger.info("جميع الاختبارات نجحت! مفاتيح AWS صالحة وتعمل كما هو متوقع.")
        return True
        
    except Exception as e:
        logger.error(f"خطأ غير متوقع أثناء اختبار مفاتيح AWS: {str(e)}")
        return False

def check_aws_credentials_files():
    """
    التحقق من وجود ملفات اعتماد AWS في المسارات المعتادة
    """
    logger.info("البحث عن ملفات اعتماد AWS...")
    
    # المسارات المحتملة لملفات الاعتماد
    home_dir = Path.home()
    aws_dir = home_dir / ".aws"
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    # التحقق من وجود مجلد .aws
    if aws_dir.exists():
        logger.info(f"تم العثور على مجلد .aws: {aws_dir}")
        
        # التحقق من ملف credentials
        if credentials_file.exists():
            logger.info(f"تم العثور على ملف credentials: {credentials_file}")
            # عرض محتوى الملف (مع إخفاء المفاتيح)
            try:
                with open(credentials_file, 'r') as f:
                    content = f.read()
                    # إخفاء المفاتيح الحساسة
                    import re
                    content = re.sub(r'(aws_access_key_id\s*=\s*)([^\s]+)', r'\1XXXXX', content)
                    content = re.sub(r'(aws_secret_access_key\s*=\s*)([^\s]+)', r'\1XXXXX', content)
                    logger.info(f"محتوى ملف credentials (مع إخفاء المفاتيح):\n{content}")
            except Exception as e:
                logger.error(f"فشل قراءة ملف credentials: {str(e)}")
        else:
            logger.info("لم يتم العثور على ملف credentials")
        
        # التحقق من ملف config
        if config_file.exists():
            logger.info(f"تم العثور على ملف config: {config_file}")
        else:
            logger.info("لم يتم العثور على ملف config")
    else:
        logger.info("لم يتم العثور على مجلد .aws")
    
    # التحقق من متغيرات البيئة
    aws_env_vars = {
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "AWS_SESSION_TOKEN": os.environ.get("AWS_SESSION_TOKEN"),
        "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
        "SP_API_AWS_ACCESS_KEY": os.environ.get("SP_API_AWS_ACCESS_KEY"),
        "SP_API_AWS_SECRET_KEY": os.environ.get("SP_API_AWS_SECRET_KEY"),
    }
    
    logger.info("متغيرات البيئة المتعلقة بـ AWS:")
    for var, value in aws_env_vars.items():
        if value:
            # إخفاء المفاتيح الحساسة
            if "KEY" in var or "SECRET" in var:
                masked_value = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "XXX"
                logger.info(f"{var}: {masked_value}")
            else:
                logger.info(f"{var}: {value}")
        else:
            logger.info(f"{var}: غير موجود")

if __name__ == "__main__":
    logger.info("بدء برنامج اختبار مفاتيح AWS")
    
    # التحقق من ملفات الاعتماد أولاً
    check_aws_credentials_files()
    
    # اختبار المفاتيح
    if test_aws_keys():
        logger.info("اختبار مفاتيح AWS نجح!")
        print("✅ مفاتيح AWS صالحة وتعمل بشكل صحيح.")
        sys.exit(0)
    else:
        logger.error("اختبار مفاتيح AWS فشل!")
        print("❌ هناك مشكلة في مفاتيح AWS. راجع السجلات للحصول على مزيد من التفاصيل.")
        sys.exit(1) 