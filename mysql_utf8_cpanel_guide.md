# دليل إصلاح مشكلة الترميز العربي في MySQL

هذا الدليل يوضح كيفية إصلاح مشكلة ترميز الحروف العربية (`Incorrect string value: '\xD9\x85\xD9\x86\xD8\xAA...'`) في بيئة الإنتاج.

## خطة التنفيذ

### 1. عمل نسخة احتياطية من قاعدة البيانات

```bash
# عبر SSH على الخادم
mysqldump -u USERNAME -p DATABASE_NAME > backup_before_charset_fix.sql
```

أو عبر cPanel:
1. انتقل إلى phpMyAdmin
2. اختر قاعدة البيانات
3. انقر على "Export"
4. اختر "Quick" واضغط "Go"

### 2. استخدام الأداة المتكاملة لتحويل قاعدة البيانات

السكريبت `fix_charset_script.py` يقوم بفحص وتحويل كامل قاعدة البيانات والجداول والأعمدة لدعم اللغة العربية (UTF-8MB4):

```bash
# الاتصال بالخادم عبر SSH
cd /path/to/your/project
python fix_charset_script.py
```

### 3. فحص إعدادات الترميز

بعد تنفيذ السكريبت، استخدم `check_mysql_charset.py` للتأكد من تطبيق جميع التغييرات بنجاح:

```bash
python check_mysql_charset.py
```

## تغيير ترميز قاعدة البيانات يدوياً (في حالة تعذر استخدام السكريبت)

### 1. تحويل قاعدة البيانات

1. قم بتسجيل الدخول إلى حساب cPanel الخاص بك
2. انتقل إلى قسم "Databases" واختر "phpMyAdmin"
3. اختر قاعدة البيانات من القائمة الجانبية
4. انقر على علامة التبويب "Operations"
5. ابحث عن قسم "Collation" وحدد `utf8mb4_unicode_ci` من القائمة المنسدلة
6. اضغط على زر "Go" لتطبيق التغييرات

### 2. تحويل الجداول

لكل جدول في قاعدة البيانات:

1. اختر الجدول من القائمة الجانبية
2. انقر على علامة التبويب "Operations"
3. ابحث عن قسم "Table options" ثم "Collation" واختر `utf8mb4_unicode_ci`
4. اضغط على زر "Go" لتطبيق التغييرات

### 3. تحويل الأعمدة

لكل عمود نصي في كل جدول:

1. اختر الجدول من القائمة الجانبية
2. انقر على علامة التبويب "Structure"
3. ابحث عن العمود الذي تريد تغييره وانقر على رمز "Change"
4. في القسم "Collation"، اختر `utf8mb4_unicode_ci`
5. اضغط على زر "Save" لتطبيق التغييرات

## في حالة استمرار المشكلة: إنشاء قاعدة بيانات جديدة

إذا استمرت المشكلة بعد تنفيذ الخطوات السابقة، يمكنك إنشاء قاعدة بيانات جديدة:

1. قم بتسجيل الدخول إلى حساب cPanel
2. انتقل إلى قسم "Databases" واختر "MySQL Databases"
3. أنشئ قاعدة بيانات جديدة
4. انتقل إلى phpMyAdmin
5. اختر قاعدة البيانات الجديدة
6. نفذ الأمر التالي لضبط الترميز:
   ```sql
   ALTER DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
7. عدّل ملف `.env` بمعلومات قاعدة البيانات الجديدة
8. قم بتنفيذ الترحيلات:
   ```bash
   python manage.py migrate
   ```

## تأكد من إعدادات Django الصحيحة

تأكد من أن ملف `settings.py` يحتوي على إعدادات الترميز الصحيحة:

```python
DATABASES = {
    'default': {
        # ... إعدادات أخرى
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
        },
    }
}
```

## إعادة تشغيل التطبيق

بعد تنفيذ التغييرات، قم بإعادة تشغيل التطبيق:

```bash
# في حالة استخدام Passenger (cPanel)
touch /path/to/your/project/tmp/restart.txt
```

## اختبار النجاح

للتأكد من أن المشكلة قد تم حلها:

1. حاول إنشاء سجل جديد يحتوي على نص عربي
2. تأكد من أنه يتم حفظه وعرضه بشكل صحيح
3. تأكد من أن صفحات التطبيق تعرض النصوص العربية بشكل صحيح 