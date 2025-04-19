import os
import sys
from main import app

# إضافة مسار المشروع إلى مسارات النظام
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# تهيئة التطبيق للاستضافة
if __name__ == "__main__":
    # استخدام المنفذ المحدد من البيئة أو المنفذ 5000 كافتراضي
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)