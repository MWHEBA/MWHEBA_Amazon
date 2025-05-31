from django.urls import path
from . import views

urlpatterns = [
    path('import/', views.import_products, name='import_products'),
    path('sync/', views.sync_all_products, name='sync_all_products'),
    path('settings/', views.amazon_settings, name='amazon_settings'),
    path('test-connection/', views.test_amazon_connection, name='test_amazon_connection'),
    path('auth/callback/', views.auth_callback, name='amazon_auth_callback'),
] 