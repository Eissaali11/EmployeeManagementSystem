# في app/utils/report_generator.py
import qrcode
import base64

import io
import os
from flask import render_template, current_app
from weasyprint import HTML, CSS
# ----------------------------------------------------------------
# لا يوجد import لـ FontConfiguration هنا الآن (تم حذفه)
# ----------------------------------------------------------------

def generate_handover_report_pdf_weasyprint(handover):
    """
    Generates a PDF report using WeasyPrint (Modern API).
    """
    try:
        # معالجة آمنة للمسارات
        if handover.damage_diagram_path:
            handover.damage_diagram_path = handover.damage_diagram_path.replace("\\", "/")
        if handover.driver_signature_path:
            handover.driver_signature_path = handover.driver_signature_path.replace("\\", "/")
        if handover.supervisor_signature_path:
            handover.supervisor_signature_path = handover.supervisor_signature_path.replace("\\", "/")
        if handover.custom_logo_path:
            handover.custom_logo_path = handover.custom_logo_path.replace("\\", "/")
        if hasattr(handover, 'movement_officer_signature_path') and handover.movement_officer_signature_path:
            handover.movement_officer_signature_path = handover.movement_officer_signature_path.replace("\\", "/")

        # print(handover.custom_company_nam)
        print(f"Error generating PDF: {handover.custom_company_name}")

        qr_code_url = None

        if handover.form_link:
            qr_img = qrcode.make(handover.form_link)
            buffered = io.BytesIO()
            qr_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            qr_code_url = f"data:image/png;base64,{img_str}"

        
        

        # movement_officer_signature_path  , supervisor_signature_path
        # --- 1. Render the HTML template with the handover data ---
        html_string = render_template('vehicles/handover_report.html', handover=handover,qr_code_url=qr_code_url)
        
        # --- 2. Define the CSS stylesheet for fonts ---
        # المسار إلى مجلد static العام
        static_folder = os.path.join(current_app.root_path, 'static')
        
        # تجربة الخطوط المتوفرة بترتيب الأولوية
        font_options = [
            ('beIN Normal ', 'beIN Normal .ttf'),
            ('beIN-Normal', 'beIN-Normal.ttf'),
            ('Tajawal', 'Tajawal-Regular.ttf'),
            ('Cairo', 'Cairo.ttf'),
            ('Cairo', 'Cairo-Regular.ttf'),
            ('Amiri', 'Amiri-Regular.ttf')
        ]
        
        selected_font_family = 'Arial'
        selected_font_path = None
        
        for font_family, font_file in font_options:
            test_path = os.path.join(static_folder, 'fonts', font_file)
            if os.path.exists(test_path):
                selected_font_family = font_family
                selected_font_path = test_path
                break
        
        print(f"Selected font: {selected_font_family}")
        print(f"Font path: {selected_font_path}")
        print(f"Font exists: {os.path.exists(selected_font_path) if selected_font_path else False}")
        
        # إنشاء CSS للخط المختار
        if selected_font_path:
            font_css = CSS(string=f'''
                @font-face {{
                    font-family: '{selected_font_family}';
                    src: url('file://{selected_font_path}');
                    font-weight: normal;
                    font-style: normal;
                }}
                
                * {{
                    font-family: '{selected_font_family}', 'Arial', sans-serif !important;
                }}
                
                body, p, h1, h2, h3, h4, h5, h6, td, th, div, span {{
                    font-family: '{selected_font_family}', 'Arial', sans-serif !important;
                }}
                
                .arabic-text {{
                    font-family: '{selected_font_family}', 'Arial', sans-serif !important;
                    direction: rtl;
                    text-align: right;
                }}
            ''')
        else:
            # Fallback إلى Arial إذا لم نجد أي خط
            font_css = CSS(string='''
                * {
                    font-family: 'Arial', sans-serif !important;
                }
                
                body, p, h1, h2, h3, h4, h5, h6, td, th, div, span {
                    font-family: 'Arial', sans-serif !important;
                }
                
                .arabic-text {
                    font-family: 'Arial', sans-serif !important;
                    direction: rtl;
                    text-align: right;
                }
            ''')

        # --- 3. Create an HTML object ---
        # base_url مهم جدًا لكي تجد WeasyPrint الصور (مثل logo.png)
        # الموجودة في مجلد static
        html = HTML(string=html_string, base_url=static_folder)

        # --- 4. Write the PDF to a memory buffer ---
        pdf_buffer = io.BytesIO()
        html.write_pdf(
            pdf_buffer,
            # نمرر الـ CSS الخاص بالخط هنا
            stylesheets=[font_css]
        )
        
        pdf_buffer.seek(0)

        print(f"Error generating PDF: {handover.custom_company_name}")
        
        return pdf_buffer

    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        raise






# import io
# import os
# from flask import render_template, current_app
# from weasyprint import HTML, CSS
# # from weasyprint.fonts import FontConfiguration
# # السطر الجديد (الصحيح)
# from weasyprint.css import FontConfiguration 

# def generate_handover_report_pdf_weasyprint(handover):
#     """
#     Generates a PDF report for a vehicle handover using WeasyPrint.
#     This function renders an HTML template and converts it to PDF.
    
#     Args:
#         handover: The VehicleHandover object containing all necessary data.

#     Returns:
#         A BytesIO buffer containing the generated PDF.
#     """
#     try:
#         # --- 1. Render the HTML template with the handover data ---
#         # We pass the handover object to the template. Jinja2 will handle the rest.
#         html_string = render_template('vehicles/handover_report.html', handover=handover)
        
#         # --- 2. Configure fonts ---
#         # This tells WeasyPrint where to find our custom Arabic font.
#         font_config = FontConfiguration()
#         font_path = os.path.join(current_app.root_path, 'static', 'fonts', 'Amiri-Regular.ttf')
        
#         # We need a CSS string to define the @font-face rule.
#         # We use a 'file://' URL which is a reliable way for WeasyPrint to find local files.
#         # This CSS is IN ADDITION to the CSS inside the HTML file. It's only for font loading.
#         css_string = f"""
#             @font-face {{
#                 font-family: 'Amiri';
#                 src: url('file://{font_path}');
#             }}
#         """
        
#         css = CSS(string=css_string, font_config=font_config)
        
#         # --- 3. Create an HTML object ---
#         # The base_url is crucial for WeasyPrint to find relative assets like images 
#         # that are linked in the HTML (e.g., <img src="/static/...">).
#         # We point it to the root of the application.
#         html = HTML(string=html_string, base_url=current_app.root_path)

