"""
URL configuration for fbm_sync_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventory.views import dashboard
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # صفحة لوحة التحكم الرئيسية
    path('dashboard/', dashboard, name='dashboard'),
    
    # الصفحة الرئيسية
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # صفحات الشروط والخصوصية
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    
    # صفحة اختبار الإشعارات
    path('notification-test/', TemplateView.as_view(template_name='notification_test.html'), name='notification_test'),
    
    # روابط تطبيق المخزون
    path('inventory/', include('inventory.urls')),
    
    # روابط تطبيق تكامل أمازون
    path('amazon/', include('amazon_integration.urls')),
    
    # روابط المصادقة
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] 