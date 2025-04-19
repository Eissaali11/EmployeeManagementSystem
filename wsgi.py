#!/usr/bin/python3
import os
import sys
import cgi

# إضافة مسار المشروع إلى مسارات النظام
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # طباعة الرأس لـ CGI
    print("Content-Type: text/html; charset=UTF-8")
    print("")
    
    # تهيئة التطبيق
    from main import app as application
    
    # عند التشغيل المباشر (اختبار محلي أو مع gunicorn)
    if __name__ == "__main__":
        # استخدام المنفذ المحدد من البيئة أو المنفذ 5000 كافتراضي
        port = int(os.environ.get("PORT", 5000))
        application.run(host='0.0.0.0', port=port)
    # للاستخدام مع CGI/FastCGI على استضافة مشتركة
    else:
        # الحصول على مسار URL الحالي من المتغيرات البيئية
        request_uri = os.environ.get('REQUEST_URI', '/')
        # معالجة الطلب يدوياً لـ CGI
        # هذا البديل لتوجيه WSGI على الاستضافة المشتركة التي لا تدعم WSGI بشكل كامل
        from io import StringIO
        import sys
        
        # إعادة توجيه الإخراج القياسي لالتقاط استجابة التطبيق
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        # تحديد مسار URL للتطبيق
        os.environ['REQUEST_URI'] = request_uri
        
        # محاكاة بيئة WSGI للتطبيق
        environ = {'PATH_INFO': request_uri}
        
        def mock_start_response(status, headers):
            pass
        
        # تنفيذ التطبيق
        try:
            application.wsgi_app(environ, mock_start_response)
        except Exception as e:
            print(f"<h1>خطأ في التطبيق</h1><p>{str(e)}</p>")
        
        # استعادة الإخراج القياسي وعرض النتيجة
        sys.stdout = old_stdout
        print(mystdout.getvalue())
        
except Exception as e:
    # عرض الأخطاء بطريقة واضحة للمطور
    print("<html dir='rtl'>")
    print("<head><title>خطأ في التطبيق</title>")
    print("<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css'>")
    print("</head><body><div class='container mt-5'>")
    print("<div class='alert alert-danger'>")
    print(f"<h3>حدث خطأ أثناء تشغيل التطبيق</h3>")
    print(f"<p>الخطأ: {str(e)}</p>")
    print("<h4>تفاصيل الخطأ:</h4>")
    print("<pre>")
    import traceback
    traceback.print_exc(file=sys.stdout)
    print("</pre>")
    print("</div>")
    print("<p>يرجى مراجعة إعدادات الاستضافة والتأكد من دعمها لتطبيقات Python.</p>")
    print("<a href='/static/deploy/' class='btn btn-primary'>الانتقال إلى صفحة الإعداد</a>")
    print("</div></body></html>")