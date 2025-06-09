"""
مولد PDF محسّن للورشة باستخدام FPDF مع دعم كامل للنصوص العربية
يستخدم arabic-reshaper و python-bidi مع خطوط آمنة
"""

from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import io
import os

class ArabicPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def format_arabic(self, text):
        """تنسيق النص العربي للعرض الصحيح"""
        if not text:
            return ""
        
        try:
            text_str = str(text)
            # إعادة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(text_str)
            # تطبيق خوارزمية الاتجاه الثنائي
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"خطأ في تنسيق النص العربي: {e}")
            return str(text)
    
    def add_arabic_text(self, x, y, text, font_size=12, font_style=''):
        """إضافة نص عربي منسق إلى PDF"""
        try:
            formatted_text = self.format_arabic(text)
            self.set_xy(x, y)
            if font_style == 'B':
                self.set_font('Arial', 'B', font_size)
            else:
                self.set_font('Arial', '', font_size)
            self.cell(0, 8, str(formatted_text), 0, 1, 'C')
        except Exception as e:
            print(f"خطأ في إضافة النص العربي: {e}")
            # العودة للنص الأصلي
            self.set_xy(x, y)
            self.set_font('Arial', '', font_size)
            self.cell(0, 8, str(text), 0, 1, 'C')
    
    def add_arabic_cell(self, w, h, text, border=1, ln=0, align='C', fill=False):
        """خلية مع نص عربي منسق"""
        try:
            formatted_text = self.format_arabic(text)
            self.cell(w, h, str(formatted_text), border, ln, align, fill)
        except Exception as e:
            print(f"خطأ في إضافة خلية عربية: {e}")
            self.cell(w, h, str(text), border, ln, align, fill)

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء تقرير ورشة باللغة العربية مع دعم كامل للنصوص العربية"""
    
    try:
        print("بدء إنشاء تقرير PDF بالعربية...")
        
        # إنشاء PDF
        pdf = ArabicPDF()
        pdf.add_page()
        
        # إضافة الشعار إذا كان متوفراً
        try:
            logo_path = 'attached_assets/ChatGPT Image Jun 8, 2025, 05_34_10 PM_1749393284624.png'
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=85, y=10, w=40, h=25)
                pdf.ln(30)
            else:
                pdf.ln(10)
        except Exception as e:
            print(f"تعذر إضافة الشعار: {e}")
            pdf.ln(10)
        
        # عنوان التقرير الرئيسي
        pdf.set_font('Arial', 'B', 20)
        pdf.set_text_color(0, 51, 102)  # أزرق داكن
        title = f"تقرير سجلات الورشة للمركبة: {vehicle.plate_number}"
        pdf.add_arabic_text(10, pdf.get_y(), title, 20, 'B')
        pdf.ln(15)
        
        # معلومات المركبة
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 51, 102)
        pdf.add_arabic_text(10, pdf.get_y(), "معلومات المركبة", 16, 'B')
        pdf.ln(10)
        
        # جدول معلومات المركبة
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        vehicle_info = [
            ("رقم اللوحة", str(vehicle.plate_number)),
            ("الصنع والموديل", f"{vehicle.make} {vehicle.model}"),
            ("سنة الصنع", str(vehicle.year)),
            ("اللون", str(vehicle.color)),
            ("الحالة الحالية", get_status_arabic(vehicle.status))
        ]
        
        for label, value in vehicle_info:
            # تسمية الحقل
            pdf.set_fill_color(240, 240, 240)
            pdf.add_arabic_cell(70, 8, label, 1, 0, 'C', True)
            # قيمة الحقل
            pdf.set_fill_color(255, 255, 255)
            pdf.add_arabic_cell(100, 8, value, 1, 1, 'C', True)
        
        pdf.ln(10)
        
        # سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(0, 51, 102)
            records_title = f"سجلات الورشة ({len(workshop_records)} سجل)"
            pdf.add_arabic_text(10, pdf.get_y(), records_title, 16, 'B')
            pdf.ln(10)
            
            # رأس جدول السجلات
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(0, 51, 102)
            pdf.set_text_color(255, 255, 255)
            
            headers = [
                "تاريخ الدخول",
                "تاريخ الخروج", 
                "سبب الدخول",
                "حالة الإصلاح",
                "التكلفة (ريال)",
                "اسم الورشة"
            ]
            
            col_widths = [30, 30, 35, 35, 25, 35]
            
            for i, header in enumerate(headers):
                pdf.add_arabic_cell(col_widths[i], 8, header, 1, 0, 'C', True)
            pdf.ln()
            
            # بيانات السجلات
            pdf.set_font('Arial', '', 9)
            pdf.set_text_color(0, 0, 0)
            
            total_cost = 0
            total_days = 0
            
            for i, record in enumerate(workshop_records):
                # تلوين الصفوف بالتناوب
                if i % 2 == 0:
                    pdf.set_fill_color(249, 249, 249)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                # تاريخ الدخول
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else "غير محدد"
                pdf.add_arabic_cell(col_widths[0], 7, entry_date, 1, 0, 'C', True)
                
                # تاريخ الخروج
                exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else "ما زالت في الورشة"
                pdf.add_arabic_cell(col_widths[1], 7, exit_date, 1, 0, 'C', True)
                
                # سبب الدخول
                reason = get_reason_arabic(record.reason)
                pdf.add_arabic_cell(col_widths[2], 7, reason, 1, 0, 'C', True)
                
                # حالة الإصلاح
                status = get_repair_status_arabic(record.repair_status)
                pdf.add_arabic_cell(col_widths[3], 7, status, 1, 0, 'C', True)
                
                # التكلفة
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                pdf.add_arabic_cell(col_widths[4], 7, f"{cost:,.0f}", 1, 0, 'C', True)
                
                # اسم الورشة
                workshop_name = record.workshop_name if record.workshop_name else "غير محدد"
                pdf.add_arabic_cell(col_widths[5], 7, workshop_name, 1, 1, 'C', True)
                
                # حساب الأيام
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
            
            pdf.ln(10)
            
            # الإحصائيات
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(0, 51, 102)
            pdf.add_arabic_text(10, pdf.get_y(), "ملخص الإحصائيات", 16, 'B')
            pdf.ln(10)
            
            pdf.set_font('Arial', '', 12)
            pdf.set_text_color(0, 0, 0)
            
            # حساب المتوسطات
            avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
            avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
            
            stats = [
                ("عدد السجلات", str(len(workshop_records))),
                ("إجمالي التكلفة", f"{total_cost:,.0f} ريال"),
                ("إجمالي أيام الإصلاح", f"{total_days} يوم"),
                ("متوسط التكلفة لكل سجل", f"{avg_cost:,.0f} ريال"),
                ("متوسط مدة الإصلاح", f"{avg_days:.1f} يوم")
            ]
            
            for label, value in stats:
                pdf.set_fill_color(230, 242, 255)
                pdf.add_arabic_cell(80, 8, label, 1, 0, 'C', True)
                pdf.set_fill_color(255, 255, 255)
                pdf.add_arabic_cell(60, 8, value, 1, 1, 'C', True)
        
        else:
            # لا توجد سجلات
            pdf.set_font('Arial', '', 14)
            pdf.set_text_color(128, 128, 128)
            pdf.add_arabic_text(10, pdf.get_y(), "لا توجد سجلات ورشة متاحة لهذه المركبة", 14)
        
        # التذييل
        pdf.ln(20)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(128, 128, 128)
        footer_text = f"تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        pdf.add_arabic_text(10, pdf.get_y(), footer_text, 10)
        
        # حفظ PDF
        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        pdf_output.write(pdf_content)
        pdf_output.seek(0)
        
        print("تم إنشاء تقرير PDF بالعربية بنجاح!")
        return pdf_output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF العربي: {str(e)}")
        # العودة للمولد الآمن في حالة الفشل
        from utils.safe_workshop_pdf import generate_workshop_pdf as safe_generate
        return safe_generate(vehicle, workshop_records)

def get_status_arabic(status):
    """ترجمة حالة المركبة للعربية"""
    status_map = {
        'available': 'متاح',
        'rented': 'مؤجر', 
        'in_workshop': 'في الورشة',
        'accident': 'حادث'
    }
    return status_map.get(status, status)

def get_reason_arabic(reason):
    """ترجمة سبب دخول الورشة للعربية"""
    reason_map = {
        'maintenance': 'صيانة دورية',
        'breakdown': 'عطل',
        'accident': 'حادث'
    }
    return reason_map.get(reason, reason if reason else "غير محدد")

def get_repair_status_arabic(status):
    """ترجمة حالة الإصلاح للعربية"""
    status_map = {
        'in_progress': 'قيد التنفيذ',
        'completed': 'تم الإصلاح',
        'pending_approval': 'بانتظار الموافقة'
    }
    return status_map.get(status, status if status else "غير محدد")