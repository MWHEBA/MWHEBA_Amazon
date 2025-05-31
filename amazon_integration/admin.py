from django.contrib import admin
# في الوقت الحالي، لا يوجد نماذج خاصة بتطبيق amazon_integration للتسجيل في لوحة الإدارة
# سيتم إضافة النماذج هنا في المرحلة الثانية من المشروع 
from .models import AmazonSettings

@admin.register(AmazonSettings)
class AmazonSettingsAdmin(admin.ModelAdmin):
    """
    إدارة إعدادات الاتصال بأمازون
    """
    list_display = ('__str__', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # منع إضافة أكثر من سجل واحد
        return not AmazonSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # منع حذف السجل الوحيد
        return False 