import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO

# تسجيل الخط العربي
font_path = os.path.join('static', 'fonts', 'ArefRuqaa-Regular.ttf')
pdfmetrics.registerFont(TTFont('ArefRuqaa', font_path))

# نص اختبار عربي
text = "هذا نص عربي للاختبار - تجربة PDF"

# تشكيل النص
reshaped_text = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped_text)

# إنشاء ملف PDF
buffer = BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)

# استخدام الخط العربي
c.setFont('ArefRuqaa', 18)

# كتابة النص
c.drawString(10*cm, 15*cm, bidi_text)

# حفظ الملف
c.save()

# كتابة الملف للقرص
with open('test_arabic.pdf', 'wb') as f:
    f.write(buffer.getvalue())

print("تم إنشاء ملف PDF!")