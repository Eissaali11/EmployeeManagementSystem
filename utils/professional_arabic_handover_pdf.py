"""
مولد PDF محسن لتقارير تسليم/استلام المركبات باستخدام نفس خط beIN Normal المحسن
يستخدم نفس النظام المطور في نظام الرواتب مع دعم كامل للنصوص العربية
"""

import os
import io
from datetime import datetime
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

class ArabicHandoverPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.arabic_font_available = False
        self.selected_font_path = None
        # محاولة إضافة الخط العربي
        self.add_arabic_font()
        
    def add_arabic_font(self):
        """إضافة نفس خط beIN Normal المستخدم في نظام الرواتب"""
        try:
            # تجربة المسارات المختلفة للخط العربي (نفس النظام المستخدم في الرواتب)
            font_paths = [
                os.path.join('static', 'fonts', 'beIN Normal .ttf'),  # نفس الخط المستخدم في نظام التسليم
                os.path.join('static', 'fonts', 'beIN-Normal.ttf'),
                os.path.join('static', 'fonts', 'Tajawal-Regular.ttf'),
                os.path.join('static', 'fonts', 'Cairo.ttf'),
                os.path.join('utils', 'beIN-Normal.ttf'),
                'Cairo.ttf'  # الخط الموجود في المجلد الجذر
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        self.add_font('Arabic', '', font_path, uni=True)
                        self.arabic_font_available = True
                        self.selected_font_path = font_path
                        print(f"استخدام خط التسليم والاستلام: {font_path}")
                        return
                    except Exception as e:
                        print(f"فشل في تحميل الخط {font_path}: {e}")
                        continue
            
            # إذا لم نجد أي خط، استخدام الخط الافتراضي
            self.arabic_font_available = False
            self.selected_font_path = None
            print("لم يتم العثور على خط عربي، سيتم استخدام الخط الافتراضي")
            
        except Exception as e:
            print(f"خطأ في إضافة الخط العربي: {e}")
            self.arabic_font_available = False

    def safe_cell(self, w, h, text='', border=0, ln=0, align='L', fill=False):
        """كتابة نص آمن مع معالجة للنصوص العربية"""
        try:
            if text and isinstance(text, str):
                # معالجة النص العربي
                reshaped_text = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped_text)
                self.cell(w, h, bidi_text, border, ln, align, fill)
            else:
                self.cell(w, h, str(text) if text else '', border, ln, align, fill)
        except Exception as e:
            print(f"خطأ في كتابة النص: {e}")
            # fallback to plain text
            self.cell(w, h, str(text) if text else '', border, ln, align, fill)

