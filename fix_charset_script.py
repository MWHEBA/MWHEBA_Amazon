#!/usr/bin/env python
"""
سكريبت لتحويل قاعدة البيانات MySQL إلى UTF-8MB4 لدعم اللغة العربية
يجب تشغيل هذا السكريبت على الخادم بعد تنفيذ أوامر الهجرة الأولية
"""

import os
import sys
import django
import pymysql

# إضافة مسار المشروع للـ sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# تهيئة Django للوصول لإعدادات قاعدة البيانات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbm_sync_project.settings')
django.setup()

from django.conf import settings
from django.db import connection

def execute_sql(sql, params=None):
    """تنفيذ استعلام SQL مباشرة على قاعدة البيانات"""
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()

def convert_database_to_utf8mb4():
    """تحويل قاعدة البيانات بالكامل إلى UTF-8MB4"""
    # الحصول على اسم قاعدة البيانات من إعدادات Django
    db_name = settings.DATABASES['default']['NAME']
    
    print(f"تحويل قاعدة البيانات {db_name} إلى UTF-8MB4...")
    
    # تحويل قاعدة البيانات نفسها
    execute_sql(f"ALTER DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    # الحصول على قائمة الجداول
    tables = execute_sql("SHOW TABLES")
    
    # تحويل كل جدول
    for table in tables:
        table_name = table[0]
        print(f"تحويل الجدول {table_name}...")
        
        # تحويل الجدول
        execute_sql(f"ALTER TABLE `{table_name}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # الحصول على قائمة الأعمدة
        columns = execute_sql(f"SHOW FULL COLUMNS FROM `{table_name}`")
        
        # تحويل الأعمدة النصية
        for column in columns:
            column_name = column[0]
            column_type = column[1]
            if any(text_type in column_type.lower() for text_type in ['varchar', 'char', 'text', 'enum']):
                # استخراج الحجم من نوع العمود إذا كان varchar أو char
                size = None
                if 'varchar' in column_type.lower() or 'char' in column_type.lower():
                    size = column_type.split('(')[1].split(')')[0]
                
                is_nullable = column[3] == 'YES'
                null_statement = '' if is_nullable else ' NOT NULL'
                
                # بناء الاستعلام بناءً على نوع العمود
                if size:
                    sql = f"ALTER TABLE `{table_name}` MODIFY `{column_name}` {column_type.split('(')[0]}({size}) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci{null_statement}"
                else:
                    sql = f"ALTER TABLE `{table_name}` MODIFY `{column_name}` {column_type} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci{null_statement}"
                
                print(f"  تحويل العمود {column_name}...")
                try:
                    execute_sql(sql)
                except Exception as e:
                    print(f"  خطأ في تحويل العمود {column_name}: {e}")
    
    print("تم تحويل قاعدة البيانات بنجاح إلى UTF-8MB4.")

if __name__ == "__main__":
    try:
        convert_database_to_utf8mb4()
    except Exception as e:
        print(f"حدث خطأ: {e}") 