#         # --- 4. Write the PDF to a memory buffer ---
#         pdf_buffer = io.BytesIO()
#         html.write_pdf(
#             pdf_buffer,
#             stylesheets=[css],  # Apply the font-face CSS
#             font_config=font_config
#         )
#         pdf_buffer.seek(0)
        
#         return pdf_buffer

#     except Exception as e:
#         # For debugging, it's very helpful to print the error.
#         print(f"Error generating PDF: {e}")
#         import traceback
#         traceback.print_exc()
#         # In a production environment, you might want to return a pre-made error PDF
#         # or raise the exception to be handled by the view.
#         raise  # Re-raise the exception so the view can handle it.













































































































# # fpdf_handover_pdf.py

# import io
# import os
# from datetime import datetime
# from fpdf import FPDF
# from arabic_reshaper import reshape
# from bidi.algorithm import get_display
# from fpdf.table  import Table


# #         font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts')
# #         try:
# #             self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'))
# #             self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'))
# # --- إعدادات أساسية ---

# PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
# FONT_PATH =os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts') # مسار دقيق أكثر
# # تعريف الألوان كثوابت
# TEAL_COLOR = (0, 150, 136) # اللون الأخضر المزرق المستخدم في التصميم
# DARK_GRAY_COLOR = (89, 89, 91)
# LIGHT_GRAY_COLOR = (242, 242, 242)

# class ReportPDF(FPDF):
#     """
#     كلاس PDF مُحسَّن للاستخدام مع fpdf2 ودعم كامل لـ Unicode.
#     """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.set_auto_page_break(auto=True, margin=15)
#         self.set_margins(10, 10, 10)
#         self.add_fonts()
#         self.set_font('Amiri', '', 10)

#     def add_fonts(self):
#         """إضافة الخطوط العربية. fpdf2 تحتاج uni=True لمعالجة Unicode."""
#         font_path = os.path.join(PROJECT_DIR, 'static', 'fonts')
#         try:
#             self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'), uni=True)
#             self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'), uni=True)
#         except RuntimeError as e:
#             if "already added" not in str(e).lower():
#                 raise e

#     def cell_with_detail(self, title_ar, title_en, value_str, align='C'):
#         """
#         (نسخة مُحسَّنة لـ fpdf2)
#         ترسم كتلة تفاصيل كاملة داخل الخلية الحالية للجدول.
#         """
#         start_x = self.get_x()
#         start_y = self.get_y()
#         # عرض الخلية الحالية التي يتم استدعاؤها من داخل الجدول
#         # width=0 يعني أن الخلية ستأخذ العرض الكامل المتاح لها
#         cell_width = 0

#         # العنوان العربي
#         self.set_font('Amiri', 'B', 10)
#         self.set_text_color(*TEAL_COLOR)
#         self.multi_cell(cell_width, 5, title_ar, 0, align)
        
#         # العنوان الإنجليزي
#         self.set_font('Amiri', '', 7)
#         self.set_text_color(160, 160, 160)
#         self.multi_cell(cell_width, 3, title_en.upper(), 0, align)

#         # القيمة
#         self.set_font('Arial', 'B', 10)
#         self.set_text_color(0, 0, 0)
#         self.set_y(self.get_y() + 1)
#         self.multi_cell(cell_width, 5, str(value_str), 0, align)
        
#         # العودة إلى الموضع X الأصلي استعداداً للخلية التالية
#         # مع y مضبوطة بالفعل من آخر multi_cell
#         self.set_x(start_x + self.w) 


#     def _cell_with_detail(cell, title_ar, title_en, value_str, align='C'):
#         pdf = cell.pdf # الحصول على كائن الـ PDF من الخلية
    
#         # العنوان العربي
#         pdf.set_font('Amiri', 'B', 10)
#         pdf.set_text_color(*TEAL_COLOR)
#         cell.write(5, f'{title_ar}\n')
        
#         # العنوان الإنجليزي
#         pdf.set_font('Amiri', '', 7)
#         pdf.set_text_color(160, 160, 160)
#         cell.write(3, f'{title_en.upper()}\n\n')

#         # القيمة
#         pdf.set_font('Arial', 'B', 10)
#         pdf.set_text_color(0, 0, 0)
#         cell.write(5, str(value_str))

#     # --- ربط الدالة المساعدة بكلاس الخلية ---
#     # هذا السطر يتم وضعه خارج أي كلاس أو دالة، في المستوى العام للملف




#     def footer(self):
#         """يرسم تذييل الصفحة."""
#         self.set_y(-15)
#         self.set_font('Amiri', '', 9)
#         self.set_text_color(*TEAL_COLOR)
#         self.cell(0, 5, 'www.rassaudi.com', 0, 1, 'C')
#         self.set_text_color(128)
#         footer_text = "Al Riyadh Musa Bin Nussier Road, Olaya, Al Nimer Tower Building 1, Office 709-710"
#         self.cell(0, 5, footer_text, 0, 1, 'C')
        
    


# def draw_header(pdf, handover):
#     """
#     دالة لرسم رأس التقرير (الشعار، اسم الشركة، عنوان التقرير).
#     تستخدم البيانات المخصصة إذا كانت متوفرة.
#     """
#     print("Drawing Header...")

#     # === 1. رسم الشعار (على اليسار) ===
#     # تحديد مسار الشعار: المخصص أولاً، ثم الافتراضي
#     if handover.custom_logo_path:
#         logo_path = os.path.join(PROJECT_DIR,  'static', 'uploads', handover.custom_logo_path)
#     else:
#         # تأكد من أن مسار الشعار الافتراضي صحيح
#         logo_path = os.path.join(PROJECT_DIR,  'static', 'images', 'logo.png')
    
#     # التحقق من وجود الملف قبل محاولة رسمه
#     if os.path.exists(logo_path):
#         try:
#             # pdf.image(مسار، x، y، عرض، ارتفاع)
#             pdf.image(logo_path, x=10, y=10, w=60) 
#         except Exception as e:
#             print(f"FPDF Error: Could not load logo image. {e}")
#             # يمكن رسم مربع بديل في حالة الفشل
#             pdf.set_xy(10, 8)
#             pdf.set_fill_color(230, 230, 230)
#             pdf.cell(45, 20, "Logo", 1, 0, 'C', True)

#     # === 2. رسم عنوان التقرير (على اليمين) ===
#     # محاذاة النص لليمين يدوياً بضبط قيمة x
#     pdf.set_text_color(*TEAL_COLOR)
    
