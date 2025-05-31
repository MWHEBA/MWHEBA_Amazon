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