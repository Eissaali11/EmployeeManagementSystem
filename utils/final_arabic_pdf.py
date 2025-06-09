"""
مولد PDF نهائي للورشة مع دعم كامل للنصوص العربية
يستخدم FPDF مع معالجة خاصة للنصوص العربية
"""

from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import io
import os

class FinalArabicPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def arabic_text(self, text):
        """معالجة النص العربي للعرض الصحيح"""
        if not text:
            return ""
        
        try:
            text_str = str(text)
            # إعادة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(text_str)
            # تطبيق خوارزمية الاتجاه الثنائي
            bidi_text = get_display(reshaped_text)
            # إزالة الأحرف التي قد تسبب مشاكل في PDF
            clean_text = ''.join(char for char in str(bidi_text) if ord(char) < 256 or char.isalnum())
            return clean_text
        except Exception as e:
            print(f"خطأ في معالجة النص العربي: {e}")
            # تحويل إلى نص لاتيني كبديل
            return self.to_latin(str(text))
    
    def to_latin(self, text):
        """تحويل النص العربي إلى أحرف لاتينية"""
        arabic_map = {
            'ا': 'a', 'أ': 'a', 'إ': 'a', 'آ': 'aa',
            'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
            'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'th',
            'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
            'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'th',
            'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
            'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a',
            'ة': 'h', 'ء': 'a', 'ؤ': 'w', 'ئ': 'y',
            # ترجمة كلمات شائعة
            'تقرير': 'Report', 'سجلات': 'Records', 'الورشة': 'Workshop',
            'معلومات': 'Information', 'المركبة': 'Vehicle',
            'رقم': 'Number', 'اللوحة': 'Plate', 'الصنع': 'Make',
            'الموديل': 'Model', 'السنة': 'Year', 'اللون': 'Color',
            'الحالة': 'Status', 'تاريخ': 'Date', 'الدخول': 'Entry',
            'الخروج': 'Exit', 'سبب': 'Reason', 'الإصلاح': 'Repair',
            'التكلفة': 'Cost', 'اسم': 'Name', 'الفني': 'Technician',
            'المسؤول': 'Responsible', 'صيانة': 'Maintenance',
            'دورية': 'Periodic', 'عطل': 'Breakdown', 'حادث': 'Accident',
            'قيد': 'In', 'التنفيذ': 'Progress', 'تم': 'Completed',
            'بانتظار': 'Pending', 'الموافقة': 'Approval',
            'ملخص': 'Summary', 'الإحصائيات': 'Statistics',
            'عدد': 'Count', 'إجمالي': 'Total', 'أيام': 'Days',
            'متوسط': 'Average', 'لكل': 'Per', 'سجل': 'Record',
            'مدة': 'Duration', 'ريال': 'SAR', 'يوم': 'Day',
            'متاح': 'Available', 'مؤجر': 'Rented', 'في': 'In',
            'ما': 'Still', 'زالت': 'In', 'غير': 'Not',
            'محدد': 'Specified', 'نظام': 'System', 'نُظم': 'NUZUM',
            'لإدارة': 'Management', 'المركبات': 'Vehicles'
        }
        
        result = text
        for arabic, latin in arabic_map.items():
            result = result.replace(arabic, latin)
        
        # تنظيف النص من الأحرف الخاصة
        clean_result = ''.join(char for char in result if char.isalnum() or char in ' .-_:()[]{}/@#$%^&*+=<>?!,;')
        return clean_result[:100]  # تحديد الطول
    
    def safe_cell(self, w, h, txt='', border=1, ln=0, align='C', fill=False):
        """خلية آمنة مع معالجة النصوص العربية"""
        try:
            processed_text = self.arabic_text(txt)
            self.cell(w, h, processed_text, border, ln, align, fill)
        except Exception as e:
            print(f"خطأ في الخلية: {e}")
            self.cell(w, h, str(txt)[:50], border, ln, align, fill)

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء تقرير ورشة نهائي باللغة العربية"""
    
    try:
        print("بدء إنشاء تقرير PDF النهائي...")
        
        # إنشاء PDF
        pdf = FinalArabicPDF()
        pdf.add_page()
        
        # إضافة الشعار
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
        
        # عنوان التقرير
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(0, 51, 102)
        title = f"Workshop Records Report - Vehicle: {vehicle.plate_number}"
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
        
        # معلومات المركبة
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, "Vehicle Information", 0, 1, 'C')
        pdf.ln(5)
        
        # جدول معلومات المركبة
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        vehicle_info = [
            ("Plate Number", str(vehicle.plate_number)),
            ("Make & Model", f"{vehicle.make} {vehicle.model}"),
            ("Year", str(vehicle.year)),
            ("Color", str(vehicle.color)),
            ("Current Status", get_status_english(vehicle.status))
        ]
        
        for label, value in vehicle_info:
            pdf.set_fill_color(240, 240, 240)
            pdf.safe_cell(70, 7, label, 1, 0, 'C', True)
            pdf.set_fill_color(255, 255, 255)
            pdf.safe_cell(100, 7, value, 1, 1, 'C', True)
        
        pdf.ln(8)
        
        # سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(0, 51, 102)
            records_title = f"Workshop Records ({len(workshop_records)} records)"
            pdf.cell(0, 8, records_title, 0, 1, 'C')
            pdf.ln(5)
            
            # رأس جدول السجلات
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(0, 51, 102)
            pdf.set_text_color(255, 255, 255)
            
            headers = ["Entry Date", "Exit Date", "Reason", "Status", "Cost (SAR)", "Workshop"]
            col_widths = [30, 30, 35, 35, 25, 35]
            
            for i, header in enumerate(headers):
                pdf.safe_cell(col_widths[i], 8, header, 1, 0, 'C', True)
            pdf.ln()
            
            # بيانات السجلات
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(0, 0, 0)
            
            total_cost = 0
            total_days = 0
            
            for i, record in enumerate(workshop_records):
                # تلوين الصفوف
                if i % 2 == 0:
                    pdf.set_fill_color(249, 249, 249)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                # البيانات
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else "Not Set"
                exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else "Still in Workshop"
                reason = get_reason_english(record.reason)
                status = get_repair_status_english(record.repair_status)
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                workshop_name = record.workshop_name if record.workshop_name else "Not Specified"
                
                pdf.safe_cell(col_widths[0], 6, entry_date, 1, 0, 'C', True)
                pdf.safe_cell(col_widths[1], 6, exit_date, 1, 0, 'C', True)
                pdf.safe_cell(col_widths[2], 6, reason, 1, 0, 'C', True)
                pdf.safe_cell(col_widths[3], 6, status, 1, 0, 'C', True)
                pdf.safe_cell(col_widths[4], 6, f"{cost:,.0f}", 1, 0, 'C', True)
                pdf.safe_cell(col_widths[5], 6, workshop_name, 1, 1, 'C', True)
                
                # حساب الأيام
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
            
            pdf.ln(8)
            
            # الإحصائيات
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 8, "Summary Statistics", 0, 1, 'C')
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            
            # حساب المتوسطات
            avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
            avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
            
            stats = [
                ("Total Records", str(len(workshop_records))),
                ("Total Cost", f"{total_cost:,.0f} SAR"),
                ("Total Days in Workshop", f"{total_days} days"),
                ("Average Cost per Record", f"{avg_cost:,.0f} SAR"),
                ("Average Repair Duration", f"{avg_days:.1f} days")
            ]
            
            for label, value in stats:
                pdf.set_fill_color(230, 242, 255)
                pdf.safe_cell(80, 7, label, 1, 0, 'C', True)
                pdf.set_fill_color(255, 255, 255)
                pdf.safe_cell(60, 7, value, 1, 1, 'C', True)
        
        else:
            # لا توجد سجلات
            pdf.set_font('Arial', '', 12)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, "No workshop records available for this vehicle", 0, 1, 'C')
        
        # التذييل
        pdf.ln(15)
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(128, 128, 128)
        footer_text = f"Generated by NUZUM Vehicle Management System - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        pdf.cell(0, 8, footer_text, 0, 1, 'C')
        
        # حفظ PDF
        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        pdf_output.write(pdf_content)
        pdf_output.seek(0)
        
        print("تم إنشاء تقرير PDF النهائي بنجاح!")
        return pdf_output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF النهائي: {str(e)}")
        # إنشاء تقرير بسيط كبديل
        return create_simple_report(vehicle, workshop_records)

def create_simple_report(vehicle, workshop_records):
    """إنشاء تقرير بسيط كبديل"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Vehicle Report: {vehicle.plate_number}", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Make: {vehicle.make}", 0, 1)
        pdf.cell(0, 8, f"Model: {vehicle.model}", 0, 1)
        pdf.cell(0, 8, f"Year: {vehicle.year}", 0, 1)
        pdf.cell(0, 8, f"Color: {vehicle.color}", 0, 1)
        pdf.cell(0, 8, f"Status: {vehicle.status}", 0, 1)
        pdf.ln(10)
        
        if workshop_records:
            pdf.cell(0, 8, f"Workshop Records: {len(workshop_records)} records", 0, 1)
            total_cost = sum(float(r.cost) if r.cost else 0 for r in workshop_records)
            pdf.cell(0, 8, f"Total Cost: {total_cost:,.2f} SAR", 0, 1)
        
        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        pdf_output.write(pdf_content)
        pdf_output.seek(0)
        
        return pdf_output.getvalue()
    except Exception as e:
        print(f"خطأ في إنشاء التقرير البسيط: {e}")
        return b"PDF Error"

def get_status_english(status):
    """ترجمة حالة المركبة للإنجليزية"""
    status_map = {
        'available': 'Available',
        'rented': 'Rented',
        'in_workshop': 'In Workshop', 
        'accident': 'Accident'
    }
    return status_map.get(status, status)

def get_reason_english(reason):
    """ترجمة سبب دخول الورشة للإنجليزية"""
    reason_map = {
        'maintenance': 'Maintenance',
        'breakdown': 'Breakdown',
        'accident': 'Accident'
    }
    return reason_map.get(reason, reason if reason else "Not Specified")

def get_repair_status_english(status):
    """ترجمة حالة الإصلاح للإنجليزية"""
    status_map = {
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'pending_approval': 'Pending Approval'
    }
    return status_map.get(status, status if status else "Not Specified")