#     pdf.set_font('Amiri', 'B', 14) # حجم الخط للإنجليزي
#     pdf.set_xy(140, 10) # 200 (عرض الورقة) - 10 (هامش) - 50 (عرض النص التقريبي)
#     pdf.cell(60, 7, 'Vehicle Delivery and receipt', 0, 1, 'R')

#     pdf.set_font('Amiri', 'B', 12) # حجم الخط للعربي
#     pdf.set_xy(140, 16)
#     pdf.cell(60, 7, pdf.RTL_text('نموذج تسليم و استلام مركبة'), 0, 1, 'R')
    
#     # === 3. رسم اسم الشركة (في المنتصف) ===
#     # تحديد اسم الشركة: المخصص أولاً، ثم الافتراضي
#     company_name = handover.custom_company_name or "شركة راس السعودية المحدودة"
    
#     pdf.set_font('Amiri', 'B', 16)
#     pdf.set_text_color(*DARK_GRAY_COLOR)
#     # لا حاجة لحساب العرض المسبق مع cell، يمكن توسيطها مباشرة
#     pdf.set_y(8) # العودة للأعلى قليلاً
#     pdf.cell(0, 10, pdf.RTL_text(company_name), 0, 1, 'C')

#     # إضافة سطر فاصل في النهاية
#     pdf.set_y(35) # تحديد موضع y للخط
#     pdf.set_draw_color(*DARK_GRAY_COLOR)
#     pdf.line(x1=10, y1=pdf.get_y(), x2=200, y2=pdf.get_y())
    
#     # ترك مسافة كافية قبل القسم التالي
#     pdf.ln(8)


# # في fpdf_handover_pdf.py

# def draw_info_block(pdf, handover):
#     """
#     دالة لرسم قسم المعلومات العامة، مع تحكم يدوي ودقيق في المواضع.
#     """
#     print("Drawing Info Block (Corrected Manual Layout)...")
    
#     start_y = pdf.get_y()
    
#     # --- دالة مساعدة داخلية بسيطة لرسم كتلة معلومات واحدة ---
#     def draw_detail(x, y, title_ar, title_en, value, align='C'):
#         # العنوان العربي
#         pdf.set_font('Amiri', 'B', 10)
#         pdf.set_text_color(*TEAL_COLOR)
#         pdf.set_xy(x, y)
#         pdf.cell(40, 5, title_ar, 0, 1, align)
        
#         # العنوان الإنجليزي
#         pdf.set_font('Amiri', '', 7)
#         pdf.set_text_color(160, 160, 160)
#         pdf.set_xy(x, pdf.get_y())
#         pdf.cell(40, 3, title_en.upper(), 0, 1, align)
        
#         # القيمة
#         pdf.set_font('Arial', 'B', 10)
#         pdf.set_text_color(0, 0, 0)
#         pdf.set_xy(x, pdf.get_y() + 1)
#         pdf.cell(40, 5, str(value), 0, 1, align)
        
#     # --- رسم شبكة المعلومات ---
#     # نحدد نقطة بداية لكل كتلة
#     # الصف العلوي
#     y_top_row = start_y
#     draw_detail(x=130, y=y_top_row, title_ar="التاريخ", title_en="Date", 
#                 value=(handover.handover_date.strftime('%d/%m/%Y') if handover.handover_date else "-"))
                
#     draw_detail(x=80, y=y_top_row, title_ar="المشروع", title_en="the project",
#                 value=(handover.project_name or "-"))

#     draw_detail(x=20, y=y_top_row, title_ar="الكيلو متر", title_en="Mileage km", 
#                 value=f"{handover.mileage:,}" if handover.mileage is not None else "-")

#     # الصف السفلي
#     y_bottom_row = start_y + 15
#     draw_detail(x=130, y=y_bottom_row, title_ar="الساعة", title_en="Time", 
#                 value=(handover.handover_time.strftime('%I:%M:%S %p') if handover.handover_time else "-"))
                
#     draw_detail(x=80, y=y_bottom_row, title_ar="المدينة", title_en="city", 
#                 value=(handover.city or "-"))

#     # --- رسم مربعات الاختيار في مكانها الصحيح (الخلية الفارغة) ---
#     box_y = y_bottom_row + 4 # محاذاة رأسية
    
#     # تسليم
#     pdf.set_font('Amiri', '', 10)
#     pdf.set_text_color(*TEAL_COLOR)
#     pdf.set_xy(25, box_y)
#     pdf.cell(10, 5, "تسليم", 0, 0, 'R')
#     pdf.rect(x=36, y=box_y + 0.5, w=4, h=4)

#     # استلام
#     pdf.set_xy(45, box_y)
#     pdf.cell(10, 5, "استلام", 0, 0, 'R')
#     pdf.rect(x=56, y=box_y + 0.5, w=4, h=4)
    
#     # علامة التحديد (الدائرة)
#     if handover.handover_type == 'delivery':
#         marker_x = 36
#     else: # 'receive'
#         marker_x = 56
            
#     pdf.set_fill_color(*TEAL_COLOR)
#     pdf.ellipse(marker_x, box_y + 0.5, 4, 4, 'F')


#     # --- النزول إلى ما بعد القسم بالكامل ---
#     pdf.set_y(y_bottom_row + 15)
#     pdf.ln(5)


# def draw_tables_section(pdf, handover):
#     """دالة لرسم جداول معلومات السيارة والسائق."""
#     print("Drawing Tables...")
#     # (سيتم إضافة الكود هنا)

# def draw_inspection_section(pdf, handover):
#     """دالة لرسم قسم فحص السيارة."""
#     print("Drawing Inspection...")
#     # (سيتم إضافة الكود هنا)

# def draw_notes_section(pdf, handover):
#     """دالة لرسم قسم الملاحظات العامة."""
#     print("Drawing Notes...")
#     # (سيتم إضافة الكود هنا)

# def draw_authorization_section(pdf, handover):
#     """دالة لرسم قسم التفويض وبيانات الأفراد."""
#     print("Drawing Authorization...")
#     # (سيتم إضافة الكود هنا)

# def draw_signatures_section(pdf, handover):
#     """دالة لرسم قسم التوقيعات النهائي."""
#     print("Drawing Signatures...")
#     # (سيتم إضافة الكود هنا)
    
# def draw_attachments_page(pdf, handover):
#     """دالة لرسم صفحة الصور المرفقة."""
#     print("Drawing Attachments...")
#     # (سيتم إضافة الكود هنا)