def generate_handover_pdf_with_bein_font(handover, vehicle):
    """
    إنشاء PDF لتقرير تسليم/استلام باستخدام نفس خط beIN Normal المحسن من نظام الرواتب
    
    Args:
        handover: سجل التسليم/الاستلام
        vehicle: بيانات المركبة
    
    Returns:
        BytesIO: ملف PDF
    """
    try:
        # إنشاء كائن PDF
        pdf = ArabicHandoverPDF()
        pdf.add_page()
        
        # تحديد الخط حسب توفر الخط العربي
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 16)
        else:
            pdf.set_font('Arial', 'B', 16)
        
        # رأس المستند
        pdf.set_fill_color(41, 128, 185)  # لون أزرق
        pdf.set_text_color(255, 255, 255)  # نص أبيض
        pdf.safe_cell(0, 15, 'تقرير تسليم واستلام المركبة', 1, 1, 'C')
        pdf.set_fill_color(255, 255, 255)  # إعادة تعيين لون الخلفية
        pdf.set_text_color(0, 0, 0)  # إعادة تعيين لون النص
        pdf.ln(5)
        
        # معلومات المركبة الأساسية
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 12)
        else:
            pdf.set_font('Arial', 'B', 12)
            
        # معلومات المركبة في جدول
        pdf.set_fill_color(52, 152, 219)  # خلفية أزرق فاتح
        pdf.set_text_color(255, 255, 255)
        pdf.safe_cell(0, 10, 'معلومات المركبة', 1, 1, 'C', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        # جدول معلومات المركبة
        vehicle_info = [
            ('رقم اللوحة', getattr(vehicle, 'plate_number', 'غير محدد')),
            ('الماركة', getattr(vehicle, 'make', 'غير محدد')),
            ('الموديل', getattr(vehicle, 'model', 'غير محدد')),
            ('السنة', str(getattr(vehicle, 'year', 'غير محدد'))),
            ('اللون', getattr(vehicle, 'color', 'غير محدد'))
        ]
        
        for label, value in vehicle_info:
            pdf.set_fill_color(245, 245, 245)  # خلفية رمادي فاتح
            pdf.safe_cell(50, 8, label, 1, 0, 'C', fill=True)
            pdf.set_fill_color(255, 255, 255)  # خلفية بيضاء
            pdf.safe_cell(0, 8, value, 1, 1, 'R')
        
        pdf.ln(5)
        
        # معلومات التسليم/الاستلام
        pdf.set_fill_color(46, 204, 113)  # أخضر
        pdf.set_text_color(255, 255, 255)
        handover_type = 'تسليم' if getattr(handover, 'handover_type', '') == 'delivery' else 'استلام'
        pdf.safe_cell(0, 10, f'بيانات {handover_type}', 1, 1, 'C', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        # جدول بيانات التسليم
        handover_info = [
            ('نوع العملية', handover_type),
            ('التاريخ', getattr(handover, 'handover_date', datetime.now()).strftime('%Y/%m/%d') if getattr(handover, 'handover_date', None) else 'غير محدد'),
            ('اسم المستلم/المُسلم', getattr(handover, 'person_name', 'غير محدد')),
            ('رقم الهوية/الإقامة', getattr(handover, 'id_number', 'غير محدد')),
            ('رقم الهاتف', getattr(handover, 'phone_number', 'غير محدد')),
            ('قراءة العداد', f"{getattr(handover, 'mileage', 0):,} كم" if getattr(handover, 'mileage', None) else 'غير محدد'),
            ('مستوى الوقود', getattr(handover, 'fuel_level', 'غير محدد')),
            ('حالة المركبة', getattr(handover, 'vehicle_condition', 'غير محدد'))
        ]
        
        for label, value in handover_info:
            pdf.set_fill_color(245, 245, 245)
            pdf.safe_cell(50, 8, label, 1, 0, 'C', fill=True)
            pdf.set_fill_color(255, 255, 255)
            pdf.safe_cell(0, 8, value, 1, 1, 'R')
        
        pdf.ln(5)
        
        # قائمة التحقق من المعدات
        pdf.set_fill_color(241, 196, 15)  # أصفر
        pdf.set_text_color(255, 255, 255)
        pdf.safe_cell(0, 10, 'قائمة التحقق من المعدات', 1, 1, 'C', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        equipment_checks = [
            ('إطار احتياطي', getattr(handover, 'has_spare_tire', False)),
            ('طفاية حريق', getattr(handover, 'has_fire_extinguisher', False)),
            ('حقيبة إسعافات أولية', getattr(handover, 'has_first_aid_kit', False)),
            ('مثلث تحذير', getattr(handover, 'has_warning_triangle', False)),
            ('أدوات الصيانة', getattr(handover, 'has_tools', False))
        ]
        
        for equipment, available in equipment_checks:
            pdf.set_fill_color(245, 245, 245)
            pdf.safe_cell(50, 8, equipment, 1, 0, 'C', fill=True)
            pdf.set_fill_color(255, 255, 255)
            status = '✓ متوفر' if available else '✗ غير متوفر'
            status_color = (46, 204, 113) if available else (231, 76, 60)
            pdf.set_text_color(*status_color)
            pdf.safe_cell(0, 8, status, 1, 1, 'C')
            pdf.set_text_color(0, 0, 0)
        
        # الملاحظات
        notes = getattr(handover, 'notes', '')
        if notes:
            pdf.ln(5)
            pdf.set_fill_color(155, 89, 182)  # بنفسجي
            pdf.set_text_color(255, 255, 255)
            pdf.safe_cell(0, 10, 'ملاحظات إضافية', 1, 1, 'C', fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)
            
            # تقسيم النص الطويل
            if pdf.arabic_font_available:
                pdf.set_font('Arabic', '', 10)
            else:
                pdf.set_font('Arial', '', 10)
            pdf.safe_cell(0, 8, notes, 1, 1, 'R')
        
        # معلومات تقنية في التذييل
        pdf.ln(10)
        pdf.set_fill_color(236, 240, 241)  # رمادي فاتح جداً
        pdf.set_text_color(127, 140, 141)  # رمادي
        
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 8)
        else:
            pdf.set_font('Arial', '', 8)
        
        # تاريخ الإنشاء
        creation_date = f'تاريخ الإنشاء: {datetime.now().strftime("%Y/%m/%d %H:%M")}'
        pdf.safe_cell(0, 6, creation_date, 1, 1, 'C', fill=True)
        
        # رسالة أسفل الصفحة
        pdf.safe_cell(0, 6, 'هذا المستند مُولد إلكترونياً من نظام نُظم لإدارة المركبات', 1, 1, 'C', fill=True)
        
        # معلومات الخط المُستخدم
        if hasattr(pdf, 'selected_font_path') and pdf.selected_font_path:
            pdf.set_font('Arial', '', 6)
            pdf.set_text_color(150, 150, 150)
            font_name = os.path.basename(pdf.selected_font_path)
            pdf.cell(0, 4, f'Font: {font_name}', 0, 1, 'C')
        
        # إنشاء buffer وإرجاع PDF
        pdf_buffer = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        
        # التأكد من أن المحتوى bytes وليس string
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        
        pdf_buffer.write(pdf_content)
        pdf_buffer.seek(0)
        
        print(f"تم إنشاء PDF تسليم واستلام محسن بحجم {len(pdf_content)} بايت")
        return pdf_buffer
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF التسليم والاستلام: {e}")
        import traceback
        traceback.print_exc()
        raise