from django.contrib import admin
# في الوقت الحالي، لا يوجد نماذج خاصة بتطبيق amazon_integration للتسجيل في لوحة الإدارة
# سيتم إضافة النماذج هنا في المرحلة الثانية من المشروع 
from .models import AmazonSettings, AppSettings

@admin.register(AmazonSettings)
class AmazonSettingsAdmin(admin.ModelAdmin):
    """
    إدارة إعدادات الاتصال بأمازون
    """
    list_display = ('id', 'get_marketplace_display', 'is_active', 'updated_at')
    list_filter = ('is_active', 'marketplace_id')
    search_fields = ('marketplace_id',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('إعدادات السوق', {
            'fields': ('marketplace_id', 'is_active')
        }),
        ('بيانات اعتماد التاجر', {
            'fields': ('refresh_token',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_marketplace_display(self, obj):
        return obj.get_marketplace_id_display()
    
    get_marketplace_display.short_description = "سوق أمازون"

@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # التحقق من وجود سجل بالفعل
        return AppSettings.objects.count() < 1 