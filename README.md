# MWHEBA Amazon FBM Sync

<p align="center">
  <img src="https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Amazon_SP--API-1.9.33-FF9900?style=for-the-badge&logo=amazon&logoColor=white" alt="Amazon SP-API" />
</p>

نظام متكامل لمزامنة المخزون مع أمازون FBM (Fulfilled By Merchant) باستخدام Amazon SP-API.

## 🌟 المميزات الرئيسية

- ✅ إدارة مخزون المنتجات بشكل متكامل
- ✅ تكامل مباشر مع Amazon SP-API
- ✅ مزامنة تلقائية للمخزون مع أمازون
- ✅ دعم كامل للغة العربية في واجهة المستخدم وقاعدة البيانات
- ✅ واجهة مستخدم سهلة الاستخدام

## 📋 متطلبات النظام

- Python 3.9+
- Django 4.2+
- python-amazon-sp-api 1.9.33+
- PyMySQL 1.1.0+ (لبيئة الإنتاج)
- boto3 1.34.40+ (لاختبار مفاتيح AWS)

## 🚀 التثبيت والإعداد

### 1. استنساخ المشروع

```bash
git clone https://github.com/mwheba/MWHEBA_Amazon.git
cd MWHEBA_Amazon
```

### 2. إنشاء بيئة افتراضية وتفعيلها

```bash
python -m venv venv

# في Windows
venv\Scripts\activate

# في Linux/Mac
source venv/bin/activate
```

### 3. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 4. إعداد المتغيرات البيئية

قم بإنشاء ملف `.env` في المجلد الرئيسي للمشروع وأضف المتغيرات التالية:

```
DEBUG=True
SECRET_KEY=your-secret-key

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///db.sqlite3
# أو لـ MySQL
# DATABASE_URL=mysql://username:password@host:port/database_name

# إعدادات Amazon SP-API
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
ROLE_ARN=your-role-arn
LWA_CLIENT_ID=your-lwa-client-id
LWA_CLIENT_SECRET=your-lwa-client-secret
REFRESH_TOKEN=your-refresh-token
```

### 5. إجراء الترحيلات وإنشاء مستخدم مسؤول

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. تشغيل الخادم المحلي

```bash
python manage.py runserver
```

## 🏗️ هيكل المشروع

```
MWHEBA_Amazon/
├── amazon_integration/  # تطبيق تكامل أمازون
├── fbm_sync_project/    # إعدادات المشروع
├── inventory/           # تطبيق المخزون
├── static/              # الملفات الثابتة
│   ├── css/
│   ├── js/
│   ├── img/
│   └── scss/
├── templates/           # قوالب HTML
│   ├── amazon_integration/
│   ├── inventory/
│   └── registration/
├── .env                 # ملف المتغيرات البيئية
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## 🔄 مزامنة المخزون مع Amazon SP-API

### الإعدادات المطلوبة

1. **إعدادات التطبيق**:
   - AWS Access Key
   - AWS Secret Key
   - Role ARN
   - LWA Client ID
   - LWA Client Secret

2. **إعدادات أمازون**:
   - Refresh Token
   - معرف السوق (Marketplace ID)
   - رقم موقع FBM (Location ID)

### خطوات المزامنة

1. قم بإعداد بيانات الاتصال في صفحة الإعدادات
2. انتقل إلى صفحة مزامنة المنتجات: `/amazon/sync-products/`
3. اضغط على زر "مزامنة المنتجات" لبدء عملية المزامنة

### ميزات المزامنة

- **مزامنة آمنة** - التعامل مع أخطاء الاتصال والـ Rate Limits
- **مزامنة في الخلفية** - تنفيذ المزامنة بدون تعطيل واجهة المستخدم
- **معالجة الأخطاء** - التعامل مع أخطاء التوثيق وحدود الطلبات
- **التحقق من النجاح** - التأكد من نجاح عملية تحديث الكميات

## 🔧 إعداد بيئة الإنتاج

### استخدام PyMySQL مع MySQL

تم تكوين PyMySQL كبديل لـ MySQLdb في بيئات الإنتاج، خاصة في استضافة cPanel:

```python
try:
    import pymysql
    pymysql.version_info = (1, 4, 6, 'final', 0)
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

### دعم اللغة العربية في MySQL

#### إنشاء قاعدة بيانات بترميز UTF-8

```sql
CREATE DATABASE mwheba_fbm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### تكوين Django لدعم UTF-8

في ملف `settings.py`:

```python
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
        },
    }
}
```

#### إصلاح مشاكل الترميز

استخدم السكريبتات المرفقة:

```bash
python fix_charset_script.py
python check_mysql_charset.py
```

## 🧪 اختبار النظام

### اختبار مزامنة المخزون

```bash
python test_inventory_sync.py
```

### اختبار مفاتيح AWS

```bash
python test_aws_keys.py
```

### اختبار مفاتيح LWA

```bash
python test_lwa_client.py
```

## 📱 روابط النظام

- الصفحة الرئيسية: `/`
- تسجيل الدخول: `/login/`
- لوحة التحكم: `/dashboard/`
- إدارة المخزون: `/inventory/`
- تكامل أمازون: `/amazon/`

## 📄 الترخيص

جميع الحقوق محفوظة © MWHEBA 2024 