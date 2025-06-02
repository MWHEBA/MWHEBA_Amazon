from django.apps import AppConfig
import os

# متغير عام لتتبع ما إذا تم تحميل الإعدادات
_settings_loaded = False
# متغير لتتبع ما إذا تم طباعة رسالة التهيئة
_init_message_printed = False

class AmazonIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amazon_integration'
    verbose_name = 'تكامل أمازون'

    def ready(self):
        """
        تنفيذ الكود عند اكتمال تهيئة التطبيق
        """
        # تجنب تنفيذ هذا الكود عند تشغيل أوامر الإدارة
        import sys
        if 'runserver' not in sys.argv and 'runserver_plus' not in sys.argv:
            return
            
        # تجنب تحميل الإعدادات مرتين
        global _settings_loaded
        if _settings_loaded:
            return
            
        # تحميل الإعدادات من قاعدة البيانات
        # استدعاء الدالة مباشرة من ملف settings.py
        from fbm_sync_project.settings import load_settings_from_database
        load_settings_from_database()
        _settings_loaded = True 