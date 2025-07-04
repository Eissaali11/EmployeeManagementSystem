"""
مولد تقارير تسليم/استلام المركبات باستخدام FPDF
مع دعم كامل للنصوص العربية والاتجاه من اليمين لليسار
"""

import io
import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# تحديد المسار الحالي ومسار المشروع
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

class ArabicPDF(FPDF):
    def __init__(self):
        super().__init__()
        # استخدام المسار المطلق للخطوط
        font_path = os.path.join(PROJECT_DIR, 'static', 'fonts')
        self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'), uni=True)
        self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'), uni=True)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)
        self.set_font('Amiri', '', 12)
    
    def arabic_text(self, x, y, txt):
        reshaped_text = reshape(txt)
        bidi_text = get_display(reshaped_text)
        self.text(x, y, bidi_text)
    
    def arabic_cell(self, w, h, txt, border=0, ln=0, align='', fill=False, link=''):
        reshaped_text = reshape(txt)
        bidi_text = get_display(reshaped_text)
        self.cell(w, h, bidi_text, border, ln, align, fill, link)

def generate_handover_report_pdf(vehicle, handover_record):
    """
    إنشاء تقرير تسليم/استلام المركبة باستخدام FPDF
    مع دعم كامل للنصوص العربية
    """
    pdf = ArabicPDF()
    pdf.add_page()
    
    # إضافة العنوان
    pdf.set_font('Amiri', 'B', 16)
    pdf.arabic_cell(0, 10, 'وثيقة تسليم واستلام المركبة', ln=True, align='C')
    pdf.set_font('Amiri', '', 12)
    pdf.arabic_cell(0, 10, f'المركبة: {vehicle.plate_number}', ln=True, align='C')
    pdf.arabic_cell(0, 10, datetime.now().strftime('%Y-%m-%d %H:%M'), ln=True, align='C')
    pdf.ln(5)
    
    # معلومات الوثيقة
    pdf.set_font('Amiri', 'B', 12)
    pdf.arabic_cell(0, 10, 'معلومات الوثيقة:', ln=True)
    pdf.set_font('Amiri', '', 12)
    pdf.arabic_cell(95, 10, f'رقم الوثيقة: #{handover_record.id}')
    operation_type = "تسليم" if handover_record.handover_type == "delivery" else "استلام"
    pdf.arabic_cell(95, 10, f'نوع العملية: {operation_type}', ln=True)
    pdf.ln(5)
    
    # معلومات المركبة
    pdf.set_font('Amiri', 'B', 12)
    pdf.arabic_cell(0, 10, 'معلومات المركبة:', ln=True)
    pdf.set_font('Amiri', '', 12)
    vehicle_info = [
        ('رقم اللوحة:', vehicle.plate_number),
        ('الماركة:', vehicle.make or 'غير محدد'),
        ('الموديل:', vehicle.model or 'غير محدد'),
        ('السنة:', str(vehicle.year) if vehicle.year else 'غير محدد'),
        ('اللون:', vehicle.color or 'غير محدد')
    ]
    for label, value in vehicle_info:
        pdf.arabic_cell(95, 10, f'{label} {value}', ln=True)
    pdf.ln(5)
    
    # تفاصيل العملية
    pdf.set_font('Amiri', 'B', 12)
    pdf.arabic_cell(0, 10, 'تفاصيل العملية:', ln=True)
    pdf.set_font('Amiri', '', 12)
    handover_info = [
        ('التاريخ:', handover_record.handover_date.strftime('%Y-%m-%d') if handover_record.handover_date else 'غير محدد'),
        ('الوقت:', handover_record.handover_time.strftime('%H:%M') if hasattr(handover_record, 'handover_time') and handover_record.handover_time else 'غير محدد'),
        ('اسم الشخص:', handover_record.person_name or 'غير محدد'),
        # ('رقم الهاتف:', handover_record.phone_number or 'غير محدد'),
        ('قراءة العداد:', f'{handover_record.mileage} كم' if handover_record.mileage else 'غير محدد'),
        ('مستوى الوقود:', f'{handover_record.fuel_level}%' if handover_record.fuel_level else 'غير محدد')
    ]
    for label, value in handover_info:
        pdf.arabic_cell(95, 10, f'{label} {value}', ln=True)
    pdf.ln(5)
    
    # معدات المركبة
    pdf.set_font('Amiri', 'B', 12)
    pdf.arabic_cell(0, 10, 'معدات المركبة:', ln=True)
    pdf.set_font('Amiri', '', 12)
    equipment_items = [
        ('has_spare_tire', 'الإطار الاحتياطي'),
        ('has_fire_extinguisher', 'طفاية الحريق'),
        ('has_first_aid_kit', 'حقيبة الإسعافات الأولية'),
        ('has_warning_triangle', 'مثلث التحذير'),
        ('has_tools', 'عدة الأدوات')
    ]
    for field, label in equipment_items:
        status = getattr(handover_record, field, None)
        status_text = "متوفر" if status == 1 else "غير متوفر"
        pdf.arabic_cell(95, 10, f'{label}: {status_text}', ln=True)
    pdf.ln(5)
    
    # الملاحظات
    if handover_record.notes:
        pdf.set_font('Amiri', 'B', 12)
        pdf.arabic_cell(0, 10, 'ملاحظات إضافية:', ln=True)
        pdf.set_font('Amiri', '', 12)
        pdf.multi_cell(0, 10, reshape(handover_record.notes))
        pdf.ln(5)
    
    # التوقيعات
    pdf.set_font('Amiri', 'B', 12)
    pdf.arabic_cell(95, 10, 'المُسلِّم:', ln=0)
    pdf.arabic_cell(95, 10, 'المُستلِم:', ln=True)
    pdf.set_font('Amiri', '', 12)
    pdf.arabic_cell(95, 10, 'الاسم: ___________________', ln=0)
    pdf.arabic_cell(95, 10, 'الاسم: ___________________', ln=True)
    pdf.arabic_cell(95, 10, 'التوقيع: _________________', ln=0)
    pdf.arabic_cell(95, 10, 'التوقيع: _________________', ln=True)
    pdf.arabic_cell(95, 10, 'التاريخ: _________________', ln=0)
    pdf.arabic_cell(95, 10, 'التاريخ: _________________', ln=True)
    pdf.ln(10)
    
    # التذييل
    pdf.set_font('Amiri', '', 10)
    pdf.arabic_cell(0, 10, 'نُظم - نظام إدارة المركبات المتقدم', ln=True, align='C')
    pdf.arabic_cell(0, 10, f'تم إنشاء هذه الوثيقة تلقائياً في {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')
    
    if handover_record.form_link:
        pdf.ln(5)
        pdf.set_font('Amiri', 'B', 10)
        pdf.arabic_cell(0, 10, 'رابط النموذج الإلكتروني:', ln=True, align='C')
        pdf.set_font('Amiri', '', 10)
        pdf.arabic_cell(0, 10, handover_record.form_link, ln=True, align='C')
    
    # حفظ الملف في الذاكرة
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer 