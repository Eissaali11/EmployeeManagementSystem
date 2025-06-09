#!/usr/bin/env python3
"""
تشغيل نظام نُظم في البيئة المحلية
"""

import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    print("تحذير: لم يتم العثور على ملف .env")

# تعيين متغيرات البيئة للتطوير المحلي
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('DATABASE_URL', 'sqlite:///nuzum_local.db')

try:
    from app import app, db
    
    # إنشاء قاعدة البيانات إذا لم تكن موجودة
    with app.app_context():
        try:
            db.create_all()
            print("✓ تم إعداد قاعدة البيانات")
        except Exception as e:
            print(f"خطأ في إعداد قاعدة البيانات: {e}")
    
    print("🚀 بدء تشغيل نظام نُظم...")
    print("📍 الرابط: http://localhost:5000")
    print("🛑 للإيقاف: Ctrl+C")
    print("-" * 50)
    
    # تشغيل الخادم
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
    
except ImportError as e:
    print(f"خطأ في استيراد الوحدات: {e}")
    print("تأكد من تثبيت المكتبات: pip install -r local_requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"خطأ في تشغيل التطبيق: {e}")
    sys.exit(1)