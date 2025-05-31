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