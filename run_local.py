#!/usr/bin/env python3
import os
import sys

print("--- [نقطة التفتيش 1] --- بداية تشغيل run_local.py")

try:
    from dotenv import load_dotenv
    print("--- [نقطة التفتيش 2] --- تم استيراد dotenv بنجاح")

    if os.path.exists('.env'):
        load_dotenv('.env')
        print("--- [نقطة التفتيش 3] --- تم تحميل الإعدادات من .env")
    else:
        print("--- [تحذير] --- لم يتم العثور على ملف .env، سيتم استخدام الإعدادات الافتراضية.")

    # --- هذا هو المكان الذي تم تعديله ---
    print("--- [نقطة التفتيش 4] --- على وشك استيراد التطبيق (app, db)...")
    from app import app, db # <--- التعديل الأول: استيراد 'app' مباشرة
    print("--- [نقطة التفتيش 5] --- تم استيراد التطبيق بنجاح!")
    
    # لا نحتاج لإنشاء التطبيق، فهو موجود بالفعل
    # app = create_app() # <--- التعديل الثاني: تم حذف هذا السطر
    print("--- [نقطة التفتيش 6] --- كائن التطبيق (app object) جاهز.")

    with app.app_context():
        print("--- [نقطة التفتيش 7] --- الدخول إلى سياق التطبيق (app context).")
        # غالبًا ما يتم استدعاء db.create_all() داخل app.py، لكن لنتركها هنا للاحتياط
        # db.create_all() 
        print("--- [نقطة التفتيش 8] --- تم فحص سياق التطبيق.")

    print("\n======= بدء تشغيل الخادم الآن =======")

    # تشغيل الخادم
    # التحقق من أننا في البرنامج الرئيسي لتجنب التشغيل المزدوج بسبب reloader
    if __name__ == '__main__':
       app.run(
    host='127.0.0.1', # <--- التعديل الجوهري هنا
    port=4032,       # دعنا نعد إلى المنفذ الأصلي
    debug=True,
    use_reloader=True
)
except Exception as e:
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!   حدث خطأ فادح   !!!!!!!!!!")
    print(f"!!!!!!!!!!   الخطأ: {e}   !!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)






# #!/usr/bin/env python3
# import os
# import sys

# print("--- [نقطة التفتيش 1] --- بداية تشغيل run_local.py")

# try:
#     from dotenv import load_dotenv
#     print("--- [نقطة التفتيش 2] --- تم استيراد dotenv بنجاح")

#     if os.path.exists('.env'):
#         load_dotenv('.env')
#         print("--- [نقطة التفتيش 3] --- تم تحميل الإعدادات من .env")
#     else:
#         print("--- [تحذير] --- لم يتم العثور على ملف .env، سيتم استخدام الإعدادات الافتراضية.")

#     # --- هذا هو المكان المحتمل للمشكلة ---
#     print("--- [نقطة التفتيش 4] --- على وشك استيراد التطبيق (create_app, db)...")
#     from app import create_app, db
#     print("--- [نقطة التفتيش 5] --- تم استيراد التطبيق بنجاح!")
    
#     app = create_app()
#     print("--- [نقطة التفتيش 6] --- تم إنشاء كائن التطبيق (app object).")

#     with app.app_context():
#         print("--- [نقطة التفتيش 7] --- الدخول إلى سياق التطبيق (app context).")
#         db.create_all()
#         print("--- [نقطة التفتيش 8] --- تم فحص قاعدة البيانات.")

#     print("\n======= بدء تشغيل الخادم الآن =======")

#     # تشغيل الخادم
#     app.run(
#         host='0.0.0.0',
#         port=5000,
#         debug=True,
#         use_reloader=True
#     )

# except Exception as e:
#     print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#     print("!!!!!!!!!!   حدث خطأ فادح   !!!!!!!!!!")
#     print(f"!!!!!!!!!!   الخطأ: {e}   !!!!!!!!!!")
#     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
#     # لإظهار تفاصيل الخطأ الكاملة (Traceback)
#     import traceback
#     traceback.print_exc()
#     sys.exit(1)









# #!/usr/bin/env python3
# """
# تشغيل نظام نُظم في البيئة المحلية
# """
# import os
# import sys
# from dotenv import load_dotenv

# def main():
#     """
#     الدالة الرئيسية لإعداد وتشغيل تطبيق Flask.
#     """
#     # تحميل متغيرات البيئة أولاً
#     if os.path.exists('.env'):
#         load_dotenv('.env')
#         print("✓ تم تحميل الإعدادات من .env")
#     elif os.path.exists('.env.local'):
#         load_dotenv('.env.local')
#         print("✓ تم تحميل الإعدادات من .env.local")
#     else:
#         print("تحذير: لم يتم العثور على ملف .env")

#     # استيراد التطبيق بعد تحميل متغيرات البيئة
#     try:
#         from app import create_app, db
#         app = create_app()
#     except ImportError as e:
#         print(f"خطأ في استيراد الوحدات: {e}")
#         print("تأكد من تفعيل البيئة الافتراضية وتثبيت المكتبات: pip install -r local_requirements.txt")
#         sys.exit(1)

#     # إنشاء جداول قاعدة البيانات ضمن سياق التطبيق
#     with app.app_context():
#         try:
#             db.create_all()
#             print("✓ تم فحص وتهيئة قاعدة البيانات بنجاح.")
#         except Exception as e:
#             print(f"خطأ أثناء تهيئة قاعدة البيانات: {e}")

#     print("\n" + "=" * 50)
#     print("🚀 بدء تشغيل نظام نُظم (وضع التطوير)...")
#     print(f"🔗 الرابط: http://{app.config.get('SERVER_NAME') or '127.0.0.1:5000'}")
#     print("🛑 للإيقاف: اضغط Ctrl+C")
#     print("=" * 50 + "\n")

#     # تشغيل الخادم
#     app.run(
#         host='0.0.0.0',
#         port=5000,
#         debug=True,
#         use_reloader=True
#     )

# # --- نقطة بداية تشغيل البرنامج ---
# # هذا هو الجزء الذي يتم تنفيذه فقط عند تشغيل `python run_local.py`
# if __name__ == '__main__':
#     main()











# #!/usr/bin/env python3
# """
# تشغيل نظام نُظم في البيئة المحلية
# """

# import os
# import sys
# from dotenv import load_dotenv

# # تحميل متغيرات البيئة
# if os.path.exists('.env'):
#     load_dotenv('.env')
# elif os.path.exists('.env.local'):
#     load_dotenv('.env.local')
# else:
#     print("تحذير: لم يتم العثور على ملف .env")

# # تعيين متغيرات البيئة للتطوير المحلي
# os.environ.setdefault('FLASK_ENV', 'development')
# os.environ.setdefault('FLASK_DEBUG', 'True')
# os.environ.setdefault('DATABASE_URL', 'sqlite:///nuzum_local.db')

# # import weasyprint  # تعطيل استدعاء WeasyPrint مؤقتًا، لاستخدام حل بديل (مثلاً، استخدام مكتبة أخرى أو تعطيل وظائف PDF مؤقتًا) بدلاً من تثبيت تبعيات GTK+ على Windows.

# try:
#     from app import app, db
    
#     # إنشاء قاعدة البيانات إذا لم تكن موجودة
#     with app.app_context():
#         try:
#             db.create_all()
#             print("✓ تم إعداد قاعدة البيانات")
#         except Exception as e:
#             print(f"خطأ في إعداد قاعدة البيانات: {e}")
    
#     print("🚀 بدء تشغيل نظام نُظم...")
#     print("📍 الرابط: http://localhost:5000")
#     print("🛑 للإيقاف: Ctrl+C")
#     print("-" * 50)
    
#     # تشغيل الخادم
#     app.run(
#         host='0.0.0.0',
#         port=5000,
#         debug=True,
#         use_reloader=True
#     )
    
# except ImportError as e:
#     print(f"خطأ في استيراد الوحدات: {e}")
#     print("تأكد من تثبيت المكتبات: pip install -r local_requirements.txt")
#     sys.exit(1)
# except Exception as e:
#     print(f"خطأ في تشغيل التطبيق: {e}")
#     sys.exit(1)