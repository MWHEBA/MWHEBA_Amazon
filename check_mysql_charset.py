#!/usr/bin/env python
"""
سكريبت للتحقق من إعدادات الترميز في قاعدة بيانات MySQL
يستخدم هذا السكريبت للتأكد من أن قاعدة البيانات والجداول والأعمدة تستخدم UTF-8MB4
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

def check_database_charset():
    """التحقق من إعدادات ترميز قاعدة البيانات"""
    db_name = settings.DATABASES['default']['NAME']
    
    print(f"\n=== فحص إعدادات الترميز في قاعدة البيانات {db_name} ===\n")
    
    # التحقق من إعدادات قاعدة البيانات
    db_charset = execute_sql("""
        SELECT default_character_set_name, default_collation_name
        FROM information_schema.SCHEMATA
        WHERE schema_name = %s
    """, [db_name])
    
    if not db_charset:
        print(f"لم يتم العثور على قاعدة البيانات {db_name}")
        return
        
    print(f"ترميز قاعدة البيانات: {db_charset[0][0]}")
    print(f"نظام المقارنة (Collation): {db_charset[0][1]}")
    
    # التحقق من متغيرات الجلسة
    session_vars = execute_sql("""
        SHOW VARIABLES 
        WHERE Variable_name LIKE 'character_set%' OR Variable_name LIKE 'collation%'
    """)
    
    print("\n=== إعدادات الترميز الحالية للجلسة ===")
    for var in session_vars:
        print(f"{var[0]}: {var[1]}")
    
    # التحقق من ترميز الجداول
    tables = execute_sql("SHOW TABLES")
    
    print("\n=== ترميز الجداول ===")
    for table in tables:
        table_name = table[0]
        table_info = execute_sql("""
            SELECT table_name, table_collation
            FROM information_schema.TABLES
            WHERE table_schema = %s AND table_name = %s
        """, [db_name, table_name])
        
        if table_info:
            print(f"الجدول {table_name}: {table_info[0][1]}")
    
    # فحص كل جدول بشكل مفصل
    print("\n=== الأعمدة النصية التي لا تستخدم UTF-8MB4 ===")
    has_non_utf8mb4 = False
    
    for table in tables:
        table_name = table[0]
        try:
            columns = execute_sql("""
                SELECT column_name, character_set_name, collation_name, data_type
                FROM information_schema.COLUMNS
                WHERE table_schema = %s AND table_name = %s
                AND data_type IN ('varchar', 'char', 'text', 'mediumtext', 'longtext', 'enum', 'set')
                AND (character_set_name != 'utf8mb4' OR collation_name NOT LIKE 'utf8mb4%')
            """, [db_name, table_name])
            
            if columns:
                has_non_utf8mb4 = True
                for col in columns:
                    print(f"الجدول {table_name}, العمود {col[0]}, النوع {col[3]}, الترميز {col[1] or 'غير محدد'}, نظام المقارنة {col[2] or 'غير محدد'}")
        except Exception as e:
            print(f"خطأ عند فحص الجدول {table_name}: {e}")
    
    if not has_non_utf8mb4:
        print("لا توجد أعمدة نصية تستخدم ترميزًا غير UTF-8MB4")
    
    print("\n=== نتيجة الفحص ===")
    if db_charset[0][0] != 'utf8mb4' or not db_charset[0][1].startswith('utf8mb4'):
        print("❌ قاعدة البيانات لا تستخدم ترميز UTF-8MB4")
    elif has_non_utf8mb4:
        print("⚠️ بعض الأعمدة لا تستخدم ترميز UTF-8MB4")
    else:
        print("✅ كل شيء يستخدم ترميز UTF-8MB4")

if __name__ == "__main__":
    try:
        check_database_charset()
    except Exception as e:
        print(f"حدث خطأ: {e}") 