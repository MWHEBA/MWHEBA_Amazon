import os
import sys
from pathlib import Path

# أضف مسار المشروع إلى مسارات النظام
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

# إعداد المتغيرات البيئية
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbm_sync_project.settings')

# تحميل متغيرات البيئة من ملف .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(CURRENT_DIR, '.env'))
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

# استدعاء تطبيق WSGI للجانجو
from fbm_sync_project.wsgi import application 