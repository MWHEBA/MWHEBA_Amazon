from django.db import models

class AmazonSettings(models.Model):
    """
    نموذج لتخزين إعدادات الاتصال بـ Amazon SP-API
    """
    aws_access_key = models.CharField(max_length=255, verbose_name="AWS Access Key")
    aws_secret_key = models.CharField(max_length=255, verbose_name="AWS Secret Key")
    role_arn = models.CharField(max_length=255, verbose_name="Role ARN")
    lwa_client_id = models.CharField(max_length=255, verbose_name="LWA Client ID")
    lwa_client_secret = models.CharField(max_length=255, verbose_name="LWA Client Secret")
    refresh_token = models.CharField(max_length=1000, verbose_name="Refresh Token")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    def __str__(self):
        return f"Amazon Settings (Last Updated: {self.updated_at})"
    
    def save(self, *args, **kwargs):
        """
        ضمان وجود سجل واحد فقط للإعدادات
        """
        if not self.pk and AmazonSettings.objects.exists():
            # إذا كان هناك سجل موجود بالفعل، قم بتحديثه بدلاً من إنشاء سجل جديد
            existing = AmazonSettings.objects.first()
            self.pk = existing.pk
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "إعدادات أمازون"
        verbose_name_plural = "إعدادات أمازون" 