# # ==========================================================
# # ====== الدالة الرئيسية لإنشاء التقرير (الهيكل الجديد) ======
# # ==========================================================
# def generate_handover_report_pdf(handover):
#     """
#     الدالة الرئيسية التي تجمع كل الأجزاء لإنشاء تقرير PDF.
#     تقبل كائن `handover` واحد فقط يحتوي على كل البيانات.
#     """
    
#     # 1. تهيئة كائن الـ PDF
#     pdf = ReportPDF('P', 'mm', 'A4')
#     # pdf.set_right_to_left(True) # تفعيل وضع RTL للصفحة
#     pdf.add_page()
    
#     # 2. استدعاء دوال الرسم لكل قسم بالترتيب
#     draw_header(pdf, handover)
#     draw_info_block(pdf, handover)
#     draw_tables_section(pdf, handover)
#     draw_inspection_section(pdf, handover)
#     draw_notes_section(pdf, handover)
#     draw_authorization_section(pdf, handover)
#     draw_signatures_section(pdf, handover)
    
#     # رسم صفحة المرفقات إذا كانت موجودة
#     if handover.images:
#         draw_attachments_page(pdf, handover)

#     # 3. حفظ الملف في الذاكرة وإعادته
#     pdf_buffer = io.BytesIO()
#     pdf.output(pdf_buffer)
#     pdf_buffer.seek(0)
    
#     return pdf_buffer

















































































# """
# مولد تقارير تسليم/استلام المركبات باستخدام FPDF
# مع دعم كامل للنصوص العربية والاتجاه من اليمين لليسار
# """

# import io
# import os
# from datetime import datetime
# from io import BytesIO
# from fpdf import FPDF
# from arabic_reshaper import reshape
# from bidi.algorithm import get_display


# # تحديد المسار الحالي ومسار المشروع
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_DIR = os.path.dirname(CURRENT_DIR)




# class ReportPDF(FPDF):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.set_auto_page_break(auto=True, margin=15)
#         self.set_margins(10, 10, 10)

#         # تحديد مسار الخطوط
#         font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts')
#         try:
#             self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'))
#             self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'))
#         except RuntimeError as e:
#             if "Font already added" not in str(e):
#                 raise e
        
#         self.set_font('Amiri', '', 10)

#     def RTL_text(self, text):
#         """
#         دالة مساعدة لتشكيل وعكس النص العربي.
#         """
#         text_str = str(text) if text is not None else ""
#         reshaped_text = reshape(text_str)
#         bidi_text = get_display(reshaped_text)
#         return bidi_text

#     def footer(self):
#         # التذييل المخصص
#         self.set_y(-15)
#         self.set_font('Amiri', '', 9)
#         self.set_text_color(0, 169, 157)
#         self.cell(0, 5, 'www.rassaudi.com', 0, 1, 'C')
#         self.set_text_color(128)
#         footer_text = "Al Riyadh Musa Bin Nussier Road, Olaya, Al Nimer Tower Building 1, Office 709-710"
#         self.cell(0, 5, footer_text, 0, 1, 'C')



# # الدالة الرئيسية لإنشاء التقرير
# def generate_handover_report_pdf(vehicle, handover_record,images):
    
#     # تعريف الألوان
#     TEAL = (0, 169, 157)
#     LIGHT_GRAY = (242, 242, 242)
#     DARK_GRAY = (89, 89, 91)

#     pdf = ReportPDF('P', 'mm', 'A4')
#     pdf.add_page()


#     # =============================================================
#     # 1. الرأس (Header) - النسخة النهائية مع الشعار والاسم المخصصين
#     # =============================================================

# # --- تحديد الشعار ---
#     if handover_record.custom_logo_path:
#         # إذا كان هناك شعار مخصص، استخدم مساره
#         logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', handover_record.custom_logo_path)
#     else:
#         # وإلا، استخدم الشعار الافتراضي
#         logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
    
#     # عرض الشعار على اليسار (مع التحقق من وجود الملف)
#     if os.path.exists(logo_path):
#         try:
#             pdf.image(logo_path, x=10, y=10, w=50)
#         except Exception as e:
#             print(f"Error loading logo into PDF: {e}")
#             # يمكنك إضافة مربع بديل هنا إذا أردت
#     else:
#         print(f"Logo not found at path: {logo_path}")
    
    
#     # --- عرض عنوان التقرير على اليمين ---
#     pdf.set_font('Amiri', 'B', 12)
#     pdf.set_text_color(*TEAL)
#     pdf.set_xy(110, 12)
#     pdf.cell(90, 7, 'Vehicle Delivery and receipt', 0, 1, 'R')
#     pdf.set_xy(110, 19)
#     pdf.cell(90, 7, pdf.RTL_text('نموذج تسليم و استلام مركبة'), 0, 1, 'R')
    
    
#     # --- عرض اسم الشركة (المخصص أو الافتراضي) في المنتصف ---
#     if handover_record.custom_company_name:
#         # إذا كان هناك اسم شركة مخصص، استخدمه
#         company_name = handover_record.custom_company_name
#     else:
#         # وإلا، استخدم الاسم الافتراضي
#         company_name = "شركة راس السعودية المحدودة" # أو أي اسم افتراضي تريده
    
#     pdf.set_font('Amiri', 'B', 14)
#     pdf.set_text_color(*DARK_GRAY)
#     # لحساب الموضع بشكل صحيح، نحصل على عرض النص أولاً
#     company_name_width = pdf.get_string_width(pdf.RTL_text(company_name))
#     # الموضع السيني للمنتصف = (عرض الصفحة - عرض النص) / 2
#     center_x_pos = (pdf.w - company_name_width) / 2
#     pdf.set_xy(center_x_pos, 15) # في المنتصف رأسياً تقريباً
#     pdf.cell(company_name_width, 10, pdf.RTL_text(company_name), 0, 1, 'C')
    
    
#     # --- رسم الخط الفاصل ---
#     pdf.set_draw_color(*DARK_GRAY)
#     pdf.line(10, 30, 200, 30)
#     pdf.ln(15) # ترك مسافة كافية قبل القسم التالي




#     # =================================
#     # 2. معلومات العملية (بنية هرمية جديدة)
#     # =================================
#     current_y = pdf.get_y()

