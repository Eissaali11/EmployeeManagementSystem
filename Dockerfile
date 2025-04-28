FROM python:3.11-slim

WORKDIR /app

# نسخ ملفات المتطلبات أولاً لتحسين ذاكرة التخزين المؤقت
COPY requirements_deploy.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements_deploy.txt

# نسخ محتويات المشروع
COPY . .

# إعداد المتغيرات البيئية
ENV PORT=8080
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# فتح المنفذ
EXPOSE ${PORT}

# بدء تشغيل التطبيق باستخدام gunicorn
CMD exec gunicorn --bind :${PORT} --workers 1 --threads 8 --timeout 0 main:app