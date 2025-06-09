"""
مولد التقرير الشامل للموظف
يقوم بتجميع كل بيانات الموظف في تقرير واحد
"""

import os
from datetime import datetime
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import pandas as pd
from io import BytesIO
from models import Employee, Attendance, Salary, Vehicle, Department

# تحميل الخط العربي
FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts')

class EmployeeComprehensivePDF(FPDF):
    """فئة لإنشاء تقرير PDF شامل للموظف"""
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.add_font('Amiri', '', os.path.join(FONT_PATH, 'amiri-regular.ttf'), uni=True)
        self.add_font('Amiri', 'B', os.path.join(FONT_PATH, 'amiri-bold.ttf'), uni=True)
        
    def header(self):
        """ترويسة الصفحة - تظهر في كل صفحة"""
        # إضافة الشعار
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        
        # إضافة عنوان الصفحة
        self.set_font('Amiri', 'B', 16)
        self.cell(0, 10, self.arabic_text('التقرير الشامل للموظف'), 0, 1, 'C')
        
        # إضافة التاريخ الحالي
        self.set_font('Amiri', '', 10)
        self.cell(0, 10, self.arabic_text(f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d")}'), 0, 1, 'R')
        
        # خط تحت الترويسة
        self.line(10, 30, 200, 30)
        self.ln(15)
        
    def footer(self):
        """تذييل الصفحة - يظهر في كل صفحة"""
        self.set_y(-15)
        self.set_font('Amiri', '', 8)
        self.cell(0, 10, self.arabic_text('صفحة ') + str(self.page_no()) + '/{nb}', 0, 0, 'C')
        
    def arabic_text(self, text):
        """معالجة النص العربي للعرض الصحيح"""
        if not text:
            return ''
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    
    def add_section_title(self, title):
        """إضافة عنوان قسم"""
        self.set_fill_color(220, 220, 220)
        self.set_font('Amiri', 'B', 14)
        self.cell(0, 10, self.arabic_text(title), 1, 1, 'R', True)
        self.ln(5)
    
    def add_info_row(self, label, value):
        """إضافة صف معلومات"""
        self.set_font('Amiri', 'B', 12)
        self.cell(100, 8, self.arabic_text(str(value) if value else '-'), 1, 0, 'R')
        self.set_font('Amiri', '', 12)
        self.cell(90, 8, self.arabic_text(label), 1, 1, 'R', True)
    
    def add_table_header(self, headers, widths):
        """إضافة ترويسة جدول"""
        self.set_font('Amiri', 'B', 12)
        self.set_fill_color(200, 200, 200)
        
        for i, header in enumerate(headers):
            self.cell(widths[i], 10, self.arabic_text(header), 1, 0, 'C', True)
        self.ln()
    
    def add_table_row(self, data, widths, fill=False):
        """إضافة صف جدول"""
        self.set_font('Amiri', '', 10)
        self.set_fill_color(240, 240, 240)
        
        for i, value in enumerate(data):
            self.cell(widths[i], 8, self.arabic_text(str(value) if value is not None else '-'), 1, 0, 'C', fill)
        self.ln()


def generate_employee_comprehensive_pdf(employee_id):
    """
    إنشاء تقرير PDF شامل للموظف
    
    :param employee_id: معرف الموظف
    :return: مخرجات ملف PDF
    """
    # استعلام بيانات الموظف
    employee = Employee.query.get(employee_id)
    if not employee:
        return None
    
    # استعلام بيانات الحضور
    attendances = Attendance.query.filter_by(employee_id=employee_id).order_by(Attendance.date.desc()).all()
    
    # استعلام بيانات الرواتب
    salaries = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.year.desc(), Salary.month.desc()).all()
    
    # استعلام بيانات المركبات المرتبطة بالموظف
    vehicles = Vehicle.query.filter_by(driver_id=employee_id).all()
    
    # إنشاء ملف PDF
    pdf = EmployeeComprehensivePDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # معلومات الموظف الأساسية
    pdf.add_section_title('المعلومات الأساسية')
    
    pdf.add_info_row('اسم الموظف', employee.name)
    pdf.add_info_row('الرقم الوظيفي', employee.employee_id)
    pdf.add_info_row('رقم الهوية', employee.national_id)
    pdf.add_info_row('تاريخ الميلاد', employee.birthdate.strftime('%Y-%m-%d') if employee.birthdate else '-')
    pdf.add_info_row('الجنسية', employee.nationality)
    pdf.add_info_row('القسم', employee.department.name if employee.department else '-')
    pdf.add_info_row('المشروع', employee.project)
    pdf.add_info_row('المدينة', employee.city)
    pdf.add_info_row('البريد الإلكتروني', employee.email)
    pdf.add_info_row('رقم الجوال', employee.phone)
    
    # معلومات الوثائق
    pdf.ln(5)
    pdf.add_section_title('معلومات الوثائق')
    
    if employee.documents:
        # عرض الوثائق مع تواريخ الانتهاء
        for doc in employee.documents:
            doc_type_map = {
                'national_id': 'الهوية الوطنية',
                'passport': 'جواز السفر',
                'visa': 'التأشيرة',
                'health_certificate': 'الشهادة الصحية',
                'driving_license': 'رخصة القيادة',
                'contract': 'عقد العمل',
                'other': 'أخرى'
            }
            doc_type_name = doc_type_map.get(doc.document_type, doc.document_type)
            expiry_date = doc.expiry_date.strftime('%Y-%m-%d') if doc.expiry_date else '-'
            pdf.add_info_row(f'{doc_type_name} - تاريخ الانتهاء', expiry_date)
    else:
        pdf.set_font('Amiri', '', 12)
        pdf.cell(0, 10, pdf.arabic_text('لا توجد وثائق مسجلة'), 0, 1, 'C')
    
    # بيانات المركبات
    pdf.ln(5)
    pdf.add_section_title('المركبات المسجلة')
    
    if vehicles:
        headers = ['رقم اللوحة', 'الطراز', 'الموديل', 'اللون', 'سنة الصنع']
        widths = [40, 40, 40, 40, 30]
        pdf.add_table_header(headers, widths)
        
        for i, vehicle in enumerate(vehicles):
            row_data = [
                vehicle.plate_number,
                vehicle.make,
                vehicle.model,
                vehicle.color,
                vehicle.year
            ]
            pdf.add_table_row(row_data, widths, fill=(i % 2 == 0))
    else:
        pdf.set_font('Amiri', '', 12)
        pdf.cell(0, 10, pdf.arabic_text('لا توجد مركبات مسجلة للموظف'), 0, 1, 'C')
    
    # بيانات الحضور والغياب
    pdf.ln(5)
    pdf.add_section_title('سجل الحضور والغياب')
    
    if attendances:
        headers = ['التاريخ', 'الحالة', 'الملاحظات']
        widths = [60, 60, 70]
        pdf.add_table_header(headers, widths)
        
        # عرض آخر 15 سجل حضور
        attendance_limit = min(15, len(attendances))
        for i, attendance in enumerate(attendances[:attendance_limit]):
            status_map = {
                'present': 'حاضر',
                'absent': 'غائب',
                'leave': 'إجازة',
                'sick': 'مرضي'
            }
            status_text = status_map.get(attendance.status, attendance.status)
            
            row_data = [
                attendance.date.strftime('%Y-%m-%d'),
                status_text,
                attendance.notes or '-'
            ]
            pdf.add_table_row(row_data, widths, fill=(i % 2 == 0))
        
        # إضافة ملخص إحصائيات الحضور
        pdf.ln(5)
        present_count = sum(1 for a in attendances if a.status == 'present')
        absent_count = sum(1 for a in attendances if a.status == 'absent')
        leave_count = sum(1 for a in attendances if a.status == 'leave')
        sick_count = sum(1 for a in attendances if a.status == 'sick')
        
        pdf.set_font('Amiri', 'B', 12)
        pdf.cell(0, 10, pdf.arabic_text(f'ملخص الحضور: حاضر: {present_count}, غائب: {absent_count}, إجازة: {leave_count}, مرضي: {sick_count}'), 0, 1, 'R')
    else:
        pdf.set_font('Amiri', '', 12)
        pdf.cell(0, 10, pdf.arabic_text('لا توجد سجلات حضور مسجلة'), 0, 1, 'C')
    
    # بيانات الرواتب
    pdf.ln(5)
    pdf.add_section_title('سجل الرواتب')
    
    if salaries:
        headers = ['الشهر', 'السنة', 'الراتب الأساسي', 'البدلات', 'الخصومات', 'صافي الراتب']
        widths = [30, 30, 35, 35, 35, 35]
        pdf.add_table_header(headers, widths)
        
        # عرض آخر 10 رواتب
        salary_limit = min(10, len(salaries))
        for i, salary in enumerate(salaries[:salary_limit]):
            row_data = [
                salary.month,
                salary.year,
                salary.basic_salary,
                salary.allowances,
                salary.deductions,
                salary.net_salary
            ]
            pdf.add_table_row(row_data, widths, fill=(i % 2 == 0))
    else:
        pdf.set_font('Amiri', '', 12)
        pdf.cell(0, 10, pdf.arabic_text('لا توجد سجلات رواتب مسجلة'), 0, 1, 'C')
    
    # إنشاء مخرجات الملف
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    
    return output


def generate_employee_comprehensive_excel(employee_id):
    """
    إنشاء تقرير Excel شامل للموظف
    
    :param employee_id: معرف الموظف
    :return: مخرجات ملف Excel
    """
    # استعلام بيانات الموظف
    employee = Employee.query.get(employee_id)
    if not employee:
        return None
    
    # استعلام بيانات الحضور
    attendances = Attendance.query.filter_by(employee_id=employee_id).order_by(Attendance.date.desc()).all()
    
    # استعلام بيانات الرواتب
    salaries = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.year.desc(), Salary.month.desc()).all()
    
    # استعلام بيانات المركبات المرتبطة بالموظف
    vehicles = Vehicle.query.filter_by(driver_id=employee_id).all()
    
    # إنشاء ExcelWriter
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # إنشاء ورقة معلومات الموظف
    employee_data = {
        'المعلومة': [
            'اسم الموظف', 'الرقم الوظيفي', 'رقم الهوية', 'تاريخ الميلاد', 'الجنسية',
            'القسم', 'المشروع', 'المدينة', 'البريد الإلكتروني', 'رقم الجوال'
        ],
        'القيمة': [
            employee.name,
            employee.employee_id,
            employee.national_id,
            employee.birthdate.strftime('%Y-%m-%d') if employee.birthdate else '-',
            employee.nationality,
            employee.department.name if employee.department else '-',
            employee.project,
            employee.city,
            employee.email,
            employee.phone
        ]
    }
    
    df_employee = pd.DataFrame(employee_data)
    df_employee.to_excel(writer, sheet_name='معلومات الموظف', index=False)
    
    # تنسيق ورقة معلومات الموظف
    worksheet = writer.sheets['معلومات الموظف']
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 40)
    
    # إنشاء ورقة الوثائق
    if employee.documents:
        doc_data = {
            'نوع الوثيقة': [],
            'تاريخ الإصدار': [],
            'تاريخ الانتهاء': [],
            'رقم الوثيقة': [],
            'ملاحظات': []
        }
        
        doc_type_map = {
            'national_id': 'الهوية الوطنية',
            'passport': 'جواز السفر',
            'visa': 'التأشيرة',
            'health_certificate': 'الشهادة الصحية',
            'driving_license': 'رخصة القيادة',
            'contract': 'عقد العمل',
            'other': 'أخرى'
        }
        
        for doc in employee.documents:
            doc_data['نوع الوثيقة'].append(doc_type_map.get(doc.document_type, doc.document_type))
            doc_data['تاريخ الإصدار'].append(doc.issue_date.strftime('%Y-%m-%d') if doc.issue_date else '-')
            doc_data['تاريخ الانتهاء'].append(doc.expiry_date.strftime('%Y-%m-%d') if doc.expiry_date else '-')
            doc_data['رقم الوثيقة'].append(doc.document_number or '-')
            doc_data['ملاحظات'].append(doc.notes or '-')
        
        df_documents = pd.DataFrame(doc_data)
        df_documents.to_excel(writer, sheet_name='الوثائق', index=False)
        
        # تنسيق ورقة الوثائق
        worksheet = writer.sheets['الوثائق']
        worksheet.set_column('A:E', 20)
    
    # إنشاء ورقة المركبات
    if vehicles:
        vehicle_data = {
            'رقم اللوحة': [],
            'الطراز': [],
            'الموديل': [],
            'اللون': [],
            'سنة الصنع': [],
            'رقم الهيكل': [],
            'تاريخ انتهاء الفحص': []
        }
        
        for vehicle in vehicles:
            vehicle_data['رقم اللوحة'].append(vehicle.plate_number)
            vehicle_data['الطراز'].append(vehicle.make)
            vehicle_data['الموديل'].append(vehicle.model)
            vehicle_data['اللون'].append(vehicle.color)
            vehicle_data['سنة الصنع'].append(vehicle.year)
            vehicle_data['رقم الهيكل'].append(vehicle.vin or '-')
            vehicle_data['تاريخ انتهاء الفحص'].append(
                vehicle.inspection_expiry.strftime('%Y-%m-%d') if hasattr(vehicle, 'inspection_expiry') and vehicle.inspection_expiry else '-'
            )
        
        df_vehicles = pd.DataFrame(vehicle_data)
        df_vehicles.to_excel(writer, sheet_name='المركبات', index=False)
        
        # تنسيق ورقة المركبات
        worksheet = writer.sheets['المركبات']
        worksheet.set_column('A:G', 18)
    
    # إنشاء ورقة الحضور
    if attendances:
        status_map = {
            'present': 'حاضر',
            'absent': 'غائب',
            'leave': 'إجازة',
            'sick': 'مرضي'
        }
        
        attendance_data = {
            'التاريخ': [],
            'اليوم': [],
            'الحالة': [],
            'الملاحظات': []
        }
        
        for attendance in attendances:
            day_name_map = {
                0: 'الاثنين',
                1: 'الثلاثاء',
                2: 'الأربعاء',
                3: 'الخميس',
                4: 'الجمعة',
                5: 'السبت',
                6: 'الأحد'
            }
            
            day_name = day_name_map.get(attendance.date.weekday(), '-')
            
            attendance_data['التاريخ'].append(attendance.date.strftime('%Y-%m-%d'))
            attendance_data['اليوم'].append(day_name)
            attendance_data['الحالة'].append(status_map.get(attendance.status, attendance.status))
            attendance_data['الملاحظات'].append(attendance.notes or '-')
        
        df_attendance = pd.DataFrame(attendance_data)
        df_attendance.to_excel(writer, sheet_name='سجل الحضور', index=False)
        
        # تنسيق ورقة الحضور
        worksheet = writer.sheets['سجل الحضور']
        worksheet.set_column('A:D', 20)
        
        # إنشاء ورقة ملخص الحضور
        present_count = sum(1 for a in attendances if a.status == 'present')
        absent_count = sum(1 for a in attendances if a.status == 'absent')
        leave_count = sum(1 for a in attendances if a.status == 'leave')
        sick_count = sum(1 for a in attendances if a.status == 'sick')
        total_count = len(attendances)
        
        attendance_summary = {
            'الحالة': ['حاضر', 'غائب', 'إجازة', 'مرضي', 'الإجمالي'],
            'العدد': [present_count, absent_count, leave_count, sick_count, total_count],
            'النسبة': [
                f"{(present_count / total_count * 100):.2f}%" if total_count else "0%",
                f"{(absent_count / total_count * 100):.2f}%" if total_count else "0%",
                f"{(leave_count / total_count * 100):.2f}%" if total_count else "0%",
                f"{(sick_count / total_count * 100):.2f}%" if total_count else "0%",
                "100%"
            ]
        }
        
        df_summary = pd.DataFrame(attendance_summary)
        df_summary.to_excel(writer, sheet_name='ملخص الحضور', index=False)
        
        # تنسيق ورقة ملخص الحضور
        worksheet = writer.sheets['ملخص الحضور']
        worksheet.set_column('A:C', 15)
    
    # إنشاء ورقة الرواتب
    if salaries:
        salary_data = {
            'الشهر': [],
            'السنة': [],
            'الراتب الأساسي': [],
            'البدلات': [],
            'الخصومات': [],
            'صافي الراتب': []
        }
        
        for salary in salaries:
            salary_data['الشهر'].append(salary.month)
            salary_data['السنة'].append(salary.year)
            salary_data['الراتب الأساسي'].append(salary.basic_salary)
            salary_data['البدلات'].append(salary.allowances)
            salary_data['الخصومات'].append(salary.deductions)
            salary_data['صافي الراتب'].append(salary.net_salary)
        
        df_salary = pd.DataFrame(salary_data)
        df_salary.to_excel(writer, sheet_name='سجل الرواتب', index=False)
        
        # تنسيق ورقة الرواتب
        worksheet = writer.sheets['سجل الرواتب']
        worksheet.set_column('A:F', 15)
    
    # حفظ الملف
    writer.close()
    
    output.seek(0)
    return output