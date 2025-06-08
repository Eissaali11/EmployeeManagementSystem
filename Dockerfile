FROM python:3.11-slim

# تثبيت المتطلبات النظامية
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملف التبعيات أولاً
COPY pyproject.toml ./

# نسخ ملفات المشروع
COPY . .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    Flask>=3.1.0 \
    Flask-Login>=0.6.3 \
    Flask-SQLAlchemy>=3.1.1 \
    Flask-WTF>=1.2.2 \
    WTForms>=3.1.2 \
    SQLAlchemy>=2.0.40 \
    psycopg2-binary>=2.9.10 \
    gunicorn>=23.0.0 \
    python-dotenv>=1.1.0 \
    Werkzeug>=3.1.3 \
    MarkupSafe>=3.0.2 \
    email-validator>=2.2.0 \
    Pillow>=11.2.1 \
    reportlab>=4.3.1 \
    weasyprint>=65.1 \
    openpyxl>=3.1.5 \
    xlrd>=2.0.1 \
    xlsxwriter>=3.2.2 \
    pandas>=2.2.3 \
    numpy>=2.2.4 \
    PyMySQL>=1.1.1 \
    arabic-reshaper>=3.0.0 \
    python-bidi>=0.6.6 \
    hijri-converter>=2.3.1 \
    fpdf>=1.7.2 \
    twilio>=9.5.2 \
    sendgrid>=6.11.0

# تعيين متغيرات البيئة
ENV PYTHONPATH=/app
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# تعريض المنفذ
EXPOSE 5000

# أمر تشغيل التطبيق
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "main:app"]