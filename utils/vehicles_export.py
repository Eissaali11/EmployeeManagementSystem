"""
وحدة للتصدير والمشاركة في نظام إدارة المركبات
تتضمن وظائف لتصدير بيانات المركبات وسجلات الورشة إلى PDF وExcel
"""

import os
import io
import tempfile
from datetime import datetime
from flask import url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import pandas as pd
from fpdf import FPDF

# تعريف مسار المجلد الحالي
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

class ArabicPDF(FPDF):
    """فئة PDF معدلة لدعم اللغة العربية"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)
        # تسجيل الخطوط العربية
        font_path = os.path.join(PROJECT_DIR, 'static', 'fonts')
        
        # إضافة خط Tajawal (خط عصري للعناوين)
        self.add_font('Tajawal', '', os.path.join(font_path, 'Tajawal-Regular.ttf'), uni=True)
        self.add_font('Tajawal', 'B', os.path.join(font_path, 'Tajawal-Bold.ttf'), uni=True)
        
        # إضافة خط Amiri (خط تقليدي للنصوص)
        self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'), uni=True)
        self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'), uni=True)
    
    def arabic_text(self, txt):
        """إعادة تشكيل النص العربي وتحويله ليعرض بشكل صحيح"""
        if txt is None or txt == '':
            return ''
        
        # تخطي المعالجة لغير النصوص
        if not isinstance(txt, str):
            return str(txt)
        
        # تخطي معالجة الأرقام والتواريخ
        if txt.replace('.', '', 1).replace(',', '', 1).isdigit() or all(c.isdigit() or c in '/-:' for c in txt):
            return txt
        
        # إعادة تشكيل النص العربي وتحويله إلى النمط المناسب للعرض
        reshaped_text = arabic_reshaper.reshape(txt)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    
    def cell(self, w=0, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
        """تجاوز دالة الخلية لدعم النص العربي"""
        # نحول النص العربي ونستخدم الواجهة القديمة للمكتبة
        arabic_txt = self.arabic_text(txt)
        super().cell(w, h, arabic_txt, border, ln, align, fill, link)
    
    def multi_cell(self, w=0, h=0, txt='', border=0, align='', fill=False):
        """تجاوز دالة الخلايا المتعددة لدعم النص العربي"""
        # نحول النص العربي ونستخدم الواجهة القديمة للمكتبة
        arabic_txt = self.arabic_text(txt)
        super().multi_cell(w, h, arabic_txt, border, align, fill)

def export_vehicle_pdf(vehicle, workshop_records=None, rental_records=None):
    """
    تصدير بيانات السيارة إلى ملف PDF
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة (اختياري)
        rental_records: سجلات الإيجار (اختياري)
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    # إنشاء كائن PDF مع دعم اللغة العربية
    pdf = ArabicPDF(orientation='P', unit='mm', format='A4')
    pdf.set_title('تقرير بيانات السيارة')
    pdf.set_author('نُظم - نظام إدارة المركبات')
    
    # إضافة صفحة جديدة
    pdf.add_page()
    
    # إضافة الشعار في رأس الصفحة
    logo_path = os.path.join(PROJECT_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=10, w=30)
    
    # عنوان التقرير
    pdf.set_font('Tajawal', 'B', 18)
    pdf.set_y(20)
    pdf.cell(0, 10, f'تقرير بيانات السيارة: {vehicle.plate_number}', 0, 1, 'C')
    
    # معلومات السيارة الأساسية
    pdf.set_font('Tajawal', 'B', 14)
    pdf.cell(0, 10, 'معلومات السيارة الأساسية', 0, 1, 'R')
    pdf.ln(5)
    
    # جدول المعلومات الأساسية
    pdf.set_font('Amiri', '', 12)
    basic_data = [
        ['رقم اللوحة:', vehicle.plate_number],
        ['النوع:', f"{vehicle.make} {vehicle.model}"],
        ['سنة الصنع:', str(vehicle.year)],
        ['اللون:', vehicle.color],
        ['رقم الهيكل:', vehicle.vin or "غير متوفر"],
        ['القسم/المالك:', vehicle.department or "غير محدد"],
        ['الحالة:', {
            'available': 'متاحة',
            'rented': 'مؤجرة',
            'in_workshop': 'في الورشة',
            'in_project': 'في المشروع',
            'accident': 'حادث',
            'sold': 'مباعة'
        }.get(vehicle.status, vehicle.status)],
        ['تاريخ انتهاء التأمين:', vehicle.insurance_expiry.strftime("%Y-%m-%d") if vehicle.insurance_expiry else "غير محدد"],
        ['تاريخ انتهاء الفحص:', vehicle.inspection_expiry.strftime("%Y-%m-%d") if vehicle.inspection_expiry else "غير محدد"],
    ]
    
    for label, value in basic_data:
        pdf.set_font('Amiri', 'B', 12)
        pdf.cell(60, 8, label, 0, 0, 'R')
        pdf.set_font('Amiri', '', 12)
        pdf.cell(0, 8, value, 0, 1, 'R')
    
    pdf.ln(10)
    
    # سجلات الورشة إذا كانت متوفرة
    if workshop_records and len(workshop_records) > 0:
        pdf.set_font('Tajawal', 'B', 14)
        pdf.cell(0, 10, 'سجلات الورشة', 0, 1, 'R')
        pdf.ln(5)
        
        # عنوان جدول سجلات الورشة
        pdf.set_font('Amiri', 'B', 12)
        headers = ['سبب الدخول', 'تاريخ الدخول', 'تاريخ الخروج', 'حالة الإصلاح', 'التكلفة (ريال)', 'اسم الورشة']
        col_widths = [40, 30, 30, 30, 25, 35]
        
        # طباعة العناوين
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
        pdf.ln()
        
        # طباعة البيانات
        pdf.set_font('Amiri', '', 10)
        for record in workshop_records:
            reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
            status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
            
            # التحقق من طول النص وتقسيمه إذا كان طويلاً
            reason = reason_map.get(record.reason, record.reason)
            if len(reason) > 20:
                reason = reason[:17] + '...'
            
            workshop_name = record.workshop_name or "غير محدد"
            if len(workshop_name) > 20:
                workshop_name = workshop_name[:17] + '...'
            
            pdf.cell(col_widths[0], 8, reason, 1, 0, 'R')
            pdf.cell(col_widths[1], 8, record.entry_date.strftime("%Y-%m-%d"), 1, 0, 'C')
            pdf.cell(col_widths[2], 8, record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة", 1, 0, 'C')
            pdf.cell(col_widths[3], 8, status_map.get(record.repair_status, record.repair_status), 1, 0, 'C')
            pdf.cell(col_widths[4], 8, f"{record.cost:,.2f}", 1, 0, 'L')
            pdf.cell(col_widths[5], 8, workshop_name, 1, 1, 'R')
        
        pdf.ln(5)
        
        # إجمالي تكاليف الصيانة
        total_cost = sum(record.cost for record in workshop_records)
        pdf.set_font('Amiri', 'B', 12)
        pdf.cell(0, 8, f"إجمالي تكاليف الصيانة: {total_cost:,.2f} ريال", 0, 1, 'R')
        pdf.ln(10)
    
    # سجلات الإيجار إذا كانت متوفرة
    if rental_records and len(rental_records) > 0:
        pdf.set_font('Tajawal', 'B', 14)
        pdf.cell(0, 10, 'سجلات الإيجار', 0, 1, 'R')
        pdf.ln(5)
        
        # عنوان جدول سجلات الإيجار
        pdf.set_font('Amiri', 'B', 12)
        headers = ['المستأجر', 'تاريخ البداية', 'تاريخ النهاية', 'التكلفة (ريال)', 'الحالة']
        col_widths = [60, 35, 35, 35, 25]
        
        # طباعة العناوين
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
        pdf.ln()
        
        # طباعة البيانات
        pdf.set_font('Amiri', '', 10)
        for record in rental_records:
            renter_name = record.renter_name
            if len(renter_name) > 25:
                renter_name = renter_name[:22] + '...'
            
            pdf.cell(col_widths[0], 8, renter_name, 1, 0, 'R')
            pdf.cell(col_widths[1], 8, record.start_date.strftime("%Y-%m-%d"), 1, 0, 'C')
            pdf.cell(col_widths[2], 8, record.end_date.strftime("%Y-%m-%d") if record.end_date else "مستمر", 1, 0, 'C')
            pdf.cell(col_widths[3], 8, f"{record.cost:,.2f}", 1, 0, 'L')
            pdf.cell(col_widths[4], 8, "نشط" if record.is_active else "منتهي", 1, 1, 'C')
    
    # حفظ الملف في الذاكرة
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


def export_workshop_records_pdf(vehicle, workshop_records):
    """
    تصدير سجلات الورشة لسيارة معينة إلى ملف PDF
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    register_fonts()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # إنشاء نمط للنص العربي
    styles.add(ParagraphStyle(name='Arabic', fontName='Amiri', fontSize=12, alignment=1))
    styles.add(ParagraphStyle(name='ArabicTitle', fontName='Amiri-Bold', fontSize=16, alignment=1))
    styles.add(ParagraphStyle(name='ArabicHeading', fontName='Amiri-Bold', fontSize=14, alignment=1))
    
    # تحضير المحتوى
    content = []
    
    # إضافة شعار الشركة إذا كان متوفراً
    logo_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"), 'img/logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=120, height=60)
        content.append(img)
        content.append(Spacer(1, 10))
    
    # عنوان التقرير
    title = Paragraph(arabic_text(f"تقرير سجلات الورشة للسيارة: {vehicle.plate_number}"), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 10))
    
    # معلومات السيارة الأساسية
    vehicle_info = Paragraph(
        arabic_text(f"السيارة: {vehicle.make} {vehicle.model} {vehicle.year} - {vehicle.color}"),
        styles['Arabic']
    )
    content.append(vehicle_info)
    content.append(Spacer(1, 20))
    
    # سجلات الورشة
    content.append(Paragraph(arabic_text("سجلات الورشة"), styles['ArabicHeading']))
    content.append(Spacer(1, 10))
    
    if workshop_records and len(workshop_records) > 0:
        # تحضير بيانات سجلات الورشة
        workshop_data = [
            [
                arabic_text("سبب الدخول"),
                arabic_text("تاريخ الدخول"),
                arabic_text("تاريخ الخروج"),
                arabic_text("حالة الإصلاح"),
                arabic_text("التكلفة (ريال)"),
                arabic_text("اسم الورشة"),
                arabic_text("الفني المسؤول")
            ]
        ]
        
        for record in workshop_records:
            reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
            status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
            
            workshop_data.append([
                arabic_text(reason_map.get(record.reason, record.reason)),
                arabic_text(record.entry_date.strftime("%Y-%m-%d")),
                arabic_text(record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة"),
                arabic_text(status_map.get(record.repair_status, record.repair_status)),
                arabic_text(f"{record.cost:,.2f}"),
                arabic_text(record.workshop_name or "غير محدد"),
                arabic_text(record.technician_name or "غير محدد")
            ])
        
        t = Table(workshop_data, colWidths=[doc.width/7] * 7)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),  # محاذاة أرقام التكلفة إلى اليسار
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        content.append(t)
        content.append(Spacer(1, 10))
        
        # إجمالي تكاليف الصيانة
        total_cost = sum(record.cost for record in workshop_records)
        cost_text = Paragraph(arabic_text(f"إجمالي تكاليف الصيانة: {total_cost:,.2f} ريال"), styles['Arabic'])
        content.append(cost_text)
        
        # إجمالي عدد أيام الورشة
        days_in_workshop = sum(
            (record.exit_date - record.entry_date).days + 1 if record.exit_date else 
            (datetime.now().date() - record.entry_date).days + 1
            for record in workshop_records
        )
        days_text = Paragraph(arabic_text(f"إجمالي عدد أيام الورشة: {days_in_workshop} يوم"), styles['Arabic'])
        content.append(days_text)
    else:
        content.append(Paragraph(arabic_text("لا توجد سجلات ورشة لهذه السيارة"), styles['Arabic']))
    
    content.append(Spacer(1, 20))
    
    # بيانات التوقيع والطباعة
    footer_text = Paragraph(
        arabic_text(f"تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة متكامل في {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        styles['Arabic']
    )
    content.append(footer_text)
    
    # بناء الوثيقة
    doc.build(content)
    buffer.seek(0)
    return buffer


def export_vehicle_excel(vehicle, workshop_records=None, rental_records=None):
    """
    تصدير بيانات السيارة إلى ملف Excel
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة (اختياري)
        rental_records: سجلات الإيجار (اختياري)
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف Excel
    """
    buffer = io.BytesIO()
    
    # إنشاء مصنف Excel مع عدة أوراق عمل
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # نمط العناوين
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'center',
            'align': 'center',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # نمط الخلايا
        cell_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        # ورقة المعلومات الأساسية
        basic_data = {
            'البيان': [
                'رقم اللوحة', 'النوع', 'سنة الصنع', 'اللون', 'رقم الهيكل',
                'القسم/المالك', 'الحالة', 'تاريخ انتهاء التأمين', 'تاريخ انتهاء الفحص'
            ],
            'القيمة': [
                vehicle.plate_number,
                f"{vehicle.make} {vehicle.model}",
                str(vehicle.year),
                vehicle.color,
                vehicle.vin or "غير متوفر",
                vehicle.department or "غير محدد",
                {
                    'available': 'متاحة',
                    'rented': 'مؤجرة',
                    'in_workshop': 'في الورشة',
                    'in_project': 'في المشروع',
                    'accident': 'حادث',
                    'sold': 'مباعة'
                }.get(vehicle.status, vehicle.status),
                vehicle.insurance_expiry.strftime("%Y-%m-%d") if vehicle.insurance_expiry else "غير محدد",
                vehicle.inspection_expiry.strftime("%Y-%m-%d") if vehicle.inspection_expiry else "غير محدد"
            ]
        }
        
        # إنشاء DataFrame وكتابته إلى ورقة العمل
        df_basic = pd.DataFrame(basic_data)
        df_basic.to_excel(writer, sheet_name='معلومات السيارة', index=False)
        
        # تعديل عرض الأعمدة
        worksheet = writer.sheets['معلومات السيارة']
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 30)
        
        # تنسيق الخلايا
        for col_num, col in enumerate(df_basic.columns):
            worksheet.write(0, col_num, col, header_format)
        
        for row_num in range(len(df_basic)):
            for col_num in range(len(df_basic.columns)):
                worksheet.write(row_num + 1, col_num, df_basic.iloc[row_num, col_num], cell_format)
        
        # إذا كانت سجلات الورشة متوفرة
        if workshop_records and len(workshop_records) > 0:
            # تحويل سجلات الورشة إلى DataFrame
            workshop_data = []
            
            for record in workshop_records:
                reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
                status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
                
                workshop_data.append({
                    'سبب الدخول': reason_map.get(record.reason, record.reason),
                    'تاريخ الدخول': record.entry_date.strftime("%Y-%m-%d"),
                    'تاريخ الخروج': record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة",
                    'حالة الإصلاح': status_map.get(record.repair_status, record.repair_status),
                    'التكلفة (ريال)': record.cost,
                    'اسم الورشة': record.workshop_name or "غير محدد",
                    'الفني المسؤول': record.technician_name or "غير محدد",
                    'الوصف': record.description or "",
                    'ملاحظات': record.notes or ""
                })
            
            df_workshop = pd.DataFrame(workshop_data)
            df_workshop.to_excel(writer, sheet_name='سجلات الورشة', index=False)
            
            # تعديل عرض الأعمدة
            worksheet = writer.sheets['سجلات الورشة']
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:G', 20)
            worksheet.set_column('H:I', 30)
            
            # تنسيق الخلايا
            for col_num, col in enumerate(df_workshop.columns):
                worksheet.write(0, col_num, col, header_format)
            
            for row_num in range(len(df_workshop)):
                for col_num in range(len(df_workshop.columns)):
                    worksheet.write(row_num + 1, col_num, df_workshop.iloc[row_num, col_num], cell_format)
            
            # إضافة صف إجمالي
            total_row = len(df_workshop) + 2
            worksheet.write(total_row, 0, 'الإجمالي', header_format)
            worksheet.write_formula(total_row, 4, f'=SUM(E2:E{len(df_workshop) + 1})', header_format)
            
            # دمج الخلايا للإجمالي
            worksheet.merge_range(total_row, 0, total_row, 3, 'الإجمالي', header_format)
        
        # إذا كانت سجلات الإيجار متوفرة
        if rental_records and len(rental_records) > 0:
            # تحويل سجلات الإيجار إلى DataFrame
            rental_data = []
            
            for record in rental_records:
                rental_data.append({
                    'المستأجر': record.renter_name,
                    'تاريخ البداية': record.start_date.strftime("%Y-%m-%d"),
                    'تاريخ النهاية': record.end_date.strftime("%Y-%m-%d") if record.end_date else "مستمر",
                    'التكلفة (ريال)': record.cost,
                    'الحالة': "نشط" if record.is_active else "منتهي",
                    'جهة الاتصال': record.contact_number or "",
                    'ملاحظات': record.notes or ""
                })
            
            df_rental = pd.DataFrame(rental_data)
            df_rental.to_excel(writer, sheet_name='سجلات الإيجار', index=False)
            
            # تعديل عرض الأعمدة
            worksheet = writer.sheets['سجلات الإيجار']
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 15)
            worksheet.set_column('G:G', 30)
            
            # تنسيق الخلايا
            for col_num, col in enumerate(df_rental.columns):
                worksheet.write(0, col_num, col, header_format)
            
            for row_num in range(len(df_rental)):
                for col_num in range(len(df_rental.columns)):
                    worksheet.write(row_num + 1, col_num, df_rental.iloc[row_num, col_num], cell_format)
    
    buffer.seek(0)
    return buffer


def export_workshop_records_excel(vehicle, workshop_records):
    """
    تصدير سجلات الورشة لسيارة معينة إلى ملف Excel
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف Excel
    """
    buffer = io.BytesIO()
    
    # إنشاء مصنف Excel
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # نمط العناوين
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'center',
            'align': 'center',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # نمط الخلايا
        cell_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        
        # معلومات السيارة
        vehicle_info = {
            'البيان': ['رقم اللوحة', 'النوع', 'سنة الصنع', 'اللون'],
            'القيمة': [
                vehicle.plate_number,
                f"{vehicle.make} {vehicle.model}",
                str(vehicle.year),
                vehicle.color
            ]
        }
        
        df_vehicle = pd.DataFrame(vehicle_info)
        df_vehicle.to_excel(writer, sheet_name='معلومات السيارة', index=False)
        
        # تعديل عرض الأعمدة
        worksheet = writer.sheets['معلومات السيارة']
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 25)
        
        # تنسيق الخلايا
        for col_num, col in enumerate(df_vehicle.columns):
            worksheet.write(0, col_num, col, header_format)
        
        for row_num in range(len(df_vehicle)):
            for col_num in range(len(df_vehicle.columns)):
                worksheet.write(row_num + 1, col_num, df_vehicle.iloc[row_num, col_num], cell_format)
        
        # سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            # تحويل سجلات الورشة إلى DataFrame
            workshop_data = []
            
            for record in workshop_records:
                reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
                status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
                
                workshop_data.append({
                    'سبب الدخول': reason_map.get(record.reason, record.reason),
                    'تاريخ الدخول': record.entry_date.strftime("%Y-%m-%d"),
                    'تاريخ الخروج': record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة",
                    'حالة الإصلاح': status_map.get(record.repair_status, record.repair_status),
                    'التكلفة (ريال)': record.cost,
                    'اسم الورشة': record.workshop_name or "غير محدد",
                    'الفني المسؤول': record.technician_name or "غير محدد",
                    'رابط التسليم': record.delivery_link or "",
                    'رابط الاستلام': record.reception_link or "",
                    'الوصف': record.description or "",
                    'ملاحظات': record.notes or ""
                })
            
            df_workshop = pd.DataFrame(workshop_data)
            df_workshop.to_excel(writer, sheet_name='سجلات الورشة', index=False)
            
            # تعديل عرض الأعمدة
            worksheet = writer.sheets['سجلات الورشة']
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:G', 20)
            worksheet.set_column('H:I', 25)
            worksheet.set_column('J:K', 30)
            
            # تنسيق الخلايا
            for col_num, col in enumerate(df_workshop.columns):
                worksheet.write(0, col_num, col, header_format)
            
            for row_num in range(len(df_workshop)):
                for col_num in range(len(df_workshop.columns)):
                    value = df_workshop.iloc[row_num, col_num]
                    # إذا كان الحقل يحتوي على رابط، نقوم بإضافة تنسيق الرابط
                    if col_num in [7, 8] and isinstance(value, str) and value.startswith('http'):
                        url_format = workbook.add_format({
                            'font_color': 'blue',
                            'underline': 1,
                            'align': 'right',
                            'valign': 'vcenter',
                            'border': 1
                        })
                        worksheet.write_url(row_num + 1, col_num, value, url_format, string='اضغط هنا للفتح')
                    else:
                        worksheet.write(row_num + 1, col_num, value, cell_format)
            
            # إضافة صف إجمالي
            total_row = len(df_workshop) + 2
            worksheet.write(total_row, 0, 'الإجمالي', header_format)
            worksheet.write_formula(total_row, 4, f'=SUM(E2:E{len(df_workshop) + 1})', header_format)
            
            # دمج الخلايا للإجمالي
            worksheet.merge_range(total_row, 0, total_row, 3, 'الإجمالي', header_format)
        else:
            # إنشاء ورقة فارغة إذا لم تكن هناك سجلات
            worksheet = workbook.add_worksheet('سجلات الورشة')
            worksheet.write(0, 0, "لا توجد سجلات ورشة لهذه السيارة", header_format)
    
    buffer.seek(0)
    return buffer