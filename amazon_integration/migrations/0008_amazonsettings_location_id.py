# Generated by Django 4.2.21 on 2025-06-01 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amazon_integration', '0007_appsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='amazonsettings',
            name='location_id',
            field=models.CharField(blank=True, help_text='رقم موقع FBM الذي تقدمه أمازون', max_length=100, null=True, verbose_name='رقم موقع FBM'),
        ),
    ]
