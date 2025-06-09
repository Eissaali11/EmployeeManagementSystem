"""
وحدة لإنشاء ملفات PDF من HTML مع دعم كامل للغة العربية
باستخدام مكتبة WeasyPrint
"""

import io
import os
from datetime import datetime
from weasyprint import HTML, CSS
from flask import render_template

def generate_pdf_from_template(template_name, **context):
    """
    إنشاء ملف PDF من قالب HTML مع دعم اللغة العربية
    
    Args:
        template_name: اسم قالب HTML (بدون .html)
        **context: متغيرات السياق للقالب
        
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    try:
        # إضافة تاريخ التوليد إلى السياق
        context['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # توليد HTML من القالب
        html_content = render_template(f'{template_name}.html', **context)
        
        # تحديد مسار الخطوط
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts')
        
        # إنشاء CSS يتضمن تعريف الخطوط العربية
        css_content = f"""
        @font-face {{
            font-family: 'Amiri';
            src: url('file://{font_path}/Amiri-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Amiri';
            src: url('file://{font_path}/Amiri-Bold.ttf') format('truetype');
            font-weight: bold;
            font-style: normal;
        }}
        
        body {{
            font-family: 'Amiri', sans-serif;
            direction: rtl;
            text-align: right;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: right;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        .report-header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .report-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .report-subtitle {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        
        .footer {{
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 10px;
            border-top: 1px solid #ddd;
            padding-top: 5px;
        }}
        """
        
        # إنشاء كائن CSS
        css = CSS(string=css_content)
        
        # إنشاء ذاكرة مؤقتة لتخزين الملف
        pdf_buffer = io.BytesIO()
        
        # إنشاء ملف PDF من HTML
        html = HTML(string=html_content)
        html.write_pdf(pdf_buffer, stylesheets=[css])
        
        # إعادة المؤشر إلى بداية الملف
        pdf_buffer.seek(0)
        
        return pdf_buffer
        
    except Exception as e:
        print(f"خطأ في إنشاء ملف PDF: {str(e)}")
        # في حالة الخطأ، نرجع ذاكرة مؤقتة فارغة
        empty_buffer = io.BytesIO()
        empty_buffer.write(b"ERROR: Failed to generate PDF")
        empty_buffer.seek(0)
        return empty_buffer