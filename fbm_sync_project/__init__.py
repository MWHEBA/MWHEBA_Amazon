"""
تهيئة المشروع
"""

# تفعيل PyMySQL كبديل لـ MySQLdb قبل استيراد Django
try:
    import pymysql
    pymysql.version_info = (1, 4, 6, 'final', 0)  # تغيير رقم الإصدار لتفادي مشاكل التوافق
    pymysql.install_as_MySQLdb()
except ImportError:
    # تجاهل الأخطاء إذا لم يتم العثور على مكتبة pymysql
    pass 