#     # --- القسم الأول: تحديد نوع العملية (تسليم واستلام) ---
#     # هذا القسم يُرسَم أولاً وبشكل مستقل
#     y_handover_type = current_y # إضافة هامش علوي صغير
#     x_center = pdf.w / 2 # مركز الصفحة الأفقي

#     # تحديد مواضع "تسليم" و "استلام" حول المركز
#     x_delivery_label = x_center + 25
#     x_receipt_label = x_center - 15

#     # رسم "تسليم" ومربعها
#     pdf.set_font('Amiri', 'B', 10)
#     pdf.set_text_color(*TEAL)
#     pdf.set_xy(x_delivery_label, y_handover_type)
#     pdf.cell(20, 7, pdf.RTL_text("تسليم"), 0, 0, 'R')
#     pdf.rect(x_delivery_label - 5, y_handover_type + 1.5, 4, 4, 'D') # رسم المربع

#     # رسم "استلام" ومربعها
#     pdf.set_xy(x_receipt_label, y_handover_type)
#     pdf.cell(20, 7, pdf.RTL_text("استلام"), 0, 0, 'R')
#     pdf.rect(x_receipt_label - 5, y_handover_type + 1.5, 4, 4, 'D') # رسم المربع

#     # وضع علامة 'X' في المربع الصحيح
#     is_delivery = (handover_record.handover_type == "delivery")
#     if is_delivery:
#         checkbox_x_to_mark = x_delivery_label - 5
#     else:
#         checkbox_x_to_mark = x_receipt_label - 5

#     pdf.set_font('Arial', 'B', 10)
#     pdf.set_xy(checkbox_x_to_mark, y_handover_type + 1.5)
#     pdf.cell(4, 4, 'X', 0, 0, 'C')


#     # --- النزول لأسفل لبدء القسم الثاني ---
#     pdf.ln(7) # ترك مسافة رأسية واضحة بين القسمين


#     # --- القسم الثاني: باقي التفاصيل ---
#     y_details_start = pdf.get_y() + 2 # الحصول على موضع البدء الجديد

#     def draw_details_pair(x_label, x_value, y, label, value):
#         # دالة مساعدة لرسم أزواج التفاصيل
#         pdf.set_font('Amiri', 'B', 10)
#         pdf.set_text_color(*TEAL)
#         pdf.set_xy(x_label, y)
#         pdf.cell(25, 7, pdf.RTL_text(label), 0, 0, 'R')
        
#         pdf.set_font('Amiri', '', 10)
#         pdf.set_text_color(0)
#         pdf.set_xy(x_value, y)
#         pdf.cell(35, 7, pdf.RTL_text(str(value)), 0, 0, 'R')

#     # تحديد إحداثيات أعمدة التفاصيل
#     X_RIGHT_COL_LABEL = 140  # العمود الأيمن (التاريخ والساعة)
#     X_RIGHT_COL_VALUE = 115
#     X_LEFT_COL_LABEL  = 80  # العمود الأيسر (المشروع والمدينة)
#     X_LEFT_COL_VALUE  = 45

#     # استخراج البيانات
#     project = getattr(handover_record, 'project_name', 'ARAMEX')
#     city = getattr(handover_record, 'city', 'القصيم')
#     handover_date_str = handover_record.handover_date.strftime('%d/%m/%Y')
#     handover_time_str = handover_record.handover_time.strftime('%I:%M %p') if hasattr(handover_record, 'handover_time') and handover_record.handover_time else 'غير محدد'
#     mileage_str = f'{handover_record.mileage} km'
#     color = vehicle.color if vehicle else 'غير محدد'

#     # رسم التفاصيل صفاً بصف
#     draw_details_pair(X_RIGHT_COL_LABEL, X_RIGHT_COL_VALUE, y_details_start, 'التاريخ', handover_date_str)
#     draw_details_pair(X_LEFT_COL_LABEL, X_LEFT_COL_VALUE, y_details_start, 'المشروع', project)

#     y_row2 = y_details_start + 8
#     draw_details_pair(X_RIGHT_COL_LABEL, X_RIGHT_COL_VALUE, y_row2, 'الساعة', handover_time_str)
#     draw_details_pair(X_LEFT_COL_LABEL, X_LEFT_COL_VALUE, y_row2, 'المدينة', city)

#     y_row3 = y_details_start + 16
#     # الكيلومترات في العمود الأيسر فقط
#     draw_details_pair(X_RIGHT_COL_LABEL, X_RIGHT_COL_VALUE, y_row3, 'اللون', color)
#     draw_details_pair(X_LEFT_COL_LABEL, X_LEFT_COL_VALUE, y_row3, 'الكيلو متر', mileage_str)


#     # --- ترك مسافة كافية قبل الجداول ---
#     pdf.ln(7)
   
   
#     # =================================
#     # 3. جداول المعلومات
#     # =================================
#     def draw_table_header(headers):
#         pdf.set_font('Amiri', 'B', 9)
#         pdf.set_fill_color(*TEAL)
#         pdf.set_text_color(255)
#         for header, width in headers:
#             pdf.cell(width, 10, pdf.RTL_text(header), 1, 0, 'C', True)
#         pdf.ln()

#     def draw_table_row(data, widths):
#         pdf.set_font('Amiri', '', 9)
#         pdf.set_text_color(0)
#         pdf.set_fill_color(255)
#         for item, width in zip(data, widths):
#             pdf.cell(width, 10, pdf.RTL_text(str(item)), 1, 0, 'C')
#         pdf.ln()

#     headers1 = [('نوع السيارة', 45), ('اللوحة', 45), ('الموديل', 45), ('سبب تغيير المركبة', 45)]
#     widths1 = [w for _, w in headers1]
#     data1 = [getattr(vehicle, 'type', 'N/A'), vehicle.plate_number, vehicle.model, getattr(handover_record, 'reason', 'N/A')]
    
#     draw_table_header(headers1)
#     draw_table_row(data1, widths1)

#     headers2 = [('اسم السائق', 45), ('رقم الهاتف', 45), ('رقم الشركة', 45), ('رقم الإقامة', 45)]
#     widths2 = [w for _, w in headers2]
#     data2 = [handover_record.person_name, getattr(handover_record, 'phone_number', 'N/A'), getattr(handover_record, 'company_id', 'N/A'), getattr(handover_record, 'residency_number', 'N/A')]
    
#     draw_table_header(headers2)
#     draw_table_row(data2, widths2)
    
#     pdf.ln(4)

