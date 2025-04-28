# دليل نشر نظام "نُظم" على Google Cloud

هذا الدليل يشرح خطوات نشر نظام "نُظم" على منصات Google Cloud المختلفة.

## الخيار الأول: النشر على Google Cloud Run (موصى به)

### المتطلبات المسبقة

1. حساب Google Cloud Platform (GCP)
2. تثبيت Google Cloud SDK على جهازك
3. قاعدة بيانات PostgreSQL (يمكن استخدام خدمة Cloud SQL من Google)

### خطوات النشر

1. **تسجيل الدخول إلى Google Cloud:**

```bash
gcloud auth login
```

2. **إنشاء مشروع جديد أو اختيار مشروع موجود:**

```bash
gcloud projects create YOUR_PROJECT_ID --name="نظام نُظم"
gcloud config set project YOUR_PROJECT_ID
```

3. **تمكين الواجهات البرمجية المطلوبة:**

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

4. **بناء حاوية Docker ونشرها:**

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/nozom-system
```

5. **نشر الحاوية على Cloud Run:**

```bash
gcloud run deploy nozom-system \
  --image gcr.io/YOUR_PROJECT_ID/nozom-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://user:password@host:port/database,FIREBASE_API_KEY=your_api_key,FIREBASE_PROJECT_ID=your_project_id,FIREBASE_APP_ID=your_app_id"
```

## الخيار الثاني: النشر على Google App Engine

### خطوات النشر

1. **تمكين خدمة App Engine:**

```bash
gcloud app create --region=us-central
```

2. **تعديل ملف app.yaml حسب الحاجة**

3. **نشر التطبيق:**

```bash
gcloud app deploy
```

## الخيار الثالث: استخدام Firebase Hosting + Cloud Functions (للواجهة الأمامية فقط)

هذا الخيار مناسب فقط لواجهة المستخدم الأمامية، ويتطلب إعادة هيكلة التطبيق ليكون API منفصل.

### خطوات النشر

1. **تسجيل الدخول إلى Firebase:**

```bash
firebase login
```

2. **تهيئة المشروع:**

```bash
firebase init
```

3. **نشر التطبيق:**

```bash
firebase deploy
```

## إعداد قاعدة البيانات على Cloud SQL

1. **إنشاء مثيل PostgreSQL:**

```bash
gcloud sql instances create nozom-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. **إنشاء قاعدة بيانات:**

```bash
gcloud sql databases create nozom_database --instance=nozom-db
```

3. **إنشاء مستخدم:**

```bash
gcloud sql users create nozom_user \
  --instance=nozom-db \
  --password=YOUR_SECURE_PASSWORD
```

## تكوين Firebase Authentication

1. افتح وحدة التحكم Firebase: https://console.firebase.google.com/
2. انتقل إلى "Authentication" وقم بتفعيل طرق تسجيل الدخول المطلوبة
3. أضف النطاقات المسموح بها إلى "Authorized domains"

## ملاحظات هامة

- تأكد من تكوين جميع المتغيرات البيئية المطلوبة عند النشر
- للنشر على Firebase، يمكنك استخدام Cloud Functions for Firebase أو Cloud Run
- عند استخدام Cloud SQL، تأكد من إعداد الاتصال الآمن وإدارة الوصول بشكل صحيح
- قم بنسخ ملف `.env.example` إلى `.env` وملأه بالقيم الصحيحة