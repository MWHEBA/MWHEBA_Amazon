from django.db import models

class AmazonSettings(models.Model):
    """
    نموذج لتخزين إعدادات الاتصال بـ Amazon SP-API
    """
    MARKETPLACE_CHOICES = [
        ('A1AM78C64UM0Y8', 'مصر'),
        ('A2VIGQ35RCS4UG', 'السعودية'),
        ('A2NGVSA5CAHHU9', 'الإمارات'),
    ]
    
    refresh_token = models.CharField(max_length=1000, verbose_name="Refresh Token")
    marketplace_id = models.CharField(max_length=50, verbose_name="سوق أمازون", choices=MARKETPLACE_CHOICES, default="A1AM78C64UM0Y8")  # مصر افتراضيًا
    location_id = models.CharField(max_length=100, verbose_name="رقم موقع FBM", blank=True, null=True, help_text="رقم موقع FBM الذي تقدمه أمازون")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    def __str__(self):
        return f"إعدادات أمازون ({self.get_marketplace_id_display()})"
    
    class Meta:
        verbose_name = "إعدادات أمازون"
        verbose_name_plural = "إعدادات أمازون"

class AppSettings(models.Model):
    """
    نموذج لتخزين إعدادات التطبيق الثابتة
    """
    aws_access_key = models.CharField(max_length=255, verbose_name="AWS Access Key")
    aws_secret_key = models.CharField(max_length=255, verbose_name="AWS Secret Key")
    role_arn = models.CharField(max_length=255, verbose_name="Role ARN")
    lwa_client_id = models.CharField(max_length=255, verbose_name="LWA Client ID")
    lwa_client_secret = models.CharField(max_length=255, verbose_name="LWA Client Secret")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    def __str__(self):
        return "إعدادات التطبيق"
    
    class Meta:
        verbose_name = "إعدادات التطبيق"
        verbose_name_plural = "إعدادات التطبيق"
        
    def save(self, *args, **kwargs):
        """
        ضمان وجود إعدادات نشطة واحدة فقط
        """
        if self.is_active:
            # إذا كان هناك إعدادات نشطة أخرى، نجعلها غير نشطة
            AppSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs) 