#     # =================================
#     # 4. فحص المركبة والصورة
#     # =================================
#     pdf.ln(1) # مسافة صغيرة قبل القسم الجديد
#     pdf.set_font('Amiri', 'B', 11)
#     pdf.set_fill_color(*LIGHT_GRAY) # استخدام نفس لون الخلفية الفاتح
#     pdf.set_draw_color(*DARK_GRAY)
#     pdf.cell(0, 8, pdf.RTL_text("فحص المركبة"), 1, 1, 'C', True)
#     pdf.ln(2)


#     checklist_y = pdf.get_y()
    
#     # --- تحديد مسار صورة هيكل المركبة بشكل ديناميكي ---
#     if handover_record.damage_diagram_path:
#           # إذا كان هناك مسار لصورة مخصصة في قاعدة البيانات، استخدمه
#           # المسار المخزن هو نسبي لمجلد uploads, مثلا: 'diagrams/xxxx.png'
#           vehicle_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', handover_record.damage_diagram_path)
#     else:
#         # وإلا، استخدم المسار الافتراضي للصورة الثابتة
#         vehicle_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'vehicle_diagram.png')
    
#     # --- الصورة على اليسار (مع التحقق من وجود الملف) ---
#     if os.path.exists(vehicle_image_path):
#         # نضع استدعاء الصورة داخل try-except كإجراء احترازي إضافي
#         try:
#             pdf.image(vehicle_image_path, x=15, y=checklist_y, w=90)
#         except Exception as e:
#             print(f"Error loading image into PDF: {e}")
#               # إذا فشلت fpdf في تحميل الصورة، ارسم المربع البديل
#             pdf.set_fill_color(240, 240, 240)
#             pdf.rect(15, checklist_y, 90, 50, 'DF')
#             pdf.set_xy(15, checklist_y + 20)
#             pdf.multi_cell(90, 5, pdf.RTL_text("خطأ في تحميل الصورة"), 0, 'C')
#     else:
#        # في حالة عدم وجود الملف أصلاً، ارسم مربعاً بديلاً
#        pdf.set_fill_color(240, 240, 240)
#        pdf.rect(15, checklist_y, 90, 50, 'DF') 
       
#        pdf.set_font('Amiri', '', 8)
#        pdf.set_xy(15, checklist_y + 20)
#        missing_file_name = os.path.basename(vehicle_image_path)
#        pdf.multi_cell(90, 5, pdf.RTL_text(f"لم يتم العثور على الصورة\n{missing_file_name}"), 0, 'C')



#         # --- دالة مساعدة لرسم عنصر فحص واحد بشكل صحيح ---
#     def draw_checklist_item(anchor_x, y, label, status):
#         """
#         ترسم عنصر فحص واحد (نص + مربع) في موقع محدد.
        
#         Args:
#             anchor_x (int): الإحداثي السيني (X) للحافة اليمنى للكتلة بأكملها.
#             y (int): الإحداثي الصادي (Y).
#             label (str): النص العربي للعنصر.
#             status (bool): هل العنصر محدد أم لا.
#         """
#         TEXT_WIDTH = 25      # عرض المساحة المخصصة للنص
#         CHECKBOX_WIDTH = 4   # عرض المربع
#         PADDING = 2          # المسافة بين النص والمربع
#         CELL_HEIGHT = 7      # ارتفاع الخلية

#         # 1. تحديد موقع النص: يجب أن ينتهي عند anchor_x
#         text_x = anchor_x - TEXT_WIDTH
#         pdf.set_font('Amiri', '', 9)
#         pdf.set_text_color(0)
#         pdf.set_xy(text_x, y)
#         pdf.cell(TEXT_WIDTH, CELL_HEIGHT, pdf.RTL_text(label), 0, 0, 'R')

#         # 2. تحديد موقع المربع: على يسار النص مع ترك مسافة
#         checkbox_x = text_x - PADDING - CHECKBOX_WIDTH
#         pdf.rect(checkbox_x, y + 1.5, CHECKBOX_WIDTH, CHECKBOX_WIDTH, 'D')

#         # 3. وضع علامة 'X' إذا كان محددًا
#         if status:
#             pdf.set_font('Arial', 'B', 10)
#             pdf.set_xy(checkbox_x, y + 1.5)
#             pdf.cell(CHECKBOX_WIDTH, CHECKBOX_WIDTH, 'X', 0, 0, 'C')
#             pdf.set_font('Amiri', '', 9) # مهم: العودة للخط العربي


#     # --- قائمة الفحص على اليمين ---
#     checklist_items = [
#         ('تهريب زيوت', 'has_oil_leaks'), ('جير', 'has_gear_issue'),
#         ('كلتش', 'has_clutch_issue'), ('ماكينة', 'has_engine_issue'),
#         ('زجاج', 'has_windows_issue'), ('كفرات', 'has_tires_issue'),
#         ('هيكل', 'has_body_issue'), ('كهرباء', 'has_electricity_issue'),
#         ('أنوار', 'has_lights_issue'), ('مكيف', 'has_ac_issue'),
#     ]

#     # تحديد نقاط الارتكاز للعمودين
#     col1_anchor_x = 195 # الحافة اليمنى للعمود الأيمن
#     col2_anchor_x = 150 # الحافة اليمنى للعمود الأيسر
#     item_y = checklist_y
#     row_height = 8 # المسافة الرأسية بين كل صف

#     for i, (ar_label, field) in enumerate(checklist_items):
#         # تحديد العمود الحالي
#         current_anchor_x = col1_anchor_x if i % 2 == 0 else col2_anchor_x
#         status = getattr(handover_record, field, False)
        
#         # رسم العنصر باستخدام الدالة المساعدة
#         draw_checklist_item(current_anchor_x, item_y, ar_label, status)

#         # الانتقال إلى الصف التالي بعد رسم عنصرين (واحد في كل عمود)
#         if i % 2 != 0:
#             item_y += row_height
            
#     # ضبط الموضع الرأسي للانتقال إلى القسم التالي
#     pdf.set_y(checklist_y + 45)

 
#     # =================================
#     # 4.1 حالة السيارة عند التسليم/الاستلام
#     # =================================
#     pdf.set_font('Amiri', '', 10)
#     pdf.set_draw_color(*DARK_GRAY)
#     pdf.set_fill_color(*LIGHT_GRAY)
#     if handover_record.vehicle_condition:
#         pdf.multi_cell(0, 8, pdf.RTL_text(f"حالة السيارة عند التسليم/الاستلام: {handover_record.vehicle_condition}"), 1, 'R', True)
#     else:
#         pdf.multi_cell(0, 8, pdf.RTL_text("حالة السيارة عند التسليم/الاستلام: لا يوجد"), 1, 'R', True)

