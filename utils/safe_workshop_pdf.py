"""
مولد PDF آمن لتقارير سجلات الورشة
يعمل بدون مشاكل ترميز أو خطوط خارجية
"""

from fpdf import FPDF
from datetime import datetime
from io import BytesIO

class SafeWorkshopPDF(FPDF):
    """فئة PDF آمنة لتقارير الورشة"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def safe_text(self, text):
        """تحويل آمن للنصوص العربية مع ترجمة المعاني"""
        if not text:
            return ""
        
        text_str = str(text)
        
        # ترجمة المصطلحات العربية المشتركة
        translations = {
            # معلومات المركبة
            'رقم اللوحة': 'Plate Number',
            'لوحة': 'Plate',
            'الصنع': 'Make',
            'الموديل': 'Model', 
            'السنة': 'Year',
            'اللون': 'Color',
            'الحالة': 'Status',
            'متاح': 'Available',
            'مؤجر': 'Rented',
            'في الورشة': 'In Workshop',
            'حادث': 'Accident',
            
            # سجلات الورشة
            'سجلات الورشة': 'Workshop Records',
            'تاريخ الدخول': 'Entry Date',
            'تاريخ الخروج': 'Exit Date', 
            'سبب الدخول': 'Entry Reason',
            'حالة الإصلاح': 'Repair Status',
            'التكلفة': 'Cost',
            'اسم الورشة': 'Workshop Name',
            'الفني المسؤول': 'Technician',
            'صيانة دورية': 'Maintenance',
            'عطل': 'Breakdown',
            'قيد التنفيذ': 'In Progress',
            'تم الإصلاح': 'Completed',
            'بانتظار الموافقة': 'Pending Approval',
            'ما زالت في الورشة': 'Still in Workshop',
            'غير محدد': 'Not Specified',
            
            # إحصائيات
            'ملخص الإحصائيات': 'Summary Statistics',
            'عدد السجلات': 'Total Records',
            'إجمالي التكلفة': 'Total Cost',
            'إجمالي أيام الإصلاح': 'Total Days in Workshop',
            'متوسط التكلفة لكل سجل': 'Average Cost per Record',
            'متوسط مدة الإصلاح': 'Average Repair Duration',
            'ريال': 'SAR',
            'يوم': 'days',
            
            # عام
            'تقرير': 'Report',
            'المركبة': 'Vehicle',
            'السيارة': 'Vehicle',
            'معلومات': 'Information',
            'التاريخ': 'Date',
            'نظام نُظم': 'NUZUM System'
        }
        
        # البحث عن ترجمة مباشرة
        for arabic, english in translations.items():
            if arabic in text_str:
                text_str = text_str.replace(arabic, english)
        
        # تحويل الأحرف العربية المتبقية
        arabic_to_latin = {
            'ا': 'a', 'أ': 'a', 'إ': 'a', 'آ': 'aa',
            'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
            'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'th',
            'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
            'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'th',
            'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
            'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a',
            'ة': 'h', 'ء': 'a', 'ؤ': 'w', 'ئ': 'y'
        }
        
        result = ""
        for char in text_str:
            if char in arabic_to_latin:
                result += arabic_to_latin[char]
            elif char.isalnum() or char in ' .-_:()[]{}/@#$%^&*+=<>?!,;':
                result += char
            else:
                result += ' '
        
        result = ' '.join(result.split())
        return result[:120]
        
    def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
        """خلية آمنة مع معالجة الأخطاء"""
        try:
            safe_txt = self.safe_text(txt)
            self.cell(w, h, safe_txt, border, ln, align, fill)
        except Exception:
            try:
                self.cell(w, h, f'[{len(str(txt))} chars]', border, ln, align, fill)
            except:
                self.cell(w, h, '[TEXT]', border, ln, align, fill)

def generate_workshop_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير ورشة آمن بدون مشاكل ترميز
    """
    try:
        pdf = SafeWorkshopPDF()
        pdf.add_page()
        
        # الرأس
        pdf.set_fill_color(52, 73, 94)  # أزرق داكن
        pdf.rect(0, 0, 210, 40, 'F')
        
        # شعار الشركة
        try:
            logo_path = 'attached_assets/ChatGPT Image Jun 8, 2025, 05_34_10 PM_1749393284624.png'
            pdf.image(logo_path, x=15, y=8, w=25, h=25)
        except:
            pdf.set_fill_color(41, 128, 185)
            pdf.rect(15, 8, 25, 25, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 10)
            pdf.set_xy(20, 18)
            pdf.safe_cell(15, 6, 'NUZUM', 0, 0, 'C')
        
        # عنوان التقرير
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(50, 10)
        pdf.safe_cell(110, 6, 'WORKSHOP RECORDS REPORT', 0, 1, 'C')
        
        # معلومات المركبة
        pdf.set_font('Arial', '', 11)
        pdf.set_xy(50, 18)
        vehicle_info = f'Vehicle: {vehicle.plate_number} - {vehicle.make} {vehicle.model} ({vehicle.year})'
        pdf.safe_cell(110, 5, vehicle_info, 0, 1, 'C')
        
        pdf.set_xy(50, 24)
        color_info = f'Color: {vehicle.color} | Status: {vehicle.status.title()}'
        pdf.safe_cell(110, 5, color_info, 0, 1, 'C')
        
        # التاريخ
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(50, 30)
        date_str = datetime.now().strftime('%Y-%m-%d')
        pdf.safe_cell(110, 6, f'Report Date: {date_str}', 0, 1, 'C')
        
        # استعادة اللون الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # معلومات المركبة التفصيلية
        pdf.set_fill_color(236, 240, 241)
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, 'VEHICLE INFORMATION', 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 11)
        vehicle_details = [
            ('Plate Number', str(vehicle.plate_number)),
            ('Make & Model', f'{vehicle.make} {vehicle.model}'),
            ('Year', str(vehicle.year)),
            ('Color', str(vehicle.color)),
            ('Status', str(vehicle.status)),
        ]
        
        for i, (label, value) in enumerate(vehicle_details):
            if i % 2 == 0:
                pdf.set_fill_color(248, 249, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
                
            pdf.safe_cell(80, 8, label, 1, 0, 'L', True)
            pdf.safe_cell(110, 8, value, 1, 1, 'L', True)
        
        pdf.ln(10)
        
        # سجلات الورشة
        pdf.set_fill_color(231, 76, 60)  # أحمر
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, f'WORKSHOP RECORDS ({len(workshop_records)} Records)', 1, 1, 'C', True)
        
        if workshop_records:
            # رأس جدول السجلات
            pdf.set_fill_color(52, 152, 219)  # أزرق
            pdf.set_font('Arial', 'B', 9)
            headers = ['Entry Date', 'Exit Date', 'Reason', 'Status', 'Cost (SAR)', 'Workshop', 'Technician']
            col_widths = [25, 25, 30, 25, 20, 35, 30]
            
            for i, header in enumerate(headers):
                pdf.safe_cell(col_widths[i], 8, header, 1, 0, 'C', True)
            pdf.ln()
            
            # بيانات السجلات
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 8)
            
            total_cost = 0
            total_days = 0
            
            for i, record in enumerate(workshop_records):
                # تناوب الألوان
                if i % 2 == 0:
                    pdf.set_fill_color(248, 249, 250)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                # تحضير البيانات
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else 'N/A'
                exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else 'In Workshop'
                
                # ترجمة القيم
                reason_map = {'maintenance': 'Maintenance', 'breakdown': 'Breakdown', 'accident': 'Accident'}
                status_map = {'in_progress': 'In Progress', 'completed': 'Completed', 'pending_approval': 'Pending'}
                
                reason = reason_map.get(record.reason, str(record.reason)) if record.reason else 'N/A'
                status = status_map.get(record.repair_status, str(record.repair_status)) if record.repair_status else 'N/A'
                
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                
                # حساب الأيام
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                
                workshop_name = str(record.workshop_name) if record.workshop_name else 'N/A'
                technician = str(record.technician_name) if record.technician_name else 'N/A'
                
                # إضافة الصف
                row_data = [entry_date, exit_date, reason, status, f'{cost:,.0f}', workshop_name, technician]
                
                for j, data in enumerate(row_data):
                    pdf.safe_cell(col_widths[j], 6, data, 1, 0, 'C', True)
                pdf.ln()
            
            pdf.ln(5)
            
            # ملخص الإحصائيات
            pdf.set_fill_color(46, 204, 113)  # أخضر
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 12)
            pdf.safe_cell(0, 8, 'SUMMARY STATISTICS', 1, 1, 'C', True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            
            stats = [
                ('Total Records', str(len(workshop_records))),
                ('Total Cost', f'{total_cost:,.2f} SAR'),
                ('Total Days in Workshop', f'{total_days} days'),
                ('Average Cost per Record', f'{total_cost/len(workshop_records):,.2f} SAR' if len(workshop_records) > 0 else '0 SAR'),
                ('Average Days per Record', f'{total_days/len(workshop_records):.1f} days' if len(workshop_records) > 0 else '0 days')
            ]
            
            for i, (label, value) in enumerate(stats):
                if i % 2 == 0:
                    pdf.set_fill_color(230, 247, 255)
                else:
                    pdf.set_fill_color(255, 255, 255)
                    
                pdf.safe_cell(100, 8, label, 1, 0, 'L', True)
                pdf.safe_cell(90, 8, value, 1, 1, 'C', True)
        
        else:
            # لا توجد سجلات
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.safe_cell(0, 20, 'No workshop records found for this vehicle', 1, 1, 'C')
        
        # التذييل
        pdf.ln(15)
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(100, 100, 100)
        
        footer_text = f'Generated by NUZUM Vehicle Management System - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        pdf.safe_cell(0, 6, footer_text, 0, 1, 'C')
        
        # إرجاع PDF
        output = BytesIO()
        
        try:
            pdf_content = pdf.output(dest='S')
            
            if isinstance(pdf_content, str):
                output.write(pdf_content.encode('latin-1', errors='replace'))
            else:
                output.write(pdf_content)
                
        except Exception as e:
            print(f"خطأ في إنشاء PDF الورشة: {str(e)}")
            return create_emergency_workshop_pdf(vehicle, workshop_records)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ عام في PDF الورشة: {str(e)}")
        return create_emergency_workshop_pdf(vehicle, workshop_records)

def create_emergency_workshop_pdf(vehicle, workshop_records):
    """PDF طوارئ للورشة"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        pdf.cell(0, 10, 'NUZUM - WORKSHOP REPORT', 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Vehicle: {vehicle.plate_number} - {vehicle.make} {vehicle.model}', 0, 1)
        pdf.cell(0, 8, f'Records Count: {len(workshop_records)}', 0, 1)
        pdf.ln(5)
        
        if workshop_records:
            total_cost = sum(float(record.cost) if record.cost else 0 for record in workshop_records)
            pdf.cell(0, 8, f'Total Workshop Cost: {total_cost:,.2f} SAR', 0, 1)
        
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        if isinstance(pdf_content, str):
            output.write(pdf_content.encode('latin-1', errors='replace'))
        else:
            output.write(pdf_content)
            
        output.seek(0)
        return output.getvalue()
        
    except Exception:
        return b'WORKSHOP_PDF_FAILED'