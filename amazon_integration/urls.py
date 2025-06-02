from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.amazon_settings, name='amazon_settings'),
    path('app-settings/', views.app_settings, name='app_settings'),
    path('test-connection/', views.test_amazon_connection, name='test_amazon_connection'),
    path('import-products/', views.import_products, name='import_products'),
    path('sync-products/', views.sync_all_products, name='sync_all_products'),
    path('sync-status/', views.sync_status, name='sync_status'),
    path('auth-callback/', views.auth_callback, name='auth_callback'),
] 