#     pdf.ln(2)

#     # =================================
#     # 4.5. قسم معدات المركبة 
#     # =================================
#     pdf.ln(2) # مسافة صغيرة قبل القسم الجديد
#     pdf.set_font('Amiri', 'B', 11)
#     pdf.set_fill_color(*LIGHT_GRAY) # استخدام نفس لون الخلفية الفاتح
#     pdf.set_draw_color(*DARK_GRAY)
#     pdf.cell(0, 8, pdf.RTL_text("معدات المركبة"), 1, 1, 'C', True)
#     pdf.ln(4)

#     # --- دالة مساعدة لرسم عنصر واحد من معدات المركبة ---
#     def draw_equipment_item(x_label, y, label, status_bool):
#         """
#         ترسم اسم المعدة وحالتها (متوفر/غير متوفر) بلون مميز.
#         """
#         # 1. تحديد النص واللون بناءً على الحالة
#         if status_bool:
#             status_text = "متوفر"
#             status_color = (0, 150, 0)  # أخضر داكن
#         else:
#             status_text = "غير متوفر"
#             status_color = (200, 0, 0) # أحمر

#         # 2. رسم اسم المعدة
#         pdf.set_font('Amiri', '', 10)
#         pdf.set_text_color(0)
#         pdf.set_xy(x_label, y)
#         pdf.cell(45, 7, pdf.RTL_text(f"{label}:"), 0, 0, 'R')

#         # 3. رسم الحالة باللون المميز
#         pdf.set_font('Amiri', 'B', 10)
#         pdf.set_text_color(*status_color)
#         # تحديد موقع الحالة على يسار اسم المعدة
#         status_x = x_label - 45
#         pdf.set_xy(status_x, y)
#         pdf.cell(25, 7, pdf.RTL_text(status_text), 0, 0, 'R')
        
#         # إعادة اللون إلى الأسود الافتراضي
#         pdf.set_text_color(0)


#     # --- قائمة المعدات (من الكود القديم) ---
#     equipment_items = [
#         ('has_spare_tire', 'الإطار الاحتياطي'),
#         ('has_fire_extinguisher', 'طفاية الحريق'),
#         ('has_first_aid_kit', 'حقيبة الإسعافات الأولية'),
#         ('has_warning_triangle', 'مثلث التحذير'),
#         ('has_tools', 'عدة الأدوات')
#     ]

#     # تحديد إحداثيات الأعمدة
#     col1_x = 150 # الحافة اليمنى للعمود الأيمن
#     col2_x = 60 # الحافة اليمنى للعمود الأيسر
#     item_y = pdf.get_y()
#     row_height = 8

#     # المرور على القائمة ورسم كل عنصر في مكانه
#     for i in range(0, len(equipment_items), 2):
#         # --- العنصر في العمود الأيمن ---
#         field_right, label_right = equipment_items[i]
#         # نفترض أن الحالة هي boolean (True/False) أو (1/0)
#         status_right = bool(getattr(handover_record, field_right, False))
#         draw_equipment_item(col1_x, item_y, label_right, status_right)

#         # --- العنصر في العمود الأيسر (إذا كان موجوداً) ---
#         if i + 1 < len(equipment_items):
#             field_left, label_left = equipment_items[i + 1]
#             status_left = bool(getattr(handover_record, field_left, False))
#             draw_equipment_item(col2_x, item_y, label_left, status_left)
        
#         # الانتقال إلى الصف التالي
#         item_y += row_height

#     # ضبط الموضع الرأسي للقسم التالي
#     pdf.set_y(item_y)

 
#     # =================================
#     # 5. الملاحظات
#     # =================================
#     pdf.set_font('Amiri', '', 10)
#     pdf.set_draw_color(*DARK_GRAY)
#     pdf.set_fill_color(*LIGHT_GRAY)
#     if handover_record.notes:
#         pdf.multi_cell(0, 8, pdf.RTL_text(f"ملاحظات: {handover_record.notes}"), 1, 'R', True)
#     else:
#         pdf.multi_cell(0, 8, pdf.RTL_text(f"ملاحظات: لا يوجد ملاحظات"), 1, 'R', True)

#     pdf.ln(4)

#     # في دالة generate_handover_report_pdf...

#     # ===============================================
#     # 6. التوقيعات (النسخة النهائية مع عرض الصور)
#     # ===============================================
#     pdf.set_font('Amiri', 'B', 10)
#     pdf.set_text_color(*TEAL)
#     pdf.cell(0, 8, pdf.RTL_text("التوقيعات"), 0, 1, 'C')
#     pdf.set_font('Amiri', '', 9)
#     pdf.set_text_color(0)
#     pdf.ln(2)
    
#     # تعريف متغيرات وبيانات التوقيعات
#     # يمكنك جعل هذه الأسماء ديناميكية إذا كانت مخزنة في مكان آخر
#     supervisor_name = "المشرف: زياد محمد علي حسن"
#     driver_name = "السائق: طاهر علي محبوب علي"
    
#     # تحديد أبعاد ومواضع التوقيعات
#     SIGNATURE_BOX_Y = pdf.get_y()
#     SIGNATURE_BOX_HEIGHT = 25  # الارتفاع الكلي المخصص لكل توقيع
#     IMAGE_HEIGHT = 20          # أقصى ارتفاع لصورة التوقيع
#     SIGNATURE_X_RIGHT = 140    # بداية منطقة التوقيع اليمنى
#     SIGNATURE_X_LEFT = 30      # بداية منطقة التوقيع اليسرى
#     BOX_WIDTH = 30             # عرض كل منطقة توقيع
    
#     # --- دالة مساعدة لرسم كتلة توقيع واحدة ---
#     def draw_signature_block(x, y, name_text, signature_path):
#         # رسم اسم الموقع
#         pdf.set_xy(x, y)
#         pdf.cell(BOX_WIDTH, 7, pdf.RTL_text(name_text), 0, 1, 'R')
        
#         # التحقق من وجود مسار التوقيع
#         if signature_path:
#             # إنشاء المسار الكامل للصورة
#             full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', signature_path)
            
