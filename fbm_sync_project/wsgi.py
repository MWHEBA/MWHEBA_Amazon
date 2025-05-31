"""
WSGI config for fbm_sync_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# أضف مسار المشروع إلى مسارات النظام
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# تحميل متغيرات البيئة من ملف .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    # تجاهل الأخطاء إذا لم يتم العثور على مكتبة dotenv
    pass
except Exception:
    # تجاهل الأخطاء إذا لم يتم العثور على ملف .env
    pass

# تفعيل PyMySQL كبديل لـ MySQLdb في بيئة الإنتاج
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    # تجاهل الأخطاء إذا لم يتم العثور على مكتبة pymysql
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbm_sync_project.settings')

application = get_wsgi_application() 