# FBM Sync Project

مشروع لمزامنة المخزون مع أمازون FBM (Fulfilled By Merchant).

## المميزات

- إدارة المخزون
- تكامل مع Amazon SP-API
- مزامنة المخزون مع أمازون

## متطلبات التشغيل

- Python 3.9+
- Django 4.2+
- python-amazon-sp-api
- PyMySQL (لبيئة الإنتاج)

## التثبيت

1. استنساخ المشروع:
```bash
git clone <repository-url>
cd fbm_sync_project
```

2. إنشاء بيئة افتراضية وتفعيلها:
```bash
python -m venv venv
# في Windows
venv\Scripts\activate
# في Linux/Mac
source venv/bin/activate
```

3. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

4. إنشاء ملف `.env` وتعبئة المتغيرات البيئية المطلوبة:
```
DEBUG=True
SECRET_KEY=your-secret-key

# Amazon SP-API Settings
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
ROLE_ARN=your-role-arn
LWA_CLIENT_ID=your-lwa-client-id
LWA_CLIENT_SECRET=your-lwa-client-secret
REFRESH_TOKEN=your-refresh-token
```

5. تنفيذ الترحيلات:
```bash
python manage.py migrate
```

6. إنشاء مستخدم مسؤول:
```bash
python manage.py createsuperuser
```

7. تشغيل الخادم المحلي:
```bash
python manage.py runserver
```

## إعداد بيئة الإنتاج

### تفعيل PyMySQL

تم تفعيل PyMySQL كبديل لـ MySQLdb في بيئة الإنتاج لاستخدامه مع قواعد بيانات MySQL. هذا مفيد بشكل خاص في بيئات استضافة cPanel حيث قد يكون من الصعب تثبيت MySQLdb.

PyMySQL تم تكوينه في الملفات التالية:
1. ملف `fbm_sync_project/__init__.py` (الموقع الرئيسي)
2. ملف `fbm_sync_project/wsgi.py`
3. ملف `passenger_wsgi.py`

التكوين يتم باستخدام الكود التالي:
```python
try:
    import pymysql
    pymysql.version_info = (1, 4, 6, 'final', 0)  # تغيير رقم الإصدار لتفادي مشاكل التوافق
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

تأكد من أن PyMySQL مثبت في بيئة الإنتاج باستخدام:
```bash
pip install PyMySQL==1.1.0
```
أو عن طريق تثبيت جميع المتطلبات:
```bash
pip install -r requirements.txt
```

### ملاحظة هامة
في بيئة الإنتاج، يجب تنفيذ الكود الخاص بتفعيل PyMySQL قبل استيراد أي كود من Django، وهذا هو السبب وراء وضعه في ملف `__init__.py` للمشروع.

### إعداد قاعدة بيانات MySQL لدعم اللغة العربية

لدعم اللغة العربية بشكل صحيح في قاعدة بيانات MySQL، يجب إعداد قاعدة البيانات والجداول لاستخدام ترميز UTF-8. تم تكوين الاتصال بقاعدة البيانات في ملف `settings.py` لاستخدام ترميز `utf8mb4`.

#### إنشاء قاعدة بيانات جديدة بترميز UTF-8
```sql
CREATE DATABASE mwheba_fbm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### تحويل قاعدة بيانات موجودة إلى UTF-8
يمكنك استخدام ملف `convert_db_to_utf8mb4.sql` الموجود في المشروع لتحويل قاعدة بيانات موجودة إلى ترميز UTF-8:
```bash
# في cPanel phpMyAdmin، قم باستيراد ملف convert_db_to_utf8mb4.sql

# أو من سطر الأوامر
mysql -u username -p mwheba_fbm < convert_db_to_utf8mb4.sql
```

## إصلاح مشكلة الترميز العربي في MySQL

عند استخدام قاعدة بيانات MySQL مع المحتوى العربي، قد تواجه خطأ:
```
Incorrect string value: '\xD9\x85\xD9\x86\xD8\xAA...' for column...
```

هذا بسبب إعدادات الترميز الافتراضية في MySQL التي لا تدعم Unicode بشكل كامل. 

### الحل المتكامل

تم توفير سكريبتات خاصة لإصلاح هذه المشكلة:

1. `fix_charset_script.py` - لتحويل قاعدة البيانات بالكامل إلى UTF-8MB4
2. `check_mysql_charset.py` - للتحقق من إعدادات الترميز في قاعدة البيانات

استخدم السكريبت الأول لإصلاح المشكلة:

```bash
python fix_charset_script.py
```

ثم تحقق من نجاح العملية باستخدام:

```bash
python check_mysql_charset.py
```

للحصول على تعليمات مفصلة، راجع الملف `mysql_utf8_cpanel_guide.md` في المشروع.

### تكوين Django الصحيح

تأكد من وجود هذه الإعدادات في `settings.py`:

```python
'OPTIONS': {
    'charset': 'utf8mb4',
    'use_unicode': True,
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES', character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
},
```

## هيكل المشروع

```
MWHEBA_Amazon/
├── amazon_integration/  # تطبيق تكامل أمازون
├── fbm_sync_project/    # إعدادات المشروع
├── inventory/           # تطبيق المخزون
├── static/              # الملفات الثابتة
│   ├── css/
│   ├── js/
│   └── img/
├── templates/           # قوالب HTML
│   ├── amazon_integration/
│   ├── inventory/
│   └── registration/
├── venv/                # البيئة الافتراضية
├── .env                 # ملف المتغيرات البيئية
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## الاستخدام

1. الصفحة الرئيسية: `http://localhost:8000/`
2. تسجيل الدخول: `http://localhost:8000/login/`
3. لوحة التحكم: `http://localhost:8000/dashboard/`
4. إدارة المخزون: `http://localhost:8000/inventory/`
5. تكامل أمازون: `http://localhost:8000/amazon/`
6. الشروط والأحكام: `http://localhost:8000/terms/`
7. سياسة الخصوصية: `http://localhost:8000/privacy/` 