#             if os.path.exists(full_path):
#                 try:
#                     # عرض الصورة
#                     pdf.image(full_path, x= x + BOX_WIDTH - 75, y=y + SIGNATURE_BOX_HEIGHT - 15, h=IMAGE_HEIGHT) # توسيط الصورة قليلاً
#                 except Exception as e:
#                     # في حالة فشل تحميل الصورة، ارسم خطاً بديلاً
#                     print(f"Failed to load signature image: {e}")
#                     pdf.line(x + 5, y + SIGNATURE_BOX_HEIGHT - 5, x + BOX_WIDTH - 5, y + SIGNATURE_BOX_HEIGHT - 5)
#             else:
#                 # إذا لم يتم العثور على الملف، ارسم خطاً
#                 pdf.line(x + 5, y + SIGNATURE_BOX_HEIGHT - 5, x + BOX_WIDTH - 5, y + SIGNATURE_BOX_HEIGHT - 5)
#         else:
#             # إذا لم يكن هناك توقيع أصلاً، ارسم خطاً
#             pdf.line(x + 5, y + SIGNATURE_BOX_HEIGHT - 5, x + BOX_WIDTH - 5, y + SIGNATURE_BOX_HEIGHT - 5)
    
#     # --- رسم توقيع المشرف (على اليمين) ---
#     draw_signature_block(SIGNATURE_X_RIGHT, SIGNATURE_BOX_Y, supervisor_name, handover_record.supervisor_signature_path)
    
#     # --- رسم توقيع السائق (على اليسار) ---
#     draw_signature_block(SIGNATURE_X_LEFT, SIGNATURE_BOX_Y, driver_name, handover_record.driver_signature_path)
    
#     # النزول بمقدار ارتفاع منطقة التوقيعات لضمان عدم التداخل مع الأقسام التالية
#     pdf.set_y(SIGNATURE_BOX_Y + SIGNATURE_BOX_HEIGHT + 5)





#     # =================================
#     # 6.1 رابط الفورم الخارجي
#     # =================================
#     pdf.set_font('Amiri', '', 10)
#     pdf.set_draw_color(*DARK_GRAY)
#     pdf.set_fill_color(*LIGHT_GRAY)
#     if handover_record.form_link:
#         pdf.multi_cell(0, 8, pdf.RTL_text(f"رابط الفورم الخارجي: {handover_record.form_link}"), 1, 'R', True)
#     else:
#         pdf.multi_cell(0, 8, pdf.RTL_text(f"رابط الفورم الخارجي: لا يوجد رابط الفورم الخارجي"), 1, 'R', True)

#     pdf.ln(2)

#     # ... نهاية القسم 6 (التوقيعات) ...

#     # ===============================================
#     # 7. قسم الصور المرفقة (القسم الجديد)
#     # ===============================================
#     # نقوم بتصفية قائمة الملفات لتشمل الصور فقط
#     report_images = [img for img in images if not img.is_pdf()]

#     if report_images:
#         # إضافة صفحة جديدة خاصة بالصور المرفقة
#         pdf.add_page()
        
#         # عنوان القسم
#         pdf.set_font('Amiri', 'B', 14)
#         pdf.cell(0, 10, pdf.RTL_text("الصور المرفقة"), 0, 1, 'C')
#         pdf.ln(5)

#         # تحديد أبعاد وتخطيط الصور في الصفحة
#         PAGE_WIDTH = pdf.w - pdf.l_margin - pdf.r_margin
#         MAX_IMAGE_WIDTH = (PAGE_WIDTH / 2) - 5  # عرض صورتين في كل صف مع هامش 10
#         MAX_IMAGE_HEIGHT = 80 # أقصى ارتفاع للصورة
#         MARGIN_BETWEEN_IMAGES = 10
        
#         x_pos = pdf.l_margin # البدء من الهامش الأيسر (أو الأيمن في RTL)
#         y_pos = pdf.get_y()
        
#         # المرور على كل صورة ورسمها
#         for i, image_record in enumerate(report_images):
            
#             # logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
#             # --- التحقق من مسار الصورة ووجود الملف ---
#             image_path = os.path.join(PROJECT_DIR, 'static', image_record.get_path())
#             if not os.path.exists(image_path):
#                 # إذا لم يتم العثور على الملف، ارسم مربعاً بديلاً
#                 pdf.set_fill_color(240, 240, 240)
#                 pdf.rect(x_pos, y_pos, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, 'DF')
                
#                 pdf.set_font('Amiri', '', 8)
#                 pdf.set_xy(x_pos, y_pos + (MAX_IMAGE_HEIGHT / 2) - 5)
#                 pdf.multi_cell(MAX_IMAGE_WIDTH, 5, pdf.RTL_text(f"لم يتم العثور على الصورة\n{os.path.basename(image_path)}"), 0, 'C')
#             else:
#                 # رسم الصورة مع الحفاظ على نسبة العرض إلى الارتفاع
#                 # pdf.image(image_path, x=x_pos, y=y_pos, w=MAX_IMAGE_WIDTH, h=MAX_IMAGE_HEIGHT)
#                 pdf.image(image_path, x=x_pos, y=y_pos, w=MAX_IMAGE_WIDTH, h=0)


#             # إضافة الوصف تحت الصورة إذا كان موجوداً
#             description = image_record.get_description()
#             if description:
#                 pdf.set_font('Amiri', '', 9)
#                 pdf.set_xy(x_pos, y_pos + MAX_IMAGE_HEIGHT + 2) # وضع الوصف أسفل الصورة
#                 pdf.multi_cell(MAX_IMAGE_WIDTH, 5, pdf.RTL_text(description), 0, 'C')

#             # --- تحديث مواضع الصورة التالية ---
#             if (i + 1) % 2 == 0:  # بعد رسم صورتين، انتقل إلى صف جديد
#                 x_pos = pdf.l_margin
#                 y_pos += MAX_IMAGE_HEIGHT + 20 # الارتفاع + هامش الوصف + هامش إضافي
                
#                 # التحقق مما إذا كنا بحاجة لصفحة جديدة
#                 if y_pos + MAX_IMAGE_HEIGHT > (pdf.h - pdf.b_margin):
#                     pdf.add_page()
#                     y_pos = pdf.t_margin # البدء من الهامش العلوي للصفحة الجديدة
#             else: # الصورة التالية في نفس الصف
#                 x_pos += MAX_IMAGE_WIDTH + MARGIN_BETWEEN_IMAGES

#     # --- نهاية القسم الجديد ---


#     # ===============================================
#     # حفظ الملف في الذاكرة 
#     # ===============================================
#     pdf_buffer = BytesIO()
#     pdf.output(pdf_buffer)
#     pdf_buffer.seek(0)

#     return pdf_buffer

