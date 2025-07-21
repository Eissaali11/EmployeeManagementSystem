from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from sqlalchemy import extract, func, or_
from forms.vehicle_forms import VehicleAccidentForm, VehicleDocumentsForm
import os
import uuid
import io
import urllib.parse
import pandas as pd
from fpdf import FPDF
import base64
import uuid

from app import db
from models import (
        Vehicle, VehicleRental, VehicleWorkshop, VehicleWorkshopImage, 
        VehicleProject, VehicleHandover, VehicleHandoverImage, SystemAudit,
        VehiclePeriodicInspection, VehicleSafetyCheck, VehicleAccident, Employee,
        Department, ExternalAuthorization, Module, Permission, UserRole
)
from utils.audit_logger import log_activity
from utils.audit_logger import log_audit
from utils.vehicles_export import export_vehicle_pdf, export_workshop_records_pdf, export_vehicle_excel, export_workshop_records_excel
from utils.simple_pdf_generator import create_vehicle_handover_pdf as generate_complete_vehicle_report
from utils.vehicle_excel_report import generate_complete_vehicle_excel_report
from utils.vehicle_excel_report import generate_complete_vehicle_excel_report
# from utils.workshop_report import generate_workshop_report_pdf
# from utils.html_to_pdf import generate_pdf_from_template
# from utils.fpdf_arabic_report import generate_workshop_report_pdf_fpdf
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import arabic_reshaper
from bidi.algorithm import get_display
# from utils.fpdf_handover_pdf import generate_handover_report_pdf

vehicles_bp = Blueprint('vehicles', __name__)
vehicles_bp = Blueprint('vehicles', __name__)

def update_vehicle_driver(vehicle_id):
        """تحديث اسم السائق في جدول السيارات بناءً على آخر سجل تسليم من نوع delivery"""
        try:
                # الحصول على جميع سجلات التسليم (delivery) للسيارة مرتبة حسب التاريخ
                delivery_records = VehicleHandover.query.filter_by(
                        vehicle_id=vehicle_id, 
                        handover_type='delivery'
                ).order_by(VehicleHandover.handover_date.desc()).all()

                if delivery_records:
                        # أخذ أحدث سجل تسليم (delivery)
                        latest_delivery = delivery_records[0]

                        # تحديد اسم السائق (إما من جدول الموظفين أو من اسم الشخص المدخل يدوياً)
                        driver_name = None
                        if latest_delivery.employee_id:
                                employee = Employee.query.get(latest_delivery.employee_id)
                                if employee:
                                        driver_name = employee.name

                        # إذا لم يكن هناك موظف معين، استخدم اسم الشخص المدخل يدوياً
                        if not driver_name and latest_delivery.person_name:
                                driver_name = latest_delivery.person_name

                        # تحديث اسم السائق في جدول السيارات
                        vehicle = Vehicle.query.get(vehicle_id)
                        if vehicle:
                                vehicle.driver_name = driver_name
                                db.session.commit()
                else:
                        # إذا لم يكن هناك سجلات تسليم، امسح اسم السائق
                        vehicle = Vehicle.query.get(vehicle_id)
                        if vehicle:
                                vehicle.driver_name = None
                                db.session.commit()

        except Exception as e:
                print(f"خطأ في تحديث اسم السائق: {e}")
                # لا نريد أن يؤثر هذا الخطأ على العملية الأساسية
                pass

def update_all_vehicle_drivers():
        """تحديث أسماء جميع السائقين في جدول السيارات"""
        vehicles = Vehicle.query.all()
        updated_count = 0

        for vehicle in vehicles:
                update_vehicle_driver(vehicle.id)
                updated_count += 1

        return updated_count

def get_vehicle_current_employee_id(vehicle_id):
        """الحصول على معرف الموظف الحالي للسيارة"""
        latest_delivery = VehicleHandover.query.filter_by(
                vehicle_id=vehicle_id
        ).filter(
                VehicleHandover.handover_type.in_(['delivery', 'تسليم', 'handover'])
        ).order_by(VehicleHandover.handover_date.desc()).first()

        if latest_delivery and latest_delivery.employee_id:
                return latest_delivery.employee_id
        return None

# قائمة بأهم حالات السيارة للاختيار منها في النماذج
VEHICLE_STATUS_CHOICES = [
        'available',  # متاحة
        'rented',  # مؤجرة
        'in_project',  # في المشروع
        'in_workshop',  # في الورشة
        'accident',  # حادث
        'out_of_service'  # خارج الخدمة
]

# قائمة بأسباب دخول الورشة
WORKSHOP_REASON_CHOICES = [
        'maintenance',  # صيانة دورية
        'breakdown',  # عطل
        'accident',  # حادث
]

# قائمة بحالات الإصلاح في الورشة
REPAIR_STATUS_CHOICES = [
        'in_progress',  # قيد التنفيذ
        'completed',  # تم الإصلاح
        'pending_approval'  # بانتظار الموافقة
]

# قائمة بأنواع عمليات التسليم والاستلام
HANDOVER_TYPE_CHOICES = [
        'delivery',  # تسليم
        'return',  # استلام
    'inspection',  # تفتيش
        'weekly_inspection',  # تفتيش اسبةعي
    'monthly_inspection'  # تفتيش شهري
]

# قائمة بأنواع الفحص الدوري
INSPECTION_TYPE_CHOICES = [
        'technical',  # فحص فني
        'periodic',   # فحص دوري
        'safety'      # فحص أمان
]

# قائمة بحالات الفحص الدوري
INSPECTION_STATUS_CHOICES = [
        'valid',          # ساري
        'expired',        # منتهي
        'expiring_soon'   # على وشك الانتهاء
]

# قائمة بأنواع فحص السلامة
SAFETY_CHECK_TYPE_CHOICES = [
        'daily',    # يومي
        'weekly',   # أسبوعي
        'monthly'   # شهري
]

# قائمة بحالات فحص السلامة
SAFETY_CHECK_STATUS_CHOICES = [
        'completed',      # مكتمل
        'in_progress',    # قيد التنفيذ
        'needs_review'    # بحاجة للمراجعة
]

# الوظائف المساعدة
def save_file(file, folder='vehicles'):
        """حفظ الملف (صورة أو PDF) في المجلد المحدد وإرجاع المسار ونوع الملف"""
        if not file:
                return None, None

        # إنشاء اسم فريد للملف
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # التأكد من وجود المجلد
        upload_folder = os.path.join(current_app.static_folder, 'uploads', folder)
        os.makedirs(upload_folder, exist_ok=True)

        # حفظ الملف
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # تحديد نوع الملف (صورة أو PDF)
        file_type = 'pdf' if filename.lower().endswith('.pdf') else 'image'

        # إرجاع المسار النسبي للملف ونوعه
        return f"uploads/{folder}/{unique_filename}", file_type

# للحفاظ على التوافق مع الكود القديم
def save_image(file, folder='vehicles'):
        """وظيفة محفوظة للتوافق مع الكود القديم"""
        file_path, _ = save_file(file, folder)
        return file_path

def format_date_arabic(date_obj):
        """تنسيق التاريخ باللغة العربية"""
        months = {
                1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 
                5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
                9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"

def log_audit(action, entity_type, entity_id, details=None):
        """تسجيل الإجراء في سجل النظام - تم الانتقال للنظام الجديد"""
        log_activity(action, entity_type, entity_id, details)

def calculate_rental_adjustment(vehicle_id, year, month):
        """حساب الخصم على إيجار السيارة بناءً على أيام وجودها في الورشة"""
        # الحصول على الإيجار النشط للسيارة
        rental = VehicleRental.query.filter_by(vehicle_id=vehicle_id, is_active=True).first()
        if not rental:
                return 0

        # الحصول على سجلات الورشة للسيارة في الشهر والسنة المحددين
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=vehicle_id).filter(
                extract('year', VehicleWorkshop.entry_date) == year,
                extract('month', VehicleWorkshop.entry_date) == month
        ).all()

        # حساب عدد الأيام التي قضتها السيارة في الورشة
        total_days_in_workshop = 0
        for record in workshop_records:
                if record.exit_date:
                        # إذا كان هناك تاريخ خروج، نحسب الفرق بين تاريخ الدخول والخروج
                        delta = (record.exit_date - record.entry_date).days
                        total_days_in_workshop += delta
                else:
                        # إذا لم يكن هناك تاريخ خروج، نحسب الفرق حتى نهاية الشهر
                        last_day_of_month = 30  # تقريبي، يمكن تحسينه
                        entry_day = record.entry_date.day
                        days_remaining = last_day_of_month - entry_day
                        total_days_in_workshop += days_remaining

        # حساب الخصم اليومي (الإيجار الشهري / 30)
        daily_rent = rental.monthly_cost / 30
        adjustment = daily_rent * total_days_in_workshop

        return adjustment

# المسارات الأساسية
@vehicles_bp.route('/expired-documents')
@login_required
def expired_documents():
        """عرض قائمة المستندات المنتهية للمركبات بشكل تفصيلي"""
        # التاريخ الحالي
        today = datetime.now().date()

        # السيارات ذات استمارة منتهية
        expired_registration = Vehicle.query.filter(
                Vehicle.registration_expiry_date.isnot(None),
                Vehicle.registration_expiry_date < today
        ).order_by(Vehicle.registration_expiry_date).all()

        # السيارات ذات فحص دوري منتهي
        expired_inspection = Vehicle.query.filter(
                Vehicle.inspection_expiry_date.isnot(None),
                Vehicle.inspection_expiry_date < today
        ).order_by(Vehicle.inspection_expiry_date).all()

        # السيارات ذات تفويض منتهي
        expired_authorization = Vehicle.query.filter(
                Vehicle.authorization_expiry_date.isnot(None),
                Vehicle.authorization_expiry_date < today
        ).order_by(Vehicle.authorization_expiry_date).all()

        # جميع السيارات التي تحتوي على وثيقة منتهية واحدة على الأقل
        expired_all = Vehicle.query.filter(
                or_(
                        Vehicle.registration_expiry_date.isnot(None) & (Vehicle.registration_expiry_date < today),
                        Vehicle.inspection_expiry_date.isnot(None) & (Vehicle.inspection_expiry_date < today),
                        Vehicle.authorization_expiry_date.isnot(None) & (Vehicle.authorization_expiry_date < today)
                )
        ).order_by(Vehicle.plate_number).all()

        return render_template(
                'vehicles/expired_documents.html',
                expired_registration=expired_registration,
                expired_inspection=expired_inspection,
                expired_authorization=expired_authorization,
                expired_all=expired_all,
                today=today
        )
@vehicles_bp.route('/expired-documents/export/excel')
@login_required
def export_expired_documents_excel():
        """تصدير بيانات الوثائق المنتهية للمركبات إلى ملف Excel منسق"""
        # التاريخ الحالي
        today = datetime.now().date()

        # السيارات ذات استمارة منتهية
        expired_registration = Vehicle.query.filter(
                Vehicle.registration_expiry_date.isnot(None),
                Vehicle.registration_expiry_date < today
        ).order_by(Vehicle.registration_expiry_date).all()

        # السيارات ذات فحص دوري منتهي
        expired_inspection = Vehicle.query.filter(
                Vehicle.inspection_expiry_date.isnot(None),
                Vehicle.inspection_expiry_date < today
        ).order_by(Vehicle.inspection_expiry_date).all()

        # السيارات ذات تفويض منتهي
        expired_authorization = Vehicle.query.filter(
                Vehicle.authorization_expiry_date.isnot(None),
                Vehicle.authorization_expiry_date < today
        ).order_by(Vehicle.authorization_expiry_date).all()

        # إنشاء قوائم البيانات
        registration_data = []
        for vehicle in expired_registration:
                days_expired = (today - vehicle.registration_expiry_date).days
                registration_data.append({
                        'رقم اللوحة': vehicle.plate_number,
                        'الشركة المصنعة': vehicle.make,
                        'الموديل': vehicle.model,
                        'السنة': vehicle.year,
                        'تاريخ انتهاء الاستمارة': vehicle.registration_expiry_date.strftime('%Y-%m-%d'),
                        'عدد أيام الانتهاء': days_expired,
                        'نوع الوثيقة': 'استمارة السيارة'
                })

        inspection_data = []
        for vehicle in expired_inspection:
                days_expired = (today - vehicle.inspection_expiry_date).days
                inspection_data.append({
                        'رقم اللوحة': vehicle.plate_number,
                        'الشركة المصنعة': vehicle.make,
                        'الموديل': vehicle.model,
                        'السنة': vehicle.year,
                        'تاريخ انتهاء الفحص': vehicle.inspection_expiry_date.strftime('%Y-%m-%d'),
                        'عدد أيام الانتهاء': days_expired,
                        'نوع الوثيقة': 'الفحص الدوري'
                })

        authorization_data = []
        for vehicle in expired_authorization:
                days_expired = (today - vehicle.authorization_expiry_date).days
                authorization_data.append({
                        'رقم اللوحة': vehicle.plate_number,
                        'الشركة المصنعة': vehicle.make,
                        'الموديل': vehicle.model,
                        'السنة': vehicle.year,
                        'تاريخ انتهاء التفويض': vehicle.authorization_expiry_date.strftime('%Y-%m-%d'),
                        'عدد أيام الانتهاء': days_expired,
                        'نوع الوثيقة': 'التفويض'
                })

        # إنشاء مخرج Excel في الذاكرة
        output = io.BytesIO()

        # استخدام ExcelWriter مع خيارات التنسيق
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # إنشاء أوراق العمل لكل نوع من الوثائق
                if registration_data:
                        reg_df = pd.DataFrame(registration_data)
                        reg_df.to_excel(writer, sheet_name='استمارات منتهية', index=False)

                        # تنسيق ورقة الاستمارات
                        workbook = writer.book
                        worksheet = writer.sheets['استمارات منتهية']

                        # تنسيق العناوين
                        header_format = workbook.add_format({
                                'bold': True,
                                'text_wrap': True,
                                'valign': 'top',
                                'fg_color': '#FFD7D7',  # خلفية حمراء فاتحة
                                'border': 1,
                                'align': 'center'
                        })

                        # تنسيق عناوين الأعمدة
                        for col_num, value in enumerate(reg_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                                # ضبط عرض العمود
                                worksheet.set_column(col_num, col_num, 18)

                        # تنسيق صفوف البيانات
                        data_format = workbook.add_format({
                                'border': 1,
                                'align': 'center'
                        })

                        # تطبيق التنسيق على كل الخلايا
                        for row in range(1, len(reg_df) + 1):
                                for col in range(len(reg_df.columns)):
                                        worksheet.write(row, col, reg_df.iloc[row-1, col], data_format)

                        # تنسيق عمود أيام الانتهاء
                        days_col = reg_df.columns.get_loc('عدد أيام الانتهاء')
                        days_format = workbook.add_format({
                                'border': 1,
                                'align': 'center',
                                'fg_color': '#FFCCCC'  # خلفية حمراء فاتحة للإبراز
                        })

                        for row in range(1, len(reg_df) + 1):
                                worksheet.write(row, days_col, reg_df.iloc[row-1, days_col], days_format)

                # تنسيق ورقة الفحص الدوري
                if inspection_data:
                        insp_df = pd.DataFrame(inspection_data)
                        insp_df.to_excel(writer, sheet_name='فحص دوري منتهي', index=False)

                        # تنسيق ورقة الفحص الدوري
                        workbook = writer.book
                        worksheet = writer.sheets['فحص دوري منتهي']

                        # تنسيق العناوين
                        header_format = workbook.add_format({
                                'bold': True,
                                'text_wrap': True,
                                'valign': 'top',
                                'fg_color': '#D7E4BC',  # خلفية خضراء فاتحة
                                'border': 1,
                                'align': 'center'
                        })

                        # تنسيق عناوين الأعمدة
                        for col_num, value in enumerate(insp_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                                # ضبط عرض العمود
                                worksheet.set_column(col_num, col_num, 18)

                        # تنسيق صفوف البيانات
                        data_format = workbook.add_format({
                                'border': 1,
                                'align': 'center'
                        })

                        # تطبيق التنسيق على كل الخلايا
                        for row in range(1, len(insp_df) + 1):
                                for col in range(len(insp_df.columns)):
                                        worksheet.write(row, col, insp_df.iloc[row-1, col], data_format)

                        # تنسيق عمود أيام الانتهاء
                        days_col = insp_df.columns.get_loc('عدد أيام الانتهاء')
                        days_format = workbook.add_format({
                                'border': 1,
                                'align': 'center',
                                'fg_color': '#E2EFDA'  # خلفية خضراء فاتحة للإبراز
                        })

                        for row in range(1, len(insp_df) + 1):
                                worksheet.write(row, days_col, insp_df.iloc[row-1, days_col], days_format)

                # تنسيق ورقة التفويض
                if authorization_data:
                        auth_df = pd.DataFrame(authorization_data)
                        auth_df.to_excel(writer, sheet_name='تفويض منتهي', index=False)

                        # تنسيق ورقة التفويض
                        workbook = writer.book
                        worksheet = writer.sheets['تفويض منتهي']

                        # تنسيق العناوين
                        header_format = workbook.add_format({
                                'bold': True,
                                'text_wrap': True,
                                'valign': 'top',
                                'fg_color': '#B4C6E7',  # خلفية زرقاء فاتحة
                                'border': 1,
                                'align': 'center'
                        })

                        # تنسيق عناوين الأعمدة
                        for col_num, value in enumerate(auth_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                                # ضبط عرض العمود
                                worksheet.set_column(col_num, col_num, 18)

                        # تنسيق صفوف البيانات
                        data_format = workbook.add_format({
                                'border': 1,
                                'align': 'center'
                        })

                        # تطبيق التنسيق على كل الخلايا
                        for row in range(1, len(auth_df) + 1):
                                for col in range(len(auth_df.columns)):
                                        worksheet.write(row, col, auth_df.iloc[row-1, col], data_format)

                        # تنسيق عمود أيام الانتهاء
                        days_col = auth_df.columns.get_loc('عدد أيام الانتهاء')
                        days_format = workbook.add_format({
                                'border': 1,
                                'align': 'center',
                                'fg_color': '#DDEBF7'  # خلفية زرقاء فاتحة للإبراز
                        })

                        for row in range(1, len(auth_df) + 1):
                                worksheet.write(row, days_col, auth_df.iloc[row-1, days_col], days_format)

                # إنشاء ورقة ملخص
                summary_data = {
                        'نوع الوثيقة': ['الاستمارة', 'الفحص الدوري', 'التفويض', 'الإجمالي'],
                        'عدد الوثائق المنتهية': [
                                len(expired_registration),
                                len(expired_inspection),
                                len(expired_authorization),
                                len(expired_registration) + len(expired_inspection) + len(expired_authorization)
                        ]
                }

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='ملخص', index=False)

                # تنسيق ورقة الملخص
                workbook = writer.book
                worksheet = writer.sheets['ملخص']

                # تنسيق العناوين
                header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#BDD7EE',  # خلفية زرقاء فاتحة
                        'border': 1,
                        'align': 'center',
                        'font_size': 12
                })

                # تنسيق عناوين الأعمدة
                for col_num, value in enumerate(summary_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        # ضبط عرض العمود
                        worksheet.set_column(col_num, col_num, 25)

                # تنسيقات مختلفة للأنواع المختلفة
                reg_format = workbook.add_format({
                        'border': 1, 'align': 'center', 'fg_color': '#FFD7D7'
                })

                insp_format = workbook.add_format({
                        'border': 1, 'align': 'center', 'fg_color': '#D7E4BC'
                })

                auth_format = workbook.add_format({
                        'border': 1, 'align': 'center', 'fg_color': '#B4C6E7'
                })

                total_format = workbook.add_format({
                        'border': 1, 'align': 'center', 'bold': True, 'fg_color': '#FFC000', 'font_size': 12
                })

                # تطبيق التنسيقات
                worksheet.write(1, 0, summary_df.iloc[0, 0], reg_format)
                worksheet.write(1, 1, summary_df.iloc[0, 1], reg_format)

                worksheet.write(2, 0, summary_df.iloc[1, 0], insp_format)
                worksheet.write(2, 1, summary_df.iloc[1, 1], insp_format)

                worksheet.write(3, 0, summary_df.iloc[2, 0], auth_format)
                worksheet.write(3, 1, summary_df.iloc[2, 1], auth_format)

                worksheet.write(4, 0, summary_df.iloc[3, 0], total_format)
                worksheet.write(4, 1, summary_df.iloc[3, 1], total_format)

                # إضافة مخطط دائري
                chart = workbook.add_chart({'type': 'pie'})
                chart.add_series({
                        'name': 'توزيع الوثائق المنتهية',
                        'categories': ['ملخص', 1, 0, 3, 0],
                        'values': ['ملخص', 1, 1, 3, 1],
                        'points': [
                                {'fill': {'color': '#FFD7D7'}},  # الاستمارة
                                {'fill': {'color': '#D7E4BC'}},  # الفحص الدوري
                                {'fill': {'color': '#B4C6E7'}}   # التفويض
                        ],
                        'data_labels': {'value': True, 'category': True, 'percentage': True}
                })

                chart.set_title({'name': 'توزيع الوثائق المنتهية'})
                chart.set_style(10)
                chart.set_size({'width': 500, 'height': 300})
                worksheet.insert_chart('D2', chart)

        # التحضير لإرسال الملف
        output.seek(0)

        # اسم الملف بالتاريخ الحالي
        today_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"الوثائق_المنتهية_{today_str}.xlsx"

        # تسجيل الإجراء
        log_audit('export', 'vehicle_documents', 0, f'تم تصدير تقرير الوثائق المنتهية للمركبات إلى Excel')

        return send_file(
                output,
                download_name=filename,
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

@vehicles_bp.route('/')
@login_required
def index():
        """عرض قائمة السيارات مع خيارات التصفية"""
        status_filter = request.args.get('status', '')
        make_filter = request.args.get('make', '')
        search_plate = request.args.get('search_plate', '')
        project_filter = request.args.get('project', '')

        # قاعدة الاستعلام الأساسية
        query = Vehicle.query

        
        # تطبيق فلترة وصول المستخدمين (المديرون يرون جميع المركبات)
        if current_user.role != UserRole.ADMIN:
            # المستخدمون العاديون يرون فقط المركبات المخصصة لهم
            from models import vehicle_user_access
            query = query.join(vehicle_user_access).filter(
                vehicle_user_access.c.user_id == current_user.id
            )
        

        # إضافة التصفية حسب الحالة إذا تم تحديدها
        if status_filter:
                query = query.filter(Vehicle.status == status_filter)

        # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
        if make_filter:
                query = query.filter(Vehicle.make == make_filter)

        # إضافة التصفية حسب المشروع إذا تم تحديده
        if project_filter:
                query = query.filter(Vehicle.project == project_filter)

        # إضافة البحث برقم السيارة إذا تم تحديده
        if search_plate:
                query = query.filter(Vehicle.plate_number.contains(search_plate))

        # الحصول على قائمة بالشركات المصنعة لقائمة التصفية
        makes = db.session.query(Vehicle.make).distinct().all()
        makes = [make[0] for make in makes]

        # الحصول على قائمة بالمشاريع لقائمة التصفية
        projects = db.session.query(Vehicle.project).filter(Vehicle.project.isnot(None)).distinct().all()
        projects = [project[0] for project in projects]

        # الحصول على قائمة السيارات
        vehicles = query.order_by(Vehicle.status, Vehicle.plate_number).all()

        # إضافة معرف الموظف الحالي لكل سيارة
        for vehicle in vehicles:
                try:
                        vehicle.current_employee_id = get_vehicle_current_employee_id(vehicle.id)
                except Exception as e:
                        vehicle.current_employee_id = None
                        print(f"خطأ في الحصول على معرف الموظف للمركبة {vehicle.id}: {e}")

        # تحقق من تواريخ انتهاء الوثائق والتنبيه بالقريبة للانتهاء
        expiring_documents = []
        today = datetime.now().date()
        thirty_days_later = today + timedelta(days=30)

        # احصائيات للوثائق المنتهية أو القريبة من الانتهاء
        for vehicle in vehicles:
                if vehicle.authorization_expiry_date and today <= vehicle.authorization_expiry_date <= thirty_days_later:
                        expiring_documents.append({
                                'vehicle_id': vehicle.id,
                                'plate_number': vehicle.plate_number,
                                'document_type': 'authorization',
                                'document_name': 'تفويض المركبة',
                                'expiry_date': vehicle.authorization_expiry_date,
                                'days_remaining': (vehicle.authorization_expiry_date - today).days
                        })

                if vehicle.registration_expiry_date and today <= vehicle.registration_expiry_date <= thirty_days_later:
                        expiring_documents.append({
                                'vehicle_id': vehicle.id,
                                'plate_number': vehicle.plate_number,
                                'document_type': 'registration',
                                'document_name': 'استمارة السيارة',
                                'expiry_date': vehicle.registration_expiry_date,
                                'days_remaining': (vehicle.registration_expiry_date - today).days
                        })

                if vehicle.inspection_expiry_date and today <= vehicle.inspection_expiry_date <= thirty_days_later:
                        expiring_documents.append({
                                'vehicle_id': vehicle.id,
                                'plate_number': vehicle.plate_number,
                                'document_type': 'inspection',
                                'document_name': 'الفحص الدوري',
                                'expiry_date': vehicle.inspection_expiry_date, 
                                'days_remaining': (vehicle.inspection_expiry_date - today).days
                        })

        # ترتيب الوثائق المنتهية حسب عدد الأيام المتبقية (الأقرب للانتهاء أولاً)
        expiring_documents.sort(key=lambda x: x['days_remaining'])

        # إحصائيات سريعة
        stats = {
                'total': Vehicle.query.count(),
                'available': Vehicle.query.filter_by(status='available').count(),
                'rented': Vehicle.query.filter_by(status='rented').count(),
                'in_project': Vehicle.query.filter_by(status='in_project').count(),
                'in_workshop': Vehicle.query.filter_by(status='in_workshop').count(),
                'accident': Vehicle.query.filter_by(status='accident').count()
        }

        return render_template(
                'vehicles/index.html',
                vehicles=vehicles,
                stats=stats,
                status_filter=status_filter,
                make_filter=make_filter,
                search_plate=search_plate,
                project_filter=project_filter,
                makes=makes,
                projects=projects,
                statuses=VEHICLE_STATUS_CHOICES,
                expiring_documents=expiring_documents
        )

@vehicles_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
        """إضافة سيارة جديدة"""
        if request.method == 'POST':
                # استخراج البيانات من النموذج
                plate_number = request.form.get('plate_number')
                make = request.form.get('make')
                model = request.form.get('model')
                year = request.form.get('year')
                color = request.form.get('color')
                status = request.form.get('status')
                notes = request.form.get('notes')
                type_of_car = request.form.get('type_of_car')
                
                # التحقق من عدم وجود سيارة بنفس رقم اللوحة
                if Vehicle.query.filter_by(plate_number=plate_number).first():
                        flash('يوجد سيارة مسجلة بنفس رقم اللوحة!', 'danger')
                        return redirect(url_for('vehicles.create'))

                # إنشاء سيارة جديدة
                driver_name = request.form.get('driver_name')
                vehicle = Vehicle(
                        plate_number=plate_number,
                        make=make,
                        model=model,
                        year=int(year),
                        color=color,
                        status=status,
                        driver_name=driver_name,
                        notes=notes,
                        type_of_car=type_of_car
                )

                db.session.add(vehicle)
                db.session.flush()  # للحصول على ID المركبة قبل الالتزام النهائي
                
                # معالجة المستخدمين المخولين
                authorized_user_ids = request.form.getlist('authorized_users')
                if authorized_user_ids:
                    from models import User
                    authorized_users = User.query.filter(User.id.in_(authorized_user_ids)).all()
                    for user in authorized_users:
                        vehicle.authorized_users.append(user)
                
                db.session.commit()

                # تسجيل الإجراء


                user_names = [user.name or user.username or user.email for user in vehicle.authorized_users]
                log_audit('create', 'vehicle', vehicle.id, 
                         f'تمت إضافة سيارة جديدة: {vehicle.plate_number}. المستخدمون المخولون: {", ".join(user_names) if user_names else "لا يوجد"}')
                
                flash(f'تمت إضافة السيارة بنجاح! المستخدمون المخولون: {len(vehicle.authorized_users)}', 'success')
                return redirect(url_for('vehicles.index'))
        
        # جلب جميع المستخدمين لإدارة الوصول
        from models import User
        all_users = User.query.filter_by(is_active=True).all()
        
        return render_template('vehicles/create.html', 
                             statuses=VEHICLE_STATUS_CHOICES,
                             all_users=all_users)


@vehicles_bp.route('/<int:id>')
@login_required
def view(id):
        """عرض تفاصيل سيارة معينة"""
        vehicle = Vehicle.query.get_or_404(id)

        
        # التحقق من صلاحية الوصول للمركبة
        if current_user.role != UserRole.ADMIN:
            # التحقق من أن المستخدم مخول للوصول لهذه المركبة
            if current_user not in vehicle.authorized_users:
                flash('ليس لديك صلاحية للوصول لهذه المركبة', 'danger')
                return redirect(url_for('vehicles.index'))
        

        # الحصول على سجلات مختلفة للسيارة
        rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
        project_assignments = VehicleProject.query.filter_by(vehicle_id=id).order_by(VehicleProject.start_date.desc()).all()
        handover_records = VehicleHandover.query.filter_by(vehicle_id=id).order_by(VehicleHandover.handover_date.desc()).all()

        # الحصول على سجلات الفحص الدوري وفحص السلامة والحوادث
        periodic_inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=id).order_by(VehiclePeriodicInspection.inspection_date.desc()).all()
        safety_checks = VehicleSafetyCheck.query.filter_by(vehicle_id=id).order_by(VehicleSafetyCheck.check_date.desc()).all()
        accidents = VehicleAccident.query.filter_by(vehicle_id=id).order_by(VehicleAccident.accident_date.desc()).all()

        # الحصول على التفويضات الخارجية
        external_authorizations = ExternalAuthorization.query.filter_by(vehicle_id=id).order_by(ExternalAuthorization.created_at.desc()).all()

        # الحصول على الأقسام والموظفين والمشاريع للنموذج
        departments = Department.query.all()
        employees = Employee.query.all()

        # حساب إجمالي تكلفة الصيانة وأيام الورشة
        total_maintenance_cost = sum(record.cost for record in workshop_records if record.cost)
        days_in_workshop = sum(
                (record.exit_date - record.entry_date).days if record.exit_date else 0
                for record in workshop_records
        )

        # تاريخ اليوم للاستخدام في حسابات الفرق بين التواريخ
        today = datetime.now().date()

        # استخراج معلومات السائق الحالي والسائقين السابقين
        current_driver = None
        previous_drivers = []

        # البحث عن آخر سجل تسليم (من حيث التاريخ) للعثور على السائق الحالي
        delivery_records = [rec for rec in handover_records if rec.handover_type in ['delivery', 'تسليم', 'handover']]
        delivery_records.sort(key=lambda x: x.handover_date, reverse=True)  # ترتيب حسب التاريخ (الأحدث أولاً)

        # تعيين أحدث سجل تسليم كسائق حالي والباقي كسائقين سابقين
        for i, record in enumerate(delivery_records):
                # الحصول على رقم هاتف الموظف إذا كان متوفراً
                phone_number = None
                if record.driver_employee and record.driver_employee.mobile:
                        phone_number = record.driver_employee.mobile

                if i == 0:  # أول سجل بعد الترتيب (الأحدث)
                        current_driver = {
                                'name': record.person_name,
                                'date': record.handover_date,
                                'formatted_date': format_date_arabic(record.handover_date),
                                'handover_id': record.id,
                                'mobile': phone_number,
                                'employee_id': record.employee_id,
                                'handover_type': record.handover_type,
                                'handover_type_ar': 'تسليم' if record.handover_type in ['delivery', 'تسليم', 'handover'] else 'استلام'
                        }
                else:
                        previous_drivers.append({
                                'name': record.person_name,
                                'date': record.handover_date,
                                'formatted_date': format_date_arabic(record.handover_date),
                                'handover_id': record.id,
                                'mobile': phone_number,
                                'employee_id': record.employee_id,
                                'handover_type': record.handover_type,
                                'handover_type_ar': 'تسليم' if record.handover_type in ['delivery', 'تسليم', 'handover'] else 'استلام'
                        })

        # تنسيق التواريخ
        for record in workshop_records:
                record.formatted_entry_date = format_date_arabic(record.entry_date)
                if record.exit_date:
                        record.formatted_exit_date = format_date_arabic(record.exit_date)

        for record in project_assignments:
                record.formatted_start_date = format_date_arabic(record.start_date)
                if record.end_date:
                        record.formatted_end_date = format_date_arabic(record.end_date)

        for record in handover_records:
                record.formatted_handover_date = format_date_arabic(record.handover_date)
                # إضافة معلومات رقم الهاتف للسجل
                record.mobile = None
                # تحديد نوع التسليم بالعربية
                if record.handover_type in ['delivery', 'تسليم', 'handover']:
                    record.handover_type_ar = 'تسليم'
                elif record.handover_type in ['return', 'استلام']:
                    record.handover_type_ar = 'استلام'
                else:
                    record.handover_type_ar = record.handover_type
                if record.driver_employee and record.driver_employee.mobile:
                        record.mobile = record.driver_employee.mobile

        for record in periodic_inspections:
                record.formatted_inspection_date = format_date_arabic(record.inspection_date)
                record.formatted_expiry_date = format_date_arabic(record.expiry_date)

        for record in safety_checks:
                record.formatted_check_date = format_date_arabic(record.check_date)

        if rental:
                rental.formatted_start_date = format_date_arabic(rental.start_date)
                if rental.end_date:
                        rental.formatted_end_date = format_date_arabic(rental.end_date)

        # ملاحظات تنبيهية عن انتهاء الفحص الدوري
        inspection_warnings = []
        for inspection in periodic_inspections:
                if inspection.is_expired:
                        inspection_warnings.append(f"الفحص الدوري منتهي الصلاحية منذ {(datetime.now().date() - inspection.expiry_date).days} يومًا")
                        break
                elif inspection.is_expiring_soon:
                        days_remaining = (inspection.expiry_date - datetime.now().date()).days
                        inspection_warnings.append(f"الفحص الدوري سينتهي خلال {days_remaining} يومًا")
                        break

        # الحصول على المرفقات (صور الورشة للسيارة)
        attachments = []
        for workshop_record in workshop_records:
            workshop_images = VehicleWorkshopImage.query.filter_by(workshop_record_id=workshop_record.id).all()
            attachments.extend(workshop_images)

        # إضافة سجلات التسليم/الاستلام للقائمة الجانبية
        handovers = handover_records

        return render_template(
                'vehicles/view.html',
                vehicle=vehicle,
                rental=rental,
                workshop_records=workshop_records,
                project_assignments=project_assignments,
                handover_records=handover_records,
                handovers=handovers,
                periodic_inspections=periodic_inspections,
                safety_checks=safety_checks,
                accidents=accidents,
                external_authorizations=external_authorizations,
                departments=departments,
                employees=employees,
                attachments=attachments,
                total_maintenance_cost=total_maintenance_cost,
                days_in_workshop=days_in_workshop,
                inspection_warnings=inspection_warnings,
                current_driver=current_driver,
                previous_drivers=previous_drivers,
                today=today
        )

@vehicles_bp.route('/documents/view/<int:id>', methods=['GET'])
@login_required
def view_documents(id):
        """عرض تفاصيل وثائق المركبة"""
        vehicle = Vehicle.query.get_or_404(id)

        # حساب الأيام المتبقية للوثائق
        today = datetime.now().date()
        documents_info = []

        if vehicle.authorization_expiry_date:
                days_remaining = (vehicle.authorization_expiry_date - today).days
                status = 'صالح'
                status_class = 'success'

                if days_remaining < 0:
                        status = 'منتهي'
                        status_class = 'danger'
                elif days_remaining <= 30:
                        status = 'على وشك الانتهاء'
                        status_class = 'warning'

                documents_info.append({
                        'name': 'تفويض المركبة',
                        'expiry_date': vehicle.authorization_expiry_date,
                        'formatted_date': format_date_arabic(vehicle.authorization_expiry_date),
                        'days_remaining': days_remaining,
                        'status': status,
                        'status_class': status_class
                })

        if vehicle.registration_expiry_date:
                days_remaining = (vehicle.registration_expiry_date - today).days
                status = 'صالح'
                status_class = 'success'

                if days_remaining < 0:
                        status = 'منتهي'
                        status_class = 'danger'
                elif days_remaining <= 30:
                        status = 'على وشك الانتهاء'
                        status_class = 'warning'

                documents_info.append({
                        'name': 'استمارة السيارة',
                        'expiry_date': vehicle.registration_expiry_date,
                        'formatted_date': format_date_arabic(vehicle.registration_expiry_date),
                        'days_remaining': days_remaining,
                        'status': status,
                        'status_class': status_class
                })

        if vehicle.inspection_expiry_date:
                days_remaining = (vehicle.inspection_expiry_date - today).days
                status = 'صالح'
                status_class = 'success'

                if days_remaining < 0:
                        status = 'منتهي'
                        status_class = 'danger'
                elif days_remaining <= 30:
                        status = 'على وشك الانتهاء'
                        status_class = 'warning'

                documents_info.append({
                        'name': 'الفحص الدوري',
                        'expiry_date': vehicle.inspection_expiry_date,
                        'formatted_date': format_date_arabic(vehicle.inspection_expiry_date),
                        'days_remaining': days_remaining,
                        'status': status,
                        'status_class': status_class
                })

        return render_template('vehicles/view_documents.html', vehicle=vehicle, documents_info=documents_info)

@vehicles_bp.route('/documents/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_documents(id):
        """تعديل تواريخ وثائق المركبة (التفويض، الاستمارة، الفحص الدوري)"""
        vehicle = Vehicle.query.get_or_404(id)
        form = VehicleDocumentsForm()

        
        # التحقق من القدوم من صفحة العمليات
        from_operations = request.args.get('from_operations')
        operation_id = from_operations if from_operations else None
        

        if request.method == 'GET':
                # ملء النموذج بالبيانات الحالية
                form.authorization_expiry_date.data = vehicle.authorization_expiry_date
                form.registration_expiry_date.data = vehicle.registration_expiry_date
                form.inspection_expiry_date.data = vehicle.inspection_expiry_date

        if form.validate_on_submit():
                # تحديث البيانات
                vehicle.authorization_expiry_date = form.authorization_expiry_date.data
                
                # إذا لم يكن قادماً من العمليات، حفظ جميع الحقول
                if not from_operations:
                    vehicle.registration_expiry_date = form.registration_expiry_date.data
                    vehicle.inspection_expiry_date = form.inspection_expiry_date.data
                
                vehicle.updated_at = datetime.utcnow()



                
                # إذا كان قادماً من العمليات، إنشاء سجل تسليم/استلام جديد
                if from_operations and operation_id:
                    try:
                        # البحث عن العملية
                        from models import Operation
                        operation = Operation.query.get(int(operation_id))
                        
                        if operation:
                            # إنشاء سجل تسليم/استلام جديد
                            handover = VehicleHandover(
                                vehicle_id=vehicle.id,
                                handover_type='delivery',  # تسليم
                                handover_date=datetime.utcnow(),
                                person_name=operation.employee.name if operation.employee else 'غير محدد',
                                notes=f'تفويض من العملية #{operation_id} - صالح حتى {form.authorization_expiry_date.data}',
                                created_by=current_user.id,
                                updated_at=datetime.utcnow()
                            )
                            
                            # إضافة معلومات إضافية إذا توفرت
                            if operation.employee:
                                handover.employee_id = operation.employee.id
                                if hasattr(operation.employee, 'mobile'):
                                    handover.driver_phone_number = operation.employee.mobile
                                if hasattr(operation.employee, 'national_id'):
                                    handover.driver_residency_number = operation.employee.national_id
                            
                            db.session.add(handover)
                            
                            # تحديث حالة العملية إلى مكتملة
                            operation.status = 'completed'
                            operation.completed_at = datetime.utcnow()
                            operation.reviewer_id = current_user.id
                            operation.review_notes = f'تم تحديد فترة التفويض وإنشاء سجل التسليم'
                            
                            # حفظ التغييرات أولاً
                            db.session.commit()
                            
                            # تحديث اسم السائق في معلومات السيارة الأساسية
                            update_vehicle_driver(vehicle.id)
                            
                            # تسجيل في العمليات
                            log_audit('create', 'vehicle_handover', handover.id, 
                                     f'تم إنشاء سجل تسليم من العملية #{operation_id}')
                            log_audit('update', 'operation', operation.id, 
                                     f'تم إكمال العملية وإنشاء سجل التسليم')
                            log_audit('update', 'vehicle', vehicle.id, 
                                     f'تم تحديث اسم السائق تلقائياً بعد إنشاء سجل التسليم')
                    
                    except Exception as e:
                        current_app.logger.error(f'خطأ في إنشاء سجل التسليم: {str(e)}')
                        flash('تم تحديث التفويض ولكن حدث خطأ في إنشاء سجل التسليم', 'warning')
                

                # حفظ التغييرات للوثائق إذا لم تكن محفوظة مسبقاً
                if not from_operations or not operation_id:
                    db.session.commit()
                

                # تسجيل الإجراء

                log_audit('update', 'vehicle_documents', vehicle.id, 
                        f'تم تحديث تواريخ وثائق المركبة: {vehicle.plate_number}')
                
                if from_operations:
                    flash('تم تحديد فترة التفويض وإنشاء سجل التسليم بنجاح!', 'success')
                    return redirect('/operations')
                else:
                    flash('تم تحديث تواريخ الوثائق بنجاح!', 'success')
                    return redirect(url_for('vehicles.view', id=id))
        
        return render_template('vehicles/edit_documents.html', 
                             form=form, vehicle=vehicle, 
                             from_operations=bool(from_operations), 
                             operation_id=operation_id)


@vehicles_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
        """تعديل بيانات سيارة"""
        vehicle = Vehicle.query.get_or_404(id)

        
        # التحقق من صلاحية الوصول للمركبة  
        if current_user.role != UserRole.ADMIN:
            # التحقق من أن المستخدم مخول للوصول لهذه المركبة
            if current_user not in vehicle.authorized_users:
                flash('ليس لديك صلاحية لتعديل هذه المركبة', 'danger')
                return redirect(url_for('vehicles.index'))
        

        if request.method == 'POST':
                # استخراج البيانات من النموذج
                plate_number = request.form.get('plate_number')
                make = request.form.get('make')
                model = request.form.get('model')
                year = request.form.get('year')
                color = request.form.get('color')
                status = request.form.get('status')
                notes = request.form.get('notes')

                # التحقق من عدم وجود سيارة أخرى بنفس رقم اللوحة
                existing = Vehicle.query.filter_by(plate_number=plate_number).first()
                if existing and existing.id != id:
                        flash('يوجد سيارة أخرى مسجلة بنفس رقم اللوحة!', 'danger')
                        return redirect(url_for('vehicles.edit', id=id))

                # تحديث بيانات السيارة
                driver_name = request.form.get('driver_name')
                project = request.form.get('project')
                vehicle.plate_number = plate_number
                vehicle.make = make
                vehicle.model = model
                vehicle.year = int(year)
                vehicle.color = color
                vehicle.status = status
                vehicle.driver_name = driver_name
                vehicle.project = project
                vehicle.notes = notes
                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('update', 'vehicle', vehicle.id, f'تم تعديل بيانات السيارة: {vehicle.plate_number}')

                flash('تم تعديل بيانات السيارة بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=id))

        # جلب الأقسام لقائمة المشاريع
        departments = Department.query.all()
        
        # جلب جميع المستخدمين لإدارة الوصول
        from models import User
        all_users = User.query.filter_by(is_active=True).all()
        
        return render_template('vehicles/edit.html', 
                             vehicle=vehicle, 
                             statuses=VEHICLE_STATUS_CHOICES, 
                             departments=departments,
                             all_users=all_users)

@vehicles_bp.route('/<int:id>/manage-user-access', methods=['POST'])
@login_required
def manage_user_access(id):
    """إدارة وصول المستخدمين للمركبة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # التحقق من صلاحيات الإدارة
    if current_user.role != UserRole.ADMIN:
        flash('ليس لديك صلاحية لإدارة وصول المستخدمين', 'danger')
        return redirect(url_for('vehicles.edit', id=id))
    
    # الحصول على المستخدمين المحددين
    authorized_user_ids = request.form.getlist('authorized_users')
    
    # مسح العلاقات الحالية
    vehicle.authorized_users.clear()
    
    # إضافة المستخدمين الجدد
    if authorized_user_ids:
        from models import User
        authorized_users = User.query.filter(User.id.in_(authorized_user_ids)).all()
        for user in authorized_users:
            vehicle.authorized_users.append(user)
    
    db.session.commit()
    
    # تسجيل الإجراء
    user_names = [user.name or user.username or user.email for user in vehicle.authorized_users]
    log_audit('update', 'vehicle_user_access', vehicle.id, 
              f'تم تحديث وصول المستخدمين للمركبة {vehicle.plate_number}. المستخدمون: {", ".join(user_names) if user_names else "لا يوجد"}')
    
    flash(f'تم تحديث إعدادات الوصول بنجاح! المستخدمون المخولون: {len(vehicle.authorized_users)}', 'success')
    return redirect(url_for('vehicles.edit', id=id))

@vehicles_bp.route('/<int:id>/confirm-delete')
@login_required
def confirm_delete(id):
        """صفحة تأكيد حذف السيارة"""
        vehicle = Vehicle.query.get_or_404(id)
        return render_template('vehicles/confirm_delete.html', vehicle=vehicle)

@vehicles_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
        """حذف سيارة"""
        vehicle = Vehicle.query.get_or_404(id)

        # التحقق من إدخال تأكيد الحذف
        confirmation = request.form.get('confirmation')
        if confirmation != 'تأكيد':
                flash('يجب كتابة كلمة "تأكيد" للمتابعة مع عملية الحذف!', 'danger')
                return redirect(url_for('vehicles.confirm_delete', id=id))

        # تسجيل الإجراء قبل الحذف
        plate_number = vehicle.plate_number
        log_audit('delete', 'vehicle', id, f'تم حذف السيارة: {plate_number}')

        db.session.delete(vehicle)
        db.session.commit()

        flash('تم حذف السيارة ومعلوماتها بنجاح!', 'success')
        return redirect(url_for('vehicles.index'))

# مسارات إدارة الحوادث المرورية
@vehicles_bp.route('/<int:id>/accident/create', methods=['GET', 'POST'])
@login_required
def create_accident(id):
        """إضافة سجل حادث مروري جديد"""
        vehicle = Vehicle.query.get_or_404(id)
        form = VehicleAccidentForm()
        form.vehicle_id.data = id

        if form.validate_on_submit():
                accident = VehicleAccident(
                        vehicle_id=id,
                        accident_date=form.accident_date.data,
                        driver_name=form.driver_name.data,
                        accident_status=form.accident_status.data,
                        vehicle_condition=form.vehicle_condition.data,
                        deduction_amount=form.deduction_amount.data,
                        deduction_status=form.deduction_status.data,
                        liability_percentage=form.liability_percentage.data,
                        accident_file_link=form.accident_file_link.data,
                        location=form.location.data,
                        police_report=form.police_report.data,
                        insurance_claim=form.insurance_claim.data,
                        description=form.description.data,
                        notes=form.notes.data
                )

                db.session.add(accident)

                # تحديث حالة السيارة إذا كان الحادث شديد
                if form.vehicle_condition.data and 'شديد' in form.vehicle_condition.data:
                        vehicle.status = 'accident'
                        vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('create', 'vehicle_accident', accident.id, 
                                 f'تم إضافة سجل حادث مروري للسيارة: {vehicle.plate_number}')

                flash('تم إضافة سجل الحادث المروري بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=id))

        return render_template('vehicles/create_accident.html', form=form, vehicle=vehicle)

@vehicles_bp.route('/accident/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_accident(id):
        """تعديل سجل حادث مروري"""
        accident = VehicleAccident.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(accident.vehicle_id)
        form = VehicleAccidentForm(obj=accident)

        if form.validate_on_submit():
                form.populate_obj(accident)
                accident.updated_at = datetime.utcnow()

                # تحديث حالة السيارة إذا كان الحادث شديد
                if form.vehicle_condition.data and 'شديد' in form.vehicle_condition.data:
                        vehicle.status = 'accident'
                elif accident.accident_status == 'مغلق':
                        # إعادة حالة السيارة إلى متاحة إذا تم إغلاق الحادث
                        vehicle.status = 'available'

                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('update', 'vehicle_accident', accident.id, 
                                 f'تم تعديل سجل حادث مروري للسيارة: {vehicle.plate_number}')

                flash('تم تعديل سجل الحادث المروري بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=vehicle.id))

        return render_template('vehicles/edit_accident.html', form=form, accident=accident)

@vehicles_bp.route('/accident/<int:id>/confirm-delete')
@login_required
def confirm_delete_accident(id):
        """عرض صفحة تأكيد حذف سجل حادث مروري"""
        accident = VehicleAccident.query.get_or_404(id)
        return render_template('vehicles/delete_accident.html', accident=accident)

@vehicles_bp.route('/accident/<int:id>/delete', methods=['POST'])
@login_required
def delete_accident(id):
        """حذف سجل حادث مروري"""
        accident = VehicleAccident.query.get_or_404(id)
        vehicle_id = accident.vehicle_id
        vehicle = Vehicle.query.get(vehicle_id)

        # تسجيل الإجراء قبل الحذف
        log_audit('delete', 'vehicle_accident', id, 
                         f'تم حذف سجل حادث مروري للسيارة: {vehicle.plate_number}')

        db.session.delete(accident)

        # تحقق مما إذا كانت حالة السيارة 'accident' وقم بتحديثها إلى 'available'
        # فقط إذا لم يكن لديها سجلات حوادث أخرى
        if vehicle.status == 'accident':
                other_accidents = VehicleAccident.query.filter_by(vehicle_id=vehicle_id).filter(VehicleAccident.id != id).all()
                if not other_accidents:
                        vehicle.status = 'available'
                        vehicle.updated_at = datetime.utcnow()

        db.session.commit()

        flash('تم حذف سجل الحادث المروري بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=vehicle_id))

# مسارات إدارة الإيجار
@vehicles_bp.route('/<int:id>/rental/create', methods=['GET', 'POST'])
@login_required
def create_rental(id):
        """إضافة معلومات إيجار لسيارة"""
        vehicle = Vehicle.query.get_or_404(id)

        # التحقق من عدم وجود إيجار نشط حالياً
        existing_rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()
        if existing_rental and request.method == 'GET':
                flash('يوجد إيجار نشط بالفعل لهذه السيارة!', 'warning')
                return redirect(url_for('vehicles.view', id=id))

        if request.method == 'POST':
                # استخراج البيانات من النموذج
                start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
                end_date_str = request.form.get('end_date')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
                monthly_cost = float(request.form.get('monthly_cost'))
                lessor_name = request.form.get('lessor_name')
                lessor_contact = request.form.get('lessor_contact')
                contract_number = request.form.get('contract_number')
                city = request.form.get('city')
                notes = request.form.get('notes')

                # إلغاء تنشيط الإيجارات السابقة
                if existing_rental:
                        existing_rental.is_active = False
                        existing_rental.updated_at = datetime.utcnow()

                # إنشاء سجل إيجار جديد
                rental = VehicleRental(
                        vehicle_id=id,
                        start_date=start_date,
                        end_date=end_date,
                        monthly_cost=monthly_cost,
                        is_active=True,
                        lessor_name=lessor_name,
                        lessor_contact=lessor_contact,
                        contract_number=contract_number,
                        city=city,
                        notes=notes
                )

                db.session.add(rental)

                # تحديث حالة السيارة
                vehicle.status = 'rented'
                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('create', 'vehicle_rental', rental.id, f'تم إضافة معلومات إيجار للسيارة: {vehicle.plate_number}')

                flash('تم إضافة معلومات الإيجار بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=id))

        return render_template('vehicles/rental_create.html', vehicle=vehicle)

@vehicles_bp.route('/rental/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rental(id):
        """تعديل معلومات إيجار"""
        rental = VehicleRental.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(rental.vehicle_id)

        if request.method == 'POST':
                # استخراج البيانات من النموذج
                start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
                end_date_str = request.form.get('end_date')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
                monthly_cost = float(request.form.get('monthly_cost'))
                is_active = bool(request.form.get('is_active'))
                lessor_name = request.form.get('lessor_name')
                lessor_contact = request.form.get('lessor_contact')
                contract_number = request.form.get('contract_number')
                city = request.form.get('city')
                notes = request.form.get('notes')

                # تحديث معلومات الإيجار
                rental.start_date = start_date
                rental.end_date = end_date
                rental.monthly_cost = monthly_cost
                rental.is_active = is_active
                rental.lessor_name = lessor_name
                rental.lessor_contact = lessor_contact
                rental.contract_number = contract_number
                rental.city = city
                rental.notes = notes
                rental.updated_at = datetime.utcnow()

                # تحديث حالة السيارة حسب حالة الإيجار
                if is_active:
                        vehicle.status = 'rented'
                else:
                        vehicle.status = 'available'
                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('update', 'vehicle_rental', rental.id, f'تم تعديل معلومات إيجار السيارة: {vehicle.plate_number}')

                flash('تم تعديل معلومات الإيجار بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=vehicle.id))

        return render_template('vehicles/rental_edit.html', rental=rental, vehicle=vehicle)

# مسارات إدارة الورشة
@vehicles_bp.route('/<int:id>/workshop/create', methods=['GET', 'POST'])
@login_required
def create_workshop(id):
        """إضافة سجل دخول السيارة للورشة"""
        vehicle = Vehicle.query.get_or_404(id)

        # فحص قيود العمليات للسيارات خارج الخدمة
        restrictions = check_vehicle_operation_restrictions(vehicle)
        if restrictions['blocked']:
                flash(restrictions['message'], 'error')
                return redirect(url_for('vehicles.view', id=id))

        if request.method == 'POST':
                # استخراج البيانات من النموذج
                entry_date = datetime.strptime(request.form.get('entry_date'), '%Y-%m-%d').date()
                exit_date_str = request.form.get('exit_date')
                exit_date = datetime.strptime(exit_date_str, '%Y-%m-%d').date() if exit_date_str else None
                reason = request.form.get('reason')
                description = request.form.get('description')
                repair_status = request.form.get('repair_status')
                cost = float(request.form.get('cost') or 0)
                workshop_name = request.form.get('workshop_name')
                technician_name = request.form.get('technician_name')
                delivery_link = request.form.get('delivery_link')
                notes = request.form.get('notes')

                # إنشاء سجل ورشة جديد
                workshop_record = VehicleWorkshop(
                        vehicle_id=id,
                        entry_date=entry_date,
                        exit_date=exit_date,
                        reason=reason,
                        description=description,
                        repair_status=repair_status,
                        cost=cost,
                        workshop_name=workshop_name,
                        technician_name=technician_name,
                        delivery_link=delivery_link,
                        notes=notes
                )

                db.session.add(workshop_record)

                # تحديث حالة السيارة
                if not exit_date:
                        vehicle.status = 'in_workshop'
                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # معالجة الصور المرفقة
                before_images = request.files.getlist('before_images')
                after_images = request.files.getlist('after_images')

                for image in before_images:
                        if image and image.filename:
                                image_path = save_image(image, 'workshop')
                                if image_path:
                                        image_record = VehicleWorkshopImage(
                                                workshop_record_id=workshop_record.id,
                                                image_type='before',
                                                image_path=image_path
                                        )
                                        db.session.add(image_record)

                for image in after_images:
                        if image and image.filename:
                                image_path = save_image(image, 'workshop')
                                if image_path:
                                        image_record = VehicleWorkshopImage(
                                                workshop_record_id=workshop_record.id,
                                                image_type='after',
                                                image_path=image_path
                                        )
                                        db.session.add(image_record)

                db.session.commit()

                # تسجيل الإجراء
                log_audit('create', 'vehicle_workshop', workshop_record.id, 
                                 f'تم إضافة سجل دخول الورشة للسيارة: {vehicle.plate_number}')

                flash('تم إضافة سجل دخول الورشة بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=id))

        return render_template(
                'vehicles/workshop_create.html', 
                vehicle=vehicle, 
                reasons=WORKSHOP_REASON_CHOICES,
                statuses=REPAIR_STATUS_CHOICES
        )

@vehicles_bp.route('/workshop/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workshop(id):
        """تعديل سجل ورشة"""
        current_app.logger.info(f"تم استدعاء edit_workshop مع معرف: {id}, طريقة: {request.method}")

        # الحصول على سجل الورشة والسيارة
        workshop = VehicleWorkshop.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(workshop.vehicle_id)
        current_app.logger.info(f"تم العثور على سجل الورشة: {workshop.id} للسيارة: {vehicle.plate_number}")

        # الحصول على الصور الحالية
        before_images = VehicleWorkshopImage.query.filter_by(workshop_record_id=id, image_type='before').all()
        after_images = VehicleWorkshopImage.query.filter_by(workshop_record_id=id, image_type='after').all()
        current_app.logger.info(f"تم العثور على {len(before_images)} صور قبل و {len(after_images)} صور بعد")

        if request.method == 'POST':
                try:
                        # تسجيل معلومات النموذج للتصحيح
                        current_app.logger.info(f"تم استقبال طلب POST لتعديل سجل الورشة {id}")
                        current_app.logger.info(f"بيانات النموذج: {request.form}")
                        current_app.logger.info(f"الملفات: {request.files}")

                        # الحصول على البيانات من الطلب
                        entry_date_str = request.form.get('entry_date')
                        exit_date_str = request.form.get('exit_date')
                        reason = request.form.get('reason')
                        description = request.form.get('description')
                        repair_status = request.form.get('repair_status')
                        cost_str = request.form.get('cost', '0')
                        workshop_name = request.form.get('workshop_name')
                        technician_name = request.form.get('technician_name')
                        delivery_link = request.form.get('delivery_link')
                        reception_link = request.form.get('reception_link')
                        notes = request.form.get('notes')

                        # تحويل التواريخ والتكلفة
                        entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date() if entry_date_str else None
                        exit_date = datetime.strptime(exit_date_str, '%Y-%m-%d').date() if exit_date_str else None
                        try:
                                cost = float(cost_str.replace(',', '.')) if cost_str and cost_str.strip() else 0.0
                        except ValueError:
                                cost = 0.0

                        # تحديث سجل الورشة
                        workshop.entry_date = entry_date
                        workshop.exit_date = exit_date
                        workshop.reason = reason
                        workshop.description = description
                        workshop.repair_status = repair_status
                        workshop.cost = cost
                        workshop.workshop_name = workshop_name
                        workshop.technician_name = technician_name
                        workshop.delivery_link = delivery_link
                        workshop.reception_link = reception_link
                        workshop.notes = notes
                        workshop.updated_at = datetime.utcnow()

                        # تحديث حالة السيارة إذا خرجت من الورشة
                        if exit_date and repair_status == 'completed':
                                other_active_records = VehicleWorkshop.query.filter(
                                        VehicleWorkshop.vehicle_id == vehicle.id,
                                        VehicleWorkshop.id != id,
                                        VehicleWorkshop.exit_date.is_(None)
                                ).count()

                                if other_active_records == 0:
                                        # لا توجد سجلات ورشة نشطة أخرى
                                        active_rental = VehicleRental.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()
                                        active_project = VehicleProject.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()

                                        if active_rental:
                                                vehicle.status = 'rented'
                                        elif active_project:
                                                vehicle.status = 'in_project'
                                        else:
                                                vehicle.status = 'available'

                        # تحديث السيارة
                        vehicle.updated_at = datetime.utcnow()
                        db.session.commit()

                        # معالجة الصور المرفقة
                        before_image_files = request.files.getlist('before_images')
                        after_image_files = request.files.getlist('after_images')

                        for image in before_image_files:
                                if image and image.filename:
                                        image_path = save_image(image, 'workshop')
                                        if image_path:
                                                workshop_image = VehicleWorkshopImage(
                                                        workshop_record_id=id,
                                                        image_type='before',
                                                        image_path=image_path
                                                )
                                                db.session.add(workshop_image)

                        for image in after_image_files:
                                if image and image.filename:
                                        image_path = save_image(image, 'workshop')
                                        if image_path:
                                                workshop_image = VehicleWorkshopImage(
                                                        workshop_record_id=id,
                                                        image_type='after',
                                                        image_path=image_path
                                                )
                                                db.session.add(workshop_image)

                        db.session.commit()

                        # تسجيل الإجراء
                        log_audit('update', 'vehicle_workshop', workshop.id, 
                                         f'تم تعديل سجل الورشة للسيارة {vehicle.plate_number}')

                        flash('تم تعديل سجل الورشة بنجاح!', 'success')
                        return redirect(url_for('vehicles.view', id=vehicle.id))

                except Exception as e:
                        current_app.logger.error(f"خطأ في حفظ سجل الورشة: {str(e)}")
                        db.session.rollback()
                        flash(f'حدث خطأ أثناء حفظ التعديلات: {str(e)}', 'danger')

        # عرض النموذج
        return render_template(
                'vehicles/workshop_edit.html', 
                workshop=workshop, 
                vehicle=vehicle,
                before_images=before_images,
                after_images=after_images,
                reasons=WORKSHOP_REASON_CHOICES,
                statuses=REPAIR_STATUS_CHOICES
        )

@vehicles_bp.route('/workshop/image/<int:id>/confirm-delete')
@login_required
def confirm_delete_workshop_image(id):
        """صفحة تأكيد حذف صورة من سجل الورشة"""
        image = VehicleWorkshopImage.query.get_or_404(id)
        workshop = VehicleWorkshop.query.get_or_404(image.workshop_record_id)
        vehicle = Vehicle.query.get_or_404(workshop.vehicle_id)

        return render_template(
                'vehicles/confirm_delete_workshop_image.html',
                image=image,
                workshop=workshop,
                vehicle=vehicle
        )

@vehicles_bp.route('/workshop/image/<int:id>/delete', methods=['POST'])
@login_required
def delete_workshop_image(id):
        """حذف صورة من سجل الورشة"""
        image = VehicleWorkshopImage.query.get_or_404(id)
        workshop_id = image.workshop_record_id
        workshop = VehicleWorkshop.query.get_or_404(workshop_id)

        # التحقق من إدخال تأكيد الحذف
        confirmation = request.form.get('confirmation')
        if confirmation != 'تأكيد':
                flash('يجب كتابة كلمة "تأكيد" للمتابعة مع عملية الحذف!', 'danger')
                return redirect(url_for('vehicles.confirm_delete_workshop_image', id=id))

        # حذف الملف الفعلي إذا كان موجوداً
        file_path = os.path.join(current_app.static_folder, image.image_path)
        if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(image)
        db.session.commit()

        # تسجيل الإجراء
        log_audit('delete', 'vehicle_workshop_image', id, 
                         f'تم حذف صورة من سجل الورشة للسيارة: {workshop.vehicle.plate_number}')

        flash('تم حذف الصورة بنجاح!', 'success')
        return redirect(url_for('vehicles.edit_workshop', id=workshop_id))

# مسارات إدارة المشاريع
@vehicles_bp.route('/<int:id>/project/create', methods=['GET', 'POST'])
@login_required
def create_project(id):
        """تخصيص السيارة لمشروع"""
        vehicle = Vehicle.query.get_or_404(id)

        # التحقق من عدم وجود تخصيص نشط حالياً
        existing_assignment = VehicleProject.query.filter_by(vehicle_id=id, is_active=True).first()
        if existing_assignment and request.method == 'GET':
                flash('هذه السيارة مخصصة بالفعل لمشروع نشط!', 'warning')
                return redirect(url_for('vehicles.view', id=id))

        if request.method == 'POST':
                # استخراج البيانات من النموذج
                project_name = request.form.get('project_name')
                location = request.form.get('location')
                manager_name = request.form.get('manager_name')
                start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
                end_date_str = request.form.get('end_date')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
                notes = request.form.get('notes')

                # إلغاء تنشيط التخصيصات السابقة
                if existing_assignment:
                        existing_assignment.is_active = False
                        existing_assignment.updated_at = datetime.utcnow()

                # إنشاء تخصيص جديد
                project = VehicleProject(
                        vehicle_id=id,
                        project_name=project_name,
                        location=location,
                        manager_name=manager_name,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=True,
                        notes=notes
                )

                db.session.add(project)

                # تحديث حالة السيارة
                vehicle.status = 'in_project'
                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('create', 'vehicle_project', project.id, 
                                 f'تم تخصيص السيارة {vehicle.plate_number} لمشروع {project_name}')

                flash('تم تخصيص السيارة للمشروع بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=id))

        return render_template('vehicles/project_create.html', vehicle=vehicle)

@vehicles_bp.route('/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
        """تعديل تخصيص المشروع"""
        project = VehicleProject.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(project.vehicle_id)

        if request.method == 'POST':
                # استخراج البيانات من النموذج
                project_name = request.form.get('project_name')
                location = request.form.get('location')
                manager_name = request.form.get('manager_name')
                start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
                end_date_str = request.form.get('end_date')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
                is_active = bool(request.form.get('is_active'))
                notes = request.form.get('notes')

                # تحديث التخصيص
                project.project_name = project_name
                project.location = location
                project.manager_name = manager_name
                project.start_date = start_date
                project.end_date = end_date
                project.is_active = is_active
                project.notes = notes
                project.updated_at = datetime.utcnow()

                # تحديث حالة السيارة
                if is_active:
                        vehicle.status = 'in_project'
                else:
                        # التحقق مما إذا كانت السيارة مؤجرة
                        active_rental = VehicleRental.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()

                        if active_rental:
                                vehicle.status = 'rented'
                        else:
                                vehicle.status = 'available'

                vehicle.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('update', 'vehicle_project', project.id, 
                                 f'تم تعديل تخصيص السيارة {vehicle.plate_number} للمشروع {project_name}')

                flash('تم تعديل تخصيص المشروع بنجاح!', 'success')
                return redirect(url_for('vehicles.view', id=vehicle.id))

        return render_template('vehicles/project_edit.html', project=project, vehicle=vehicle)

# في ملف routes.py
# بعد قسم الاستيرادات وقبل تعريف البلوبرنت أو أول route

def save_base64_image(base64_string, subfolder):
        """
        تستقبل سلسلة Base64، تفك تشفيرها، تحفظها كملف PNG فريد،
        وتُرجع المسار النسبي للملف.
        """
        if not base64_string or not base64_string.startswith('data:image/'):
                return None

        try:
                # إعداد مسار الحفظ
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', subfolder)
                os.makedirs(upload_folder, exist_ok=True)

                # فك التشفير
                header, encoded_data = base64_string.split(',', 1)
                image_data = base64.b64decode(encoded_data)

                # إنشاء اسم ملف فريد وحفظه
                filename = f"{uuid.uuid4().hex}.png"
                file_path = os.path.join(upload_folder, filename)
                with open(file_path, 'wb') as f:
                        f.write(image_data)

                # إرجاع المسار النسبي (مهم لقاعدة البيانات و HTML)
                return os.path.join(subfolder, filename)

        except Exception as e:
                print(f"Error saving Base64 image: {e}")
                return None

# في ملف routes.py

def save_uploaded_file(file, subfolder):
        """
        تحفظ ملف مرفوع (من request.files) في مجلد فرعي داخل uploads،
        وتُرجع المسار النسبي.
        """
        if not file or not file.filename:
                return None

        try:
                # إعداد مسار الحفظ
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', subfolder)
                os.makedirs(upload_folder, exist_ok=True)

                # الحصول على اسم آمن للملف وإنشاء اسم فريد
                from werkzeug.utils import secure_filename
                filename_secure = secure_filename(file.filename)
                # فصل الاسم والامتداد
                name, ext = os.path.splitext(filename_secure)
                # إنشاء اسم فريد لمنع الكتابة فوق الملفات
                unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)

                # إرجاع المسار النسبي
                return os.path.join(subfolder, unique_filename)

        except Exception as e:
                print(f"Error saving uploaded file: {e}")
                return None



# هذا هو الكود الكامل والنهائي للدالة، يمكنك استبدال دالة create_handover القديمة به

@vehicles_bp.route('/<int:id>/handover/create', methods=['GET', 'POST'])
@login_required
def create_handover(id):
    """إنشاء نموذج تسليم/استلام للسيارة مع حفظ نسخة كاملة من البيانات"""

    vehicle = Vehicle.query.get_or_404(id)

    # فحص قيود العمليات للسيارات خارج الخدمة
    restrictions = check_vehicle_operation_restrictions(vehicle)
    if restrictions['blocked']:
        flash(restrictions['message'], 'error')
        return redirect(url_for('vehicles.view', id=id))

    # هذا الجزء يعمل عند إرسال النموذج (طلب POST)
    if request.method == 'POST':
        try:
            # === 1. استخراج كل البيانات من النموذج (Forms) ===

            # --- البيانات الأساسية للعملية ---
            handover_type = request.form.get('handover_type')
            handover_date_str = request.form.get('handover_date')
            handover_time_str = request.form.get('handover_time')

            # --- معرفات الموظفين (السائق والمشرف) ---
            employee_id_str = request.form.get('employee_id')
            supervisor_employee_id_str = request.form.get('supervisor_employee_id')

            # --- البيانات النصية والمتغيرة الأخرى ---
            person_name_from_form = request.form.get('person_name', '').strip()
            supervisor_name_from_form = request.form.get('supervisor_name', '').strip()
            mileage = int(request.form.get('mileage', 0))
            fuel_level = request.form.get('fuel_level')
            project_name = request.form.get('project_name')
            city = request.form.get('city')
            reason_for_change = request.form.get('reason_for_change')
            vehicle_status_summary = request.form.get('vehicle_status_summary')
            notes = request.form.get('notes')
            reason_for_authorization = request.form.get('reason_for_authorization')
            authorization_details = request.form.get('authorization_details')
            movement_officer_name = request.form.get('movement_officer_name')
            form_link = request.form.get('form_link')
            custom_company_name = request.form.get('custom_company_name', '').strip() or None

            # --- بيانات قائمة الفحص (Checklist) ---
            has_spare_tire = 'has_spare_tire' in request.form
            has_fire_extinguisher = 'has_fire_extinguisher' in request.form
            has_first_aid_kit = 'has_first_aid_kit' in request.form
            has_warning_triangle = 'has_warning_triangle' in request.form
            has_tools = 'has_tools' in request.form
            has_oil_leaks = 'has_oil_leaks' in request.form
            has_gear_issue = 'has_gear_issue' in request.form
            has_clutch_issue = 'has_clutch_issue' in request.form
            has_engine_issue = 'has_engine_issue' in request.form
            has_windows_issue = 'has_windows_issue' in request.form
            has_tires_issue = 'has_tires_issue' in request.form
            has_body_issue = 'has_body_issue' in request.form
            has_electricity_issue = 'has_electricity_issue' in request.form
            has_lights_issue = 'has_lights_issue' in request.form
            has_ac_issue = 'has_ac_issue' in request.form

            # --- معالجة التواريخ والأوقات ---
            handover_date = datetime.strptime(handover_date_str, '%Y-%m-%d').date() if handover_date_str else date.today()
            handover_time = datetime.strptime(handover_time_str, '%H:%M').time() if handover_time_str else None

            # --- معالجة الصور والتواقيع والملفات المرفوعة (باستخدام دوالك المساعدة) ---
            saved_diagram_path = save_base64_image(request.form.get('damage_diagram_data'), 'diagrams')
            saved_supervisor_sig_path = save_base64_image(request.form.get('supervisor_signature_data'), 'signatures')
            saved_driver_sig_path = save_base64_image(request.form.get('driver_signature_data'), 'signatures')
            movement_officer_signature_path = save_base64_image(request.form.get('movement_officer_signature'), 'signatures')

            custom_logo_file = request.files.get('custom_logo_file')
            saved_custom_logo_path = save_uploaded_file(custom_logo_file, 'logos')

            # === 2. جلب الكائنات الكاملة من قاعدة البيانات ===
            driver = Employee.query.get(employee_id_str) if employee_id_str and employee_id_str.isdigit() else None
            supervisor = Employee.query.get(supervisor_employee_id_str) if supervisor_employee_id_str and supervisor_employee_id_str.isdigit() else None

            # === 3. إنشاء كائن VehicleHandover وتعبئته بالبيانات المنسوخة ===
            handover = VehicleHandover(
                vehicle_id=id,
                handover_type=handover_type,
                handover_date=handover_date,
                handover_time=handover_time,
                mileage=mileage,
                project_name=project_name,
                city=city,

                vehicle_car_type=f"{vehicle.make} {vehicle.model}",
                vehicle_plate_number=vehicle.plate_number,
                vehicle_model_year=str(vehicle.year),

                employee_id=driver.id if driver else None,
                person_name=driver.name if driver else person_name_from_form,
                driver_company_id=driver.employee_id if driver else None,
                driver_phone_number=driver.mobile if driver else None,
                driver_residency_number=driver.national_id if driver else None,
                driver_contract_status=driver.contract_status if driver else None,
                driver_license_status=driver.license_status if driver else None,
                driver_signature_path=saved_driver_sig_path,

                supervisor_employee_id=supervisor.id if supervisor else None,
                supervisor_name=supervisor.name if supervisor else supervisor_name_from_form,
                supervisor_company_id=supervisor.employee_id if supervisor else None,
                supervisor_phone_number=supervisor.mobile if supervisor else None,
                supervisor_residency_number=supervisor.national_id if supervisor else None,
                supervisor_contract_status=supervisor.contract_status if supervisor else None,
                supervisor_license_status=supervisor.license_status if supervisor else None,
                supervisor_signature_path=saved_supervisor_sig_path,

                reason_for_change=reason_for_change,
                vehicle_status_summary=vehicle_status_summary,
                notes=notes,
                reason_for_authorization=reason_for_authorization,
                authorization_details=authorization_details,
                fuel_level=fuel_level,
                has_spare_tire=has_spare_tire,
                has_fire_extinguisher=has_fire_extinguisher,
                has_first_aid_kit=has_first_aid_kit,
                has_warning_triangle=has_warning_triangle,
                has_tools=has_tools,
                has_oil_leaks=has_oil_leaks,
                has_gear_issue=has_gear_issue,
                has_clutch_issue=has_clutch_issue,
                has_engine_issue=has_engine_issue,
                has_windows_issue=has_windows_issue,
                has_tires_issue=has_tires_issue,
                has_body_issue=has_body_issue,
                has_electricity_issue=has_electricity_issue,
                has_lights_issue=has_lights_issue,
                has_ac_issue=has_ac_issue,

                movement_officer_name=movement_officer_name,
                movement_officer_signature_path=movement_officer_signature_path,
                damage_diagram_path=saved_diagram_path,
                form_link=form_link,
                custom_company_name=custom_company_name,
                custom_logo_path=saved_custom_logo_path
            )

            db.session.add(handover)
            db.session.commit()

            # === 4. حفظ الملفات المرفقة وتحديث حالة السائق (لا تغيير في المنطق) ===
            update_vehicle_driver(id)

            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    file_path, file_type = save_file(file, 'handover')
                    if file_path:
                        file_description = request.form.get(f'description_{file.filename}', '')
                        file_record = VehicleHandoverImage(
                            handover_record_id=handover.id,
                            file_path=file_path,
                            file_type=file_type,
                            file_description=file_description,
                            image_path=file_path,  # للتوافق
                            image_description=file_description # للتوافق
                        )
                        db.session.add(file_record)

            db.session.commit()

            action_type = 'تسليم' if handover_type == 'delivery' else 'استلام'
            log_audit('create', 'vehicle_handover', handover.id, f'تم إنشاء نموذج {action_type} للسيارة: {vehicle.plate_number}')

            flash(f'تم إنشاء نموذج {action_type} بنجاح!', 'success')
            return redirect(url_for('vehicles.view', id=id))

        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            flash(f'حدث خطأ غير متوقع أثناء الحفظ: {str(e)}', 'danger')
            # إعادة عرض الصفحة مرة أخرى في حالة الخطأ لتجنب فقدان البيانات
            # استرجاع البيانات لعرضها مرة أخرى في القالب
            employees_for_template = Employee.query.order_by(Employee.name).all()
            departments_for_template = Department.query.order_by(Department.name).all()
            # ... جلب handover_types ...

            return render_template(
                'vehicles/handover_create.html', 
                vehicle=vehicle,
                handover_types=HANDOVER_TYPE_CHOICES,
                default_handover_type=request.form.get('handover_type'),
                # default_handover_type=...
                employees=employees_for_template,
                departments=departments_for_template,
                form_data=request.form # إعادة إرسال بيانات النموذج للملء التلقائي
            )

    # هذا الجزء يعمل عند فتح الصفحة لأول مرة (طلب GET)
    # تحديد نوع النموذج (تسليم أو استلام) من معلمة الاستعلام
    default_type = request.args.get('type', '')
    if default_type == 'delivery':
        default_handover_type = 'delivery'
    elif default_type == 'receive':
        default_handover_type = 'receive'
    else:
        default_handover_type = 'delivery' # أو أي قيمة افتراضية أخرى

    # جلب قائمة الموظفين مع أقسامهم والأقسام للاختيار منهم
    employees = Employee.query.options(
        db.joinedload(Employee.departments)
    ).order_by(Employee.name).all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        'vehicles/handover_create.html', 
        vehicle=vehicle,
        handover_types=HANDOVER_TYPE_CHOICES, # تأكد من أن هذا المتغير معرف أو قم بتمرير قائمة
        default_handover_type=default_handover_type,
        employees=employees,
        departments=departments
    )







# @vehicles_bp.route('/<int:id>/handover/create', methods=['GET', 'POST'])
# @login_required
# def create_handover(id):
#     import base64
#     import uuid

#     """إنشاء نموذج تسليم/استلام للسيارة"""
#     vehicle = Vehicle.query.get_or_404(id)

#     # تحديد نوع النموذج (تسليم أو استلام) من معلمة الاستعلام
#     default_type = request.args.get('type', '')
#     if default_type == 'delivery':
#         default_handover_type = 'delivery'
#     elif default_type == 'receive':
#         default_handover_type = 'receive'
#     else:
#         default_handover_type = None

#     # جلب قائمة الموظفين والأقسام للاختيار منهم
#     employees = Employee.query.order_by(Employee.name).all()
#     departments = Department.query.order_by(Department.name).all()

#     if request.method == 'POST':
#         # استخراج البيانات من النموذج
#         handover_type = request.form.get('handover_type')
#         handover_date = datetime.strptime(request.form.get('handover_date'), '%Y-%m-%d').date()
#         person_name = request.form.get('person_name')
#         employee_id = request.form.get('employee_id')  # معرف الموظف من النموذج
#         vehicle_condition = request.form.get('vehicle_condition')
#         fuel_level = request.form.get('fuel_level')
#         mileage = int(request.form.get('mileage'))
#         has_spare_tire = 'has_spare_tire' in request.form
#         has_fire_extinguisher = 'has_fire_extinguisher' in request.form
#         has_first_aid_kit = 'has_first_aid_kit' in request.form
#         has_warning_triangle = 'has_warning_triangle' in request.form
#         has_tools = 'has_tools' in request.form
#         form_link = request.form.get('form_link')
#         notes = request.form.get('notes')
#                 # --- استخراج بيانات قائمة الفحص الجديدة ---
#         has_oil_leaks = 'has_oil_leaks' in request.form
#         has_gear_issue = 'has_gear_issue' in request.form
#         has_clutch_issue = 'has_clutch_issue' in request.form
#         has_engine_issue = 'has_engine_issue' in request.form
#         has_windows_issue = 'has_windows_issue' in request.form
#         has_tires_issue = 'has_tires_issue' in request.form
#         has_body_issue = 'has_body_issue' in request.form
#         has_electricity_issue = 'has_electricity_issue' in request.form
#         has_lights_issue = 'has_lights_issue' in request.form
#         has_ac_issue = 'has_ac_issue' in request.form
#         custom_logo = request.files.get('custom_logo_file')
#         saved_custom_logo_path = save_uploaded_file(custom_logo, 'logos') # حفظ في مجلد 'logos'
#         custom_company_name = request.form.get('custom_company_name').strip() or None


#         # --- استقبال وحفظ الصور المرسومة والمرفوعة (باستخدام الدالة المساعدة) ---
#         damage_diagram_base64 = request.form.get('damage_diagram_data')
#         supervisor_sig_base64 = request.form.get('supervisor_signature_data')
#         driver_sig_base64 = request.form.get('driver_signature_data')
#         saved_diagram_path = save_base64_image(damage_diagram_base64, 'diagrams')
#         saved_supervisor_sig_path = save_base64_image(supervisor_sig_base64, 'signatures')
#         saved_driver_sig_path = save_base64_image(driver_sig_base64, 'signatures')






#         # إنشاء سجل تسليم/استلام جديد
#         handover = VehicleHandover(
#             vehicle_id=id,
#             handover_type=handover_type,
#             handover_date=handover_date,
#             person_name=person_name,
#             employee_id=int(employee_id) if employee_id else None, # تخزين معرف الموظف إذا تم اختياره
#             vehicle_condition=vehicle_condition,
#             fuel_level=fuel_level,
#             mileage=mileage,
#             has_spare_tire=has_spare_tire,
#             has_fire_extinguisher=has_fire_extinguisher,
#             has_first_aid_kit=has_first_aid_kit,
#             has_warning_triangle=has_warning_triangle,
#             has_tools=has_tools,
#             form_link=form_link,
#             notes=notes,
#             has_oil_leaks=has_oil_leaks,
#             has_gear_issue=has_gear_issue,
#             has_clutch_issue=has_clutch_issue,
#             has_engine_issue=has_engine_issue,
#             has_windows_issue=has_windows_issue,
#             has_tires_issue=has_tires_issue,
#             has_body_issue=has_body_issue,
#             has_electricity_issue=has_electricity_issue,
#             has_lights_issue=has_lights_issue,
#             has_ac_issue=has_ac_issue,
#             damage_diagram_path=saved_diagram_path,
#             supervisor_signature_path=saved_supervisor_sig_path,
#             driver_signature_path=saved_driver_sig_path,
#             custom_company_name=custom_company_name,
#             custom_logo_path=saved_custom_logo_path

#         )

#         db.session.add(handover)
#         db.session.commit()

#         # تحديث اسم السائق في جدول السيارات
#         update_vehicle_driver(id)

#         # معالجة الملفات المرفقة (صور و PDF)
#         files = request.files.getlist('files')

#         for file in files:
#             if file and file.filename:
#                 file_path, file_type = save_file(file, 'handover')
#                 if file_path:
#                     file_description = request.form.get(f'description_{file.filename}', '')
#                     # للحفاظ على توافق البيانات، نستخدم نفس القيمة لحقلي image_path و file_path
#                     file_record = VehicleHandoverImage(
#                         handover_record_id=handover.id,
#                         image_path=file_path,  # للتوافق مع القيود على قاعدة البيانات
#                         image_description=file_description,  # للتوافق مع القيود على قاعدة البيانات
#                         file_path=file_path,
#                         file_type=file_type,
#                         file_description=file_description
#                     )
#                     db.session.add(file_record)

#         db.session.commit()

#         # تسجيل الإجراء
#         action_type = 'تسليم' if handover_type == 'delivery' else 'استلام'
#         log_audit('create', 'vehicle_handover', handover.id, 
#                  f'تم إنشاء نموذج {action_type} للسيارة: {vehicle.plate_number}')

#         flash(f'تم إنشاء نموذج {action_type} بنجاح!', 'success')
#         return redirect(url_for('vehicles.view', id=id))

#     return render_template(
#         'vehicles/handover_create.html', 
#         vehicle=vehicle,
#         handover_types=HANDOVER_TYPE_CHOICES,
#         default_handover_type=default_handover_type,
#         employees=employees,
#         departments=departments
#     )


# # مسارات تسليم واستلام السيارات
# @vehicles_bp.route('/<int:id>/handover/create', methods=['GET', 'POST'])
# @login_required
# def create_handover(id):
#       import base64
#       import uuid

#       """إنشاء نموذج تسليم/استلام للسيارة"""
#       vehicle = Vehicle.query.get_or_404(id)

#       # تحديد نوع النموذج (تسليم أو استلام) من معلمة الاستعلام
#       default_type = request.args.get('type', '')
#       if default_type == 'delivery':
#               default_handover_type = 'delivery'
#       elif default_type == 'receive':
#               default_handover_type = 'receive'
#       else:
#               default_handover_type = None

#       # يمكنك استبدال كل محتوى "if request.method == 'POST':" بهذا الكود
#     # جلب قائمة الموظفين والأقسام للاختيار منهم
#       employees = Employee.query.order_by(Employee.name).all()
#       departments = Department.query.order_by(Department.name).all()


#     if request.method == 'POST':

#             # === 1. استخراج كل البيانات من النموذج (Forms) ===

#             # --- البيانات الأساسية للعملية ---
#             handover_type = request.form.get('handover_type')
#             handover_date_str = request.form.get('handover_date')
#             handover_time_str = request.form.get('handover_time')

#             # --- معرفات الموظفين (السائق والمشرف) ---
#             employee_id_str = request.form.get('employee_id') # معرف السائق
#             supervisor_employee_id_str = request.form.get('supervisor_employee_id') # معرف المشرف

#             # --- البيانات النصية والمتغيرة الأخرى ---
#             person_name_from_form = request.form.get('person_name', '').strip() # اسم السائق إذا تم إدخاله يدوياً
#             supervisor_name_from_form = request.form.get('supervisor_name', '').strip() # اسم المشرف إذا تم إدخاله يدوياً
#             mileage = int(request.form.get('mileage', 0))
#             fuel_level = request.form.get('fuel_level')
#             project_name = request.form.get('project_name')
#             city = request.form.get('city')
#             reason_for_change = request.form.get('reason_for_change')
#             vehicle_status_summary = request.form.get('vehicle_status_summary')
#             notes = request.form.get('notes')
#             reason_for_authorization = request.form.get('reason_for_authorization')
#             authorization_details = request.form.get('authorization_details')
#             movement_officer_name = request.form.get('movement_officer_name')
#             form_link = request.form.get('form_link')
#             custom_company_name = request.form.get('custom_company_name', '').strip() or None

#             # --- بيانات قائمة الفحص (Checklist) ---
#             has_spare_tire = 'has_spare_tire' in request.form
#             has_fire_extinguisher = 'has_fire_extinguisher' in request.form
#             has_first_aid_kit = 'has_first_aid_kit' in request.form
#             has_warning_triangle = 'has_warning_triangle' in request.form
#             has_tools = 'has_tools' in request.form
#             has_oil_leaks = 'has_oil_leaks' in request.form
#             has_gear_issue = 'has_gear_issue' in request.form
#             has_clutch_issue = 'has_clutch_issue' in request.form
#             has_engine_issue = 'has_engine_issue' in request.form
#             has_windows_issue = 'has_windows_issue' in request.form
#             has_tires_issue = 'has_tires_issue' in request.form
#             has_body_issue = 'has_body_issue' in request.form
#             has_electricity_issue = 'has_electricity_issue' in request.form
#             has_lights_issue = 'has_lights_issue' in request.form
#             has_ac_issue = 'has_ac_issue' in request.form

#             # --- معالجة التواريخ والأوقات ---
#             handover_date = datetime.strptime(handover_date_str, '%Y-%m-%d').date() if handover_date_str else date.today()
#             handover_time = datetime.strptime(handover_time_str, '%H:%M').time() if handover_time_str else None

#             # --- معالجة الصور والتواقيع والملفات المرفوعة (باستخدام دوالك المساعدة) ---
#             saved_diagram_path = save_base64_image(request.form.get('damage_diagram_data'), 'diagrams')
#             saved_supervisor_sig_path = save_base64_image(request.form.get('supervisor_signature_data'), 'signatures')
#             saved_driver_sig_path = save_base64_image(request.form.get('driver_signature_data'), 'signatures')
#             movement_officer_signature_path = save_base64_image(request.form.get('movement_officer_signature_data'), 'signatures')

#             custom_logo_file = request.files.get('custom_logo_file')
#             saved_custom_logo_path = save_uploaded_file(custom_logo_file, 'logos')

#             # === 2. جلب الكائنات الكاملة من قاعدة البيانات ===
#             driver = Employee.query.get(employee_id_str) if employee_id_str else None
#             supervisor = Employee.query.get(supervisor_employee_id_str) if supervisor_employee_id_str else None

#             # === 3. إنشاء كائن VehicleHandover وتعبئته بالبيانات المنسوخة ===
#             handover = VehicleHandover(
#                 vehicle_id=id,

#                 # --- معلومات العملية ---
#                 handover_type=handover_type,
#                 handover_date=handover_date,
#                 handover_time=handover_time,
#                 mileage=mileage,
#                 project_name=project_name,
#                 city=city,

#                 # --- معلومات السيارة (منسوخة) ---
#                 vehicle_car_type=f"{vehicle.make} {vehicle.model}",
#                 vehicle_plate_number=vehicle.plate_number,
#                 vehicle_model_year=str(vehicle.year),

#                 # --- معلومات السائق (منسوخة) - الأولوية للبيانات من الكائن إذا تم اختياره ---
#                 employee_id=driver.id if driver else None,
#                 person_name=driver.name if driver else person_name_from_form,
#                 driver_company_id=driver.employee_id if driver else None,
#                 driver_phone_number=driver.mobile if driver else None,
#                 driver_residency_number=driver.national_id if driver else None,
#                 driver_contract_status=driver.contract_status if driver else None,
#                 driver_license_status=driver.license_status if driver else None,
#                 driver_signature_path=saved_driver_sig_path,

#                 # --- معلومات المشرف (منسوخة) - نفس منطق السائق ---
#                 supervisor_employee_id=supervisor.id if supervisor else None,
#                 supervisor_name=supervisor.name if supervisor else supervisor_name_from_form,
#                 supervisor_company_id=supervisor.employee_id if supervisor else None,
#                 supervisor_phone_number=supervisor.mobile if supervisor else None,
#                 supervisor_residency_number=supervisor.national_id if supervisor else None,
#                 supervisor_contract_status=supervisor.contract_status if supervisor else None,
#                 supervisor_license_status=supervisor.license_status if supervisor else None,
#                 supervisor_signature_path=saved_supervisor_sig_path,

#                 # --- معلومات الفحص والملاحظات والتفويض ---
#                 reason_for_change=reason_for_change,
#                 vehicle_status_summary=vehicle_status_summary,
#                 notes=notes,
#                 reason_for_authorization=reason_for_authorization,
#                 authorization_details=authorization_details,
#                 fuel_level=fuel_level,
#                 has_spare_tire=has_spare_tire,
#                 has_fire_extinguisher=has_fire_extinguisher,
#                 has_first_aid_kit=has_first_aid_kit,
#                 has_warning_triangle=has_warning_triangle,
#                 has_tools=has_tools,
#                 has_oil_leaks=has_oil_leaks,
#                 has_gear_issue=has_gear_issue,
#                 has_clutch_issue=has_clutch_issue,
#                 has_engine_issue=has_engine_issue,
#                 has_windows_issue=has_windows_issue,
#                 has_tires_issue=has_tires_issue,
#                 has_body_issue=has_body_issue,
#                 has_electricity_issue=has_electricity_issue,
#                 has_lights_issue=has_lights_issue,
#                 has_ac_issue=has_ac_issue,

#                 # --- معلومات متنوعة ---
#                 movement_officer_name=movement_officer_name,
#                 movement_officer_signature_path=movement_officer_signature_path,
#                 damage_diagram_path=saved_diagram_path,
#                 form_link=form_link,
#                 custom_company_name=custom_company_name,
#                 custom_logo_path=saved_custom_logo_path
#             )

#             db.session.add(handover)
#             db.session.commit()

#             # === 4. حفظ الملفات المرفقة وتحديث حالة السائق (لا تغيير في المنطق) ===
#             update_vehicle_driver(id)

#             files = request.files.getlist('files')
#             for file in files:
#                 if file and file.filename:
#                     file_path, file_type = save_file(file, 'handover')
#                     if file_path:
#                         file_description = request.form.get(f'description_{file.filename}', '')
#                         file_record = VehicleHandoverImage(
#                             handover_record_id=handover.id,
#                             file_path=file_path,
#                             file_type=file_type,
#                             file_description=file_description
#                         )
#                         db.session.add(file_record)

#             db.session.commit()

#             action_type = 'تسليم' if handover_type == 'delivery' else 'استلام'
#             log_audit('create', 'vehicle_handover', handover.id, f'تم إنشاء نموذج {action_type} للسيارة: {vehicle.plate_number}')

#             flash(f'تم إنشاء نموذج {action_type} بنجاح!', 'success')
#             return redirect(url_for('vehicles.view', id=id))

#         except Exception as e:
#             db.session.rollback()
#             # مهم جداً لطباعة الأخطاء أثناء التطوير
#             import traceback
#             traceback.print_exc()
#             flash(f'حدث خطأ غير متوقع أثناء الحفظ: {str(e)}', 'danger')
#             # نعيد توجيه المستخدم لنفس الصفحة لكي لا يفقد البيانات التي أدخلها
#             return render_template(
#                 'vehicles/handover_create.html', 
#                 vehicle=vehicle,
#                 # handover_types=HANDOVER_TYPE_CHOICES,
#                 default_handover_type=default_handover_type,
#                 employees=employees,
#                 departments=departments,
#                 # يمكنك إعادة إرسال بيانات النموذج هنا للملء التلقائي في حال الخطأ
#                 form_data=request.form 
#             )











#       return render_template(
#               'vehicles/handover_create.html', 
#               vehicle=vehicle,
#               handover_types=HANDOVER_TYPE_CHOICES,
#               default_handover_type=default_handover_type,
#               employees=employees,
#               departments=departments
#       )











@vehicles_bp.route('/handover/<int:id>/view')
@vehicles_bp.route('/<int:vehicle_id>/handover/<int:id>')
@login_required
def view_handover(id, vehicle_id=None):
        """عرض تفاصيل نموذج تسليم/استلام"""
        handover = VehicleHandover.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
        images = VehicleHandoverImage.query.filter_by(handover_record_id=id).all()

        # تنسيق التاريخ
        handover.formatted_handover_date = format_date_arabic(handover.handover_date)

        # تحديد نوع التسليم بالعربية
        if handover.handover_type in ['delivery', 'تسليم', 'handover']:
            handover_type_name = 'تسليم'
        elif handover.handover_type in ['return', 'استلام']:
            handover_type_name = 'استلام'
        else:
            handover_type_name = handover.handover_type

        return render_template(
                'vehicles/handover_view.html',
                handover=handover,
                vehicle=vehicle,
                images=images,
                handover_type_name=handover_type_name
        )

@vehicles_bp.route('/handover/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_handover(id):
        """تعديل بيانات نموذج تسليم/استلام"""
        handover = VehicleHandover.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(handover.vehicle_id)

        # الحصول على صور نموذج التسليم/الاستلام للعرض
        images = VehicleHandoverImage.query.filter_by(handover_record_id=id).all()

        # تحويل التاريخ إلى النسق المناسب للنموذج
        handover_date_str = handover.handover_date.strftime('%Y-%m-%d') if handover.handover_date else None

        # تحديد اسم نوع النموذج
        handover_type_name = 'تسليم' if handover.handover_type == 'delivery' else 'استلام'

        if request.method == 'POST':
                try:
                        # استخراج البيانات من النموذج
                        handover_date_str = request.form.get('handover_date')
                        person_name = request.form.get('person_name')
                        mileage_str = request.form.get('mileage')
                        fuel_level = request.form.get('fuel_level')
                        vehicle_condition = request.form.get('vehicle_condition')
                        form_link = request.form.get('form_link')
                        notes = request.form.get('notes')

                        # معالجة مربعات الاختيار
                        has_spare_tire = 'has_spare_tire' in request.form
                        has_fire_extinguisher = 'has_fire_extinguisher' in request.form
                        has_first_aid_kit = 'has_first_aid_kit' in request.form
                        has_warning_triangle = 'has_warning_triangle' in request.form
                        has_tools = 'has_tools' in request.form

                        # تحويل التاريخ والعداد
                        handover_date = datetime.strptime(handover_date_str, '%Y-%m-%d').date() if handover_date_str else None
                        try:
                                mileage = int(mileage_str.replace(',', '')) if mileage_str else 0
                        except (ValueError, TypeError) as e:
                                flash(f'خطأ في تنسيق قراءة العداد: {str(e)}', 'danger')
                                return redirect(url_for('vehicles.edit_handover', id=id))

                        # تحديث بيانات النموذج
                        handover.handover_date = handover_date
                        handover.person_name = person_name
                        handover.mileage = mileage
                        handover.fuel_level = fuel_level
                        handover.vehicle_condition = vehicle_condition
                        handover.form_link = form_link
                        handover.notes = notes
                        handover.has_spare_tire = has_spare_tire
                        handover.has_fire_extinguisher = has_fire_extinguisher
                        handover.has_first_aid_kit = has_first_aid_kit
                        handover.has_warning_triangle = has_warning_triangle
                        handover.has_tools = has_tools
                        handover.updated_at = datetime.utcnow()

                        db.session.commit()

                        # تسجيل الإجراء
                        log_audit('update', 'vehicle_handover', handover.id, f'تم تعديل نموذج {handover_type_name} للسيارة: {vehicle.plate_number}')

                        flash(f'تم تعديل بيانات نموذج {handover_type_name} بنجاح!', 'success')
                        return redirect(url_for('vehicles.view_handover', id=id))

                except Exception as e:
                        db.session.rollback()
                        current_app.logger.error(f"Error updating handover form: {str(e)}")
                        flash(f'حدث خطأ أثناء تعديل نموذج التسليم/الاستلام: {str(e)}', 'danger')

        # جلب قائمة الموظفين للاختيار منهم
        employees = Employee.query.order_by(Employee.name).all()
        departments = Department.query.order_by(Department.name).all()

        return render_template(
                'vehicles/edit_handover.html',
                handover=handover,
                vehicle=vehicle,
                images=images,
                handover_date=handover_date_str,
                handover_type_name=handover_type_name,
                employees=employees,
                departments=departments
        )

@vehicles_bp.route('/<int:vehicle_id>/handovers/confirm-delete', methods=['POST'])
@login_required
def confirm_delete_handovers(vehicle_id):
        """صفحة تأكيد حذف سجلات التسليم/الاستلام المحددة"""
        vehicle = Vehicle.query.get_or_404(vehicle_id)

        # الحصول على معرفات السجلات المحددة
        record_ids = request.form.getlist('handover_ids[]')

        if not record_ids:
                flash('لم يتم تحديد أي سجل للحذف!', 'warning')
                return redirect(url_for('vehicles.view', id=vehicle_id))

        # تحويل المعرفات إلى أرقام صحيحة
        record_ids = [int(id) for id in record_ids]

        # الحصول على السجلات المحددة
        records = VehicleHandover.query.filter(VehicleHandover.id.in_(record_ids)).all()

        # التحقق من أن السجلات تنتمي للسيارة المحددة
        for record in records:
                if record.vehicle_id != vehicle_id:
                        flash('خطأ في البيانات المرسلة! بعض السجلات لا تنتمي لهذه السيارة.', 'danger')
                        return redirect(url_for('vehicles.view', id=vehicle_id))

        # تنسيق التواريخ للعرض
        for record in records:
                record.formatted_handover_date = format_date_arabic(record.handover_date)

        return render_template(
                'vehicles/confirm_delete_handovers.html',
                vehicle=vehicle,
                records=records,
                record_ids=record_ids
        )

@vehicles_bp.route('/<int:vehicle_id>/handovers/delete', methods=['POST'])
@login_required
def delete_handovers(vehicle_id):
        """حذف سجلات التسليم/الاستلام المحددة"""
        vehicle = Vehicle.query.get_or_404(vehicle_id)

        # التحقق من إدخال تأكيد الحذف
        confirmation = request.form.get('confirmation')
        if confirmation != 'تأكيد':
                flash('يجب كتابة كلمة "تأكيد" للمتابعة مع عملية الحذف!', 'danger')
                return redirect(url_for('vehicles.view', id=vehicle_id))

        # الحصول على معرفات السجلات المحددة
        record_ids = request.form.getlist('record_ids')
        if not record_ids:
                flash('لم يتم تحديد أي سجل للحذف!', 'warning')
                return redirect(url_for('vehicles.view', id=vehicle_id))

        # تحويل المعرفات إلى أرقام صحيحة
        record_ids = [int(id) for id in record_ids]

        # التحقق من أن السجلات تنتمي للسيارة المحددة
        records = VehicleHandover.query.filter(VehicleHandover.id.in_(record_ids)).all()
        for record in records:
                if record.vehicle_id != vehicle_id:
                        flash('خطأ في البيانات المرسلة! بعض السجلات لا تنتمي لهذه السيارة.', 'danger')
                        return redirect(url_for('vehicles.view', id=vehicle_id))

        # حذف السجلات
        for record in records:
                # تسجيل الإجراء قبل الحذف
                log_audit('delete', 'vehicle_handover', record.id, 
                                 f'تم حذف سجل {"تسليم" if record.handover_type == "delivery" else "استلام"} للسيارة {vehicle.plate_number}')

                db.session.delete(record)

        db.session.commit()

        # رسالة نجاح
        if len(records) == 1:
                flash('تم حذف السجل بنجاح!', 'success')
        else:
                flash(f'تم حذف {len(records)} سجلات بنجاح!', 'success')

        return redirect(url_for('vehicles.view', id=vehicle_id))

@vehicles_bp.route('/handover/<int:id>/pdf')
@login_required
def handover_pdf(id):
        """إنشاء نموذج تسليم/استلام كملف PDF"""
        from flask import send_file, flash, redirect, url_for
        import io
        import os
        from datetime import datetime
        # استخدام مولد PDF المحسن مع WeasyPrint
        from utils.weasyprint_handover_pdf import generate_handover_report_pdf

        try:
                # التأكد من تحويل المعرف إلى عدد صحيح
                id = int(id) if not isinstance(id, int) else id

                # جلب البيانات
                handover = VehicleHandover.query.get_or_404(id)
                vehicle = Vehicle.query.get_or_404(handover.vehicle_id)

                # تجهيز البيانات
                handover_data = {
                        'vehicle': {
                                'plate_number': str(vehicle.plate_number),
                                'make': str(vehicle.make),
                                'model': str(vehicle.model),
                                'year': int(vehicle.year),
                                'color': str(vehicle.color)
                        },
                        'handover_type': 'تسليم' if handover.handover_type == 'delivery' else 'استلام',
                        'handover_date': handover.handover_date.strftime('%Y-%m-%d'),
                        'person_name': str(handover.person_name),
                        'vehicle_condition': str(handover.vehicle_condition),
                        'fuel_level': str(handover.fuel_level),
                        'mileage': int(handover.mileage),
                        'has_spare_tire': bool(handover.has_spare_tire),
                        'has_fire_extinguisher': bool(handover.has_fire_extinguisher),
                        'has_first_aid_kit': bool(handover.has_first_aid_kit),
                        'has_warning_triangle': bool(handover.has_warning_triangle),
                        'has_tools': bool(handover.has_tools),
                        'notes': str(handover.notes) if handover.notes else "",
                        'form_link': str(handover.form_link) if handover.form_link else ""
                }

                # إضافة معلومات المشرف إذا وجدت
                if hasattr(handover, 'supervisor_name') and handover.supervisor_name:
                        handover_data['supervisor_name'] = str(handover.supervisor_name)

                # إنشاء ملف PDF باستخدام المولد المحسن
                pdf_buffer = generate_handover_report_pdf(vehicle, handover)

                # تحديد اسم الملف
                filename = f"handover_form_{vehicle.plate_number}.pdf"

                # إرسال الملف للمستخدم
                return send_file(
                        pdf_buffer,
                        download_name=filename,
                        as_attachment=True,
                        mimetype='application/pdf'
                )
        except Exception as e:
                # في حالة حدوث خطأ، عرض رسالة الخطأ والعودة إلى صفحة عرض السيارة
                flash(f'خطأ في إنشاء ملف PDF: {str(e)}', 'danger')
                return redirect(url_for('vehicles.view', id=vehicle.id if 'vehicle' in locals() else id))



@vehicles_bp.route('/handover/<int:id>/view/public')
def handover_view_public(id):
    """عرض صفحة PDF العامة مع زر الرجوع للمستخدمين المسجلي الدخول"""
    handover = VehicleHandover.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(handover.vehicle_id)

    return render_template(
        'vehicles/handover_pdf_public.html',
        handover=handover,
        vehicle=vehicle,
        pdf_url=url_for('vehicles.handover_pdf_public', id=id)
    )

@vehicles_bp.route('/handover/<int:id>/pdf/public')
def handover_pdf_public(id):
    """إنشاء ملف PDF لنموذج تسليم/استلام باستخدام نفس خط beIN Normal المحسن من نظام الرواتب"""
    try:
        # الحصول على سجل التسليم/الاستلام
        handover = VehicleHandover.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(handover.vehicle_id)

        # استخدام مولد PDF الأصلي مع تحديث خط beIN-Normal
        from utils.fpdf_handover_pdf import generate_handover_report_pdf_weasyprint

        # إنشاء PDF باستخدام WeasyPrint مع خط beIN-Normal
        pdf_buffer = generate_handover_report_pdf_weasyprint(handover)

        # التحقق من نجاح إنشاء PDF
        if not pdf_buffer:
            current_app.logger.error(f"فشل في إنشاء PDF للتسليم {id}")
            return "خطأ في إنشاء ملف PDF. يرجى المحاولة مرة أخرى.", 500

        # التحقق من حجم PDF
        pdf_buffer.seek(0, 2)  # الانتقال إلى نهاية الملف
        pdf_size = pdf_buffer.tell()
        pdf_buffer.seek(0)  # العودة إلى البداية

        if pdf_size == 0:
            current_app.logger.error(f"PDF فارغ للتسليم {id}")
            return "ملف PDF فارغ. يرجى المحاولة مرة أخرى.", 500

        current_app.logger.info(f"تم إنشاء PDF بحجم {pdf_size} بايت للتسليم {id}")

        # تحضير اسم الملف
        plate_clean = handover.vehicle.plate_number if handover.vehicle else f"record_{handover.id}"
        filename = f"handover_{plate_clean}_{handover.handover_date}.pdf"

        return send_file(
            pdf_buffer,
            download_name=filename,
            as_attachment=False,
            mimetype='application/pdf'
        )

    except Exception as e:
        current_app.logger.error(f"خطأ في إنشاء PDF للتسليم {id}: {e}")
        return "خطأ في إنشاء الملف. يرجى المحاولة مرة أخرى.", 500


# في ملف views الخاص بالمركبات

# @vehicles_bp.route('/handover/<int:id>/pdf/public')
# def handover_pdf_public(id):
#     """إنشاء ملف PDF لنموذج تسليم/استلام - وصول مفتوح بدون تسجيل دخول"""
#     try:
#         # تأكد من أن المسار صحيح لدالة إنشاء التقرير
#         # من utils.weasyprint_handover_pdf أو أي ملف آخر تستخدمه
#         from utils.fpdf_handover_pdf import generate_handover_report_pdf

#         # --- الخطوة 1: جلب كل البيانات اللازمة باستعلام واحد فعال ---

#         # نستخدم joinedload لجلب كل شيء دفعة واحدة وتجنب الاستعلامات المتعددة
#         handover = VehicleHandover.query.options(
#             db.joinedload(VehicleHandover.vehicle), # لجلب معلومات السيارة الحالية (لتسمية الملف)
#             db.joinedload(VehicleHandover.images)  # لجلب الصور المرفقة
#         ).get_or_404(id)

#         # لم نعد بحاجة لجلب الكائنات بشكل منفصل
#         # vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
#         # images = VehicleHandoverImage.query.filter_by(handover_record_id=id).all()

#         # --- الخطوة 2: استدعاء دالة إنشاء التقرير ---

#         # نمرر كائن handover بالكامل، فهو يحتوي على كل شيء الآن.
#         # نمرر vehicle و images أيضاً إذا كانت دالة الرسم تتوقعهم.
#         # النسخة الأنظف هي أن تتوقع الدالة كائن handover فقط.
#         pdf_buffer = generate_handover_report_pdf(handover)

#         # --- الخطوة 3: إعداد وإرسال الملف ---

#         # استخدام البيانات المنسوخة من handover لتسمية الملف لضمان عدم حدوث خطأ
#         # إذا تم حذف السيارة الأصلية.
#         plate_number = handover.vehicle_plate_number or f"record_{handover.id}"
#         filename = f"handover_form_{plate_number}.pdf"

#         return send_file(
#             pdf_buffer,
#             download_name=filename,
#             as_attachment=True,
#             mimetype='application/pdf'
#         )


#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         # في حالة حدوث خطأ، عرض رسالة خطأ بسيطة وواضحة
#         return f"عذراً، حدث خطأ أثناء إنشاء التقرير. يرجى المحاولة لاحقاً.: {str(e)}", 500


# @vehicles_bp.route('/handover/<int:id>/pdf/public')
# def handover_pdf_public(id):
#       """إنشاء ملف PDF لنموذج تسليم/استلام - وصول مفتوح بدون تسجيل دخول"""
#       try:
#               from utils.fpdf_handover_pdf import generate_handover_report_pdf

#               # البحث عن نموذج التسليم/الاستلام
#               handover = VehicleHandover.query.get_or_404(id)
#               vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
#               images = VehicleHandoverImage.query.filter_by(handover_record_id=id).all()

#               # إنشاء ملف PDF باستخدام FPDF
#               pdf_buffer = generate_handover_report_pdf(vehicle, handover,images)

#               # تحديد اسم الملف
#               filename = f"handover_form_{vehicle.plate_number}.pdf"

#               # إرسال الملف للمستخدم
#               return send_file(
#                       pdf_buffer,
#                       download_name=filename,
#                       as_attachment=True,
#                       mimetype='application/pdf'
#               )
#       except Exception as e:
#               # في حالة حدوث خطأ، عرض رسالة خطأ بسيطة
#               return f"خطأ في إنشاء ملف PDF: {str(e)}", 500






# مسارات التقارير والإحصائيات
@vehicles_bp.route('/dashboard')
@login_required
def dashboard():
        """لوحة المعلومات والإحصائيات للسيارات"""
        # إجمالي عدد السيارات
        total_vehicles = Vehicle.query.count()

        # توزيع السيارات حسب الحالة
        status_stats = db.session.query(
                Vehicle.status, func.count(Vehicle.id)
        ).group_by(Vehicle.status).all()

        status_dict = {status: count for status, count in status_stats}

        # حساب قيمة الإيجارات الشهرية
        total_monthly_rent = db.session.query(
                func.sum(VehicleRental.monthly_cost)
        ).filter_by(is_active=True).scalar() or 0

        # السيارات في الورشة حالياً
        vehicles_in_workshop = VehicleWorkshop.query.filter(
                VehicleWorkshop.exit_date.is_(None)
        ).count()

        # تكاليف الصيانة الإجمالية (للسنة الحالية)
        current_year = datetime.now().year
        current_month = datetime.now().month

        yearly_maintenance_cost = db.session.query(
                func.sum(VehicleWorkshop.cost)
        ).filter(
                extract('year', VehicleWorkshop.entry_date) == current_year
        ).scalar() or 0

        # تكاليف الصيانة الشهرية (للأشهر الستة الماضية)
        monthly_costs = []
        for i in range(6):
                month = current_month - i
                year = current_year
                if month <= 0:
                        month += 12
                        year -= 1

                month_cost = db.session.query(
                        func.sum(VehicleWorkshop.cost)
                ).filter(
                        extract('year', VehicleWorkshop.entry_date) == year,
                        extract('month', VehicleWorkshop.entry_date) == month
                ).scalar() or 0

                month_name = [
                        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
                ][month - 1]

                monthly_costs.append({
                        'month': month_name,
                        'cost': month_cost
                })

        # عكس ترتيب القائمة لعرض الأشهر من الأقدم إلى الأحدث
        monthly_costs.reverse()

        # قائمة التنبيهات
        alerts = []

        # تنبيهات السيارات في الورشة لفترة طويلة (أكثر من أسبوعين)
        long_workshop_stays = VehicleWorkshop.query.filter(
                VehicleWorkshop.exit_date.is_(None),
                VehicleWorkshop.entry_date <= (datetime.now().date() - timedelta(days=14))
        ).all()

        for stay in long_workshop_stays:
                days = (datetime.now().date() - stay.entry_date).days
                vehicle = Vehicle.query.get(stay.vehicle_id)
                alerts.append({
                        'type': 'workshop',
                        'message': f'السيارة {vehicle.plate_number} في الورشة منذ {days} يوم',
                        'vehicle_id': vehicle.id,
                        'plate_number': vehicle.plate_number,
                        'make': vehicle.make,
                        'model': vehicle.model
                })

        # تنبيهات الإيجارات التي ستنتهي قريباً (خلال أسبوع)
        ending_rentals = VehicleRental.query.filter(
                VehicleRental.is_active == True,
                VehicleRental.end_date.isnot(None),
                VehicleRental.end_date <= (datetime.now().date() + timedelta(days=7)),
                VehicleRental.end_date >= datetime.now().date()
        ).all()

        for rental in ending_rentals:
                days = (rental.end_date - datetime.now().date()).days
                vehicle = Vehicle.query.get(rental.vehicle_id)
                alerts.append({
                        'type': 'rental',
                        'message': f'إيجار السيارة {vehicle.plate_number} سينتهي خلال {days} يوم',
                        'vehicle_id': vehicle.id,
                        'plate_number': vehicle.plate_number,
                        'make': vehicle.make,
                        'model': vehicle.model
                })

        # استرجاع السيارات ذات الوثائق المنتهية
        today = datetime.now().date()

        # السيارات ذات استمارة منتهية
        expired_registration_vehicles = Vehicle.query.filter(
                Vehicle.registration_expiry_date.isnot(None),
                Vehicle.registration_expiry_date < today
        ).order_by(Vehicle.registration_expiry_date).all()

        # السيارات ذات فحص دوري منتهي
        expired_inspection_vehicles = Vehicle.query.filter(
                Vehicle.inspection_expiry_date.isnot(None),
                Vehicle.inspection_expiry_date < today
        ).order_by(Vehicle.inspection_expiry_date).all()

        # السيارات ذات تفويض منتهي
        expired_authorization_vehicles = Vehicle.query.filter(
                Vehicle.authorization_expiry_date.isnot(None),
                Vehicle.authorization_expiry_date < today
        ).order_by(Vehicle.authorization_expiry_date).all()

        # إعداد بيانات حالة السيارات بالتنسيق المطلوب في القالب
        status_counts = {
                'available': status_dict.get('available', 0),
                'rented': status_dict.get('rented', 0),
                'in_project': status_dict.get('in_project', 0),
                'in_workshop': status_dict.get('in_workshop', 0),
                'accident': status_dict.get('accident', 0)
        }

        # تجميع الإحصائيات في كائن واحد
        stats = {
                'total_vehicles': total_vehicles,
                'status_stats': status_dict,
                'status_counts': status_counts,  # إضافة حالات السيارات بالتنسيق المناسب للقالب
                'total_monthly_rent': total_monthly_rent,
                'total_rental_cost': total_monthly_rent,  # نفس القيمة تستخدم في القالب باسم مختلف
                'vehicles_in_workshop': vehicles_in_workshop,
                'yearly_maintenance_cost': yearly_maintenance_cost,
                'new_vehicles_last_month': Vehicle.query.filter(
                        Vehicle.created_at >= (datetime.now() - timedelta(days=30))
                ).count(),  # عدد السيارات المضافة في الشهر الماضي

                # تكاليف الورشة للشهر الحالي
                'workshop_cost_current_month': db.session.query(
                        func.sum(VehicleWorkshop.cost)
                ).filter(
                        extract('year', VehicleWorkshop.entry_date) == current_year,
                        extract('month', VehicleWorkshop.entry_date) == current_month
                ).scalar() or 0,

                # عدد السيارات في المشاريع
                'vehicles_in_projects': Vehicle.query.filter_by(status='in_project').count(),

                # عدد المشاريع النشطة
                'project_assignments_count': db.session.query(
                        func.count(func.distinct(VehicleProject.project_name))
                ).filter_by(is_active=True).scalar() or 0
        }

        # Datos para el gráfico de costos de alquiler
        rental_cost_data = {
                'labels': [],  # Nombres de meses
                'data_values': []   # Valores de costos - renombrado para evitar conflicto con el método values()
        }

        # Datos para el gráfico de costos de mantenimiento
        maintenance_cost_data = {
                'labels': [],  # Nombres de meses
                'data_values': []   # Valores de costos - renombrado para evitar conflicto con el método values()
        }

        # Obtener datos de los últimos 6 meses para los gráficos
        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(5, -1, -1):
                month_num = (current_month - i) % 12
                if month_num == 0:
                        month_num = 12
                year = current_year - 1 if current_month - i <= 0 else current_year

                month_name = {
                        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 5: 'مايو', 6: 'يونيو',
                        7: 'يوليو', 8: 'أغسطس', 9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
                }[month_num]

                month_label = f"{month_name} {year}"

                # Añadir datos para ambos gráficos
                rental_cost_data['labels'].append(month_label)
                rental_cost_data['data_values'].append(0)  # Valor predeterminado 0, se puede reemplazar con datos reales

                maintenance_cost_data['labels'].append(month_label)
                maintenance_cost_data['data_values'].append(0)  # Valor predeterminado 0, se puede reemplazar con datos reales

        return render_template(
                'vehicles/dashboard.html',
                stats=stats,
                monthly_costs=monthly_costs,
                alerts=alerts,
                rental_cost_data=rental_cost_data,
                maintenance_cost_data=maintenance_cost_data,
                expired_registration_vehicles=expired_registration_vehicles,
                expired_inspection_vehicles=expired_inspection_vehicles,
                expired_authorization_vehicles=expired_authorization_vehicles,
                today=today
        )

@vehicles_bp.route('/reports')
@login_required
def reports():
        """صفحة تقارير السيارات"""
        # توزيع السيارات حسب الشركة المصنعة
        make_stats = db.session.query(
                Vehicle.make, func.count(Vehicle.id)
        ).group_by(Vehicle.make).all()

        # توزيع السيارات حسب سنة الصنع
        year_stats = db.session.query(
                Vehicle.year, func.count(Vehicle.id)
        ).group_by(Vehicle.year).order_by(Vehicle.year).all()

        # إحصائيات الورشة
        workshop_reason_stats = db.session.query(
                VehicleWorkshop.reason, func.count(VehicleWorkshop.id)
        ).group_by(VehicleWorkshop.reason).all()

        # إجمالي تكاليف الصيانة لكل سيارة (أعلى 10 سيارات)
        top_maintenance_costs = db.session.query(
                Vehicle.plate_number, Vehicle.make, Vehicle.model, 
                func.sum(VehicleWorkshop.cost).label('total_cost')
        ).join(
                VehicleWorkshop, Vehicle.id == VehicleWorkshop.vehicle_id
        ).group_by(
                Vehicle.id, Vehicle.plate_number, Vehicle.make, Vehicle.model
        ).order_by(
                func.sum(VehicleWorkshop.cost).desc()
        ).limit(10).all()

        return render_template(
                'vehicles/reports.html',
                make_stats=make_stats,
                year_stats=year_stats,
                workshop_reason_stats=workshop_reason_stats,
                top_maintenance_costs=top_maintenance_costs
        )

@vehicles_bp.route('/detailed')
@login_required
def detailed_list():
        """قائمة تفصيلية للسيارات مع معلومات إضافية لكل سيارة على حدة"""
        # إعداد قيم التصفية
        status = request.args.get('status')
        make = request.args.get('make')
        year = request.args.get('year')
        project = request.args.get('project')
        location = request.args.get('location')
        sort = request.args.get('sort', 'plate_number')
        search = request.args.get('search', '')

        # استعلام قاعدة البيانات مع التصفية
        query = Vehicle.query

        if status:
                query = query.filter(Vehicle.status == status)
        if make:
                query = query.filter(Vehicle.make == make)
        if year:
                query = query.filter(Vehicle.year == int(year))
        if search:
                query = query.filter(
                        or_(
                                Vehicle.plate_number.ilike(f'%{search}%'),
                                Vehicle.make.ilike(f'%{search}%'),
                                Vehicle.model.ilike(f'%{search}%'),
                                Vehicle.color.ilike(f'%{search}%')
                        )
                )

        # فلترة حسب المشروع
        if project:
                vehicle_ids = db.session.query(VehicleProject.vehicle_id).filter_by(
                        project_name=project, is_active=True
                ).all()
                vehicle_ids = [v[0] for v in vehicle_ids]
                query = query.filter(Vehicle.id.in_(vehicle_ids))

        # فلترة حسب الموقع (المنطقة)
        if location:
                vehicle_ids = db.session.query(VehicleProject.vehicle_id).filter_by(
                        location=location, is_active=True
                ).all()
                vehicle_ids = [v[0] for v in vehicle_ids]
                query = query.filter(Vehicle.id.in_(vehicle_ids))

        # ترتيب النتائج
        if sort == 'make':
                query = query.order_by(Vehicle.make, Vehicle.model)
        elif sort == 'year':
                query = query.order_by(Vehicle.year.desc())
        elif sort == 'status':
                query = query.order_by(Vehicle.status)
        elif sort == 'created_at':
                query = query.order_by(Vehicle.created_at.desc())
        else:
                query = query.order_by(Vehicle.plate_number)

        # الترقيم
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(page=page, per_page=20, error_out=False)
        vehicles = pagination.items

        # استخراج معلومات إضافية لكل سيارة
        for vehicle in vehicles:
                # معلومات الإيجار النشط
                vehicle.active_rental = VehicleRental.query.filter_by(
                        vehicle_id=vehicle.id, is_active=True
                ).first()

                # معلومات آخر دخول للورشة
                vehicle.latest_workshop = VehicleWorkshop.query.filter_by(
                        vehicle_id=vehicle.id
                ).order_by(VehicleWorkshop.entry_date.desc()).first()

                # معلومات المشروع الحالي
                vehicle.active_project = VehicleProject.query.filter_by(
                        vehicle_id=vehicle.id, is_active=True
                ).first()

        # استخراج قوائم الفلاتر
        makes = db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()
        makes = [make[0] for make in makes]

        years = db.session.query(Vehicle.year).distinct().order_by(Vehicle.year.desc()).all()
        years = [year[0] for year in years]

        # استخراج قائمة المشاريع النشطة
        projects = db.session.query(VehicleProject.project_name).filter_by(
                is_active=True
        ).distinct().order_by(VehicleProject.project_name).all()
        projects = [project[0] for project in projects]

        # استخراج قائمة المواقع (المناطق)
        locations = db.session.query(VehicleProject.location).distinct().order_by(
                VehicleProject.location
        ).all()
        locations = [location[0] for location in locations]

        return render_template(
                'vehicles/detailed_list.html',
                vehicles=vehicles,
                pagination=pagination,
                makes=makes,
                years=years,
                locations=locations,
                total_count=Vehicle.query.count(),
                request=request
        )

@vehicles_bp.route('/report/export/excel')
@login_required
def export_vehicles_excel():
        """تصدير بيانات السيارات إلى ملف Excel"""
        import io
        import pandas as pd
        from flask import send_file
        import datetime

        status_filter = request.args.get('status', '')
        make_filter = request.args.get('make', '')

        # قاعدة الاستعلام الأساسية
        query = Vehicle.query

        # إضافة التصفية حسب الحالة إذا تم تحديدها
        if status_filter:
                query = query.filter(Vehicle.status == status_filter)

        # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
        if make_filter:
                query = query.filter(Vehicle.make == make_filter)

        # الحصول على قائمة السيارات
        vehicles = query.order_by(Vehicle.status, Vehicle.plate_number).all()

        # تحويل حالة السيارة إلى نص مقروء بالعربية
        status_map = {
                'available': 'متاحة',
                'rented': 'مؤجرة',
                'in_project': 'في المشروع',
                'in_workshop': 'في الورشة',
                'accident': 'حادث'
        }

        # إنشاء قائمة بالبيانات
        vehicle_data = []
        for vehicle in vehicles:
                # حساب تكاليف الصيانة الإجمالية
                total_maintenance_cost = db.session.query(
                        func.sum(VehicleWorkshop.cost)
                ).filter(
                        VehicleWorkshop.vehicle_id == vehicle.id
                ).scalar() or 0

                # الحصول على معلومات الإيجار النشط
                active_rental = VehicleRental.query.filter_by(
                        vehicle_id=vehicle.id, is_active=True
                ).first()

                # الحصول على معلومات المشروع النشط
                active_project = VehicleProject.query.filter_by(
                        vehicle_id=vehicle.id, is_active=True
                ).first()

                vehicle_data.append({
                        'رقم اللوحة': vehicle.plate_number,
                        'الشركة المصنعة': vehicle.make,
                        'الموديل': vehicle.model,
                        'السنة': vehicle.year,
                        'اللون': vehicle.color,
                        'الحالة': status_map.get(vehicle.status, vehicle.status),
                        'تكاليف الصيانة الإجمالية': total_maintenance_cost,
                        'المؤجر': active_rental.lessor_name if active_rental else '',
                        'تكلفة الإيجار الشهرية': active_rental.monthly_cost if active_rental else 0,
                        'المشروع': active_project.project_name if active_project else '',
                        'الموقع': active_project.location if active_project else '',
                        'ملاحظات': vehicle.notes or ''
                })

        # إنشاء DataFrame من البيانات
        df = pd.DataFrame(vehicle_data)

        # إنشاء ملف Excel في الذاكرة
        output = io.BytesIO()

        # استخدام ExcelWriter مع خيارات لتحسين المظهر
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='بيانات السيارات', index=False)

                # الحصول على ورقة العمل وworkbook للتنسيق
                workbook = writer.book
                worksheet = writer.sheets['بيانات السيارات']

                # تنسيق الخلايا
                header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#D7E4BC',
                        'border': 1
                })

                # تنسيق عناوين الأعمدة
                for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        # ضبط عرض العمود
                        worksheet.set_column(col_num, col_num, 15)

        # التحضير لإرسال الملف
        output.seek(0)

        # اسم الملف بالتاريخ الحالي
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = f"تقرير_السيارات_{today}.xlsx"

        # إرسال الملف كمرفق للتنزيل
        return send_file(
                output,
                download_name=filename,
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


# مسار عرض تفاصيل سجل الورشة
@vehicles_bp.route('/workshop-details/<int:workshop_id>')
@login_required
def workshop_details(workshop_id):
        """عرض تفاصيل سجل ورشة في صفحة منفصلة"""
        # الحصول على سجل الورشة
        record = VehicleWorkshop.query.get_or_404(workshop_id)
        vehicle = Vehicle.query.get_or_404(record.vehicle_id)

        # تنسيق التواريخ
        record.formatted_entry_date = format_date_arabic(record.entry_date)
        if record.exit_date:
                record.formatted_exit_date = format_date_arabic(record.exit_date)

        # استرجاع الصور المرتبطة بسجل الورشة
        images = VehicleWorkshopImage.query.filter_by(workshop_record_id=workshop_id).all()
        record.images = images

        # تسجيل الوقت الحالي
        current_date = format_date_arabic(datetime.now().date())

        return render_template(
                'vehicles/workshop_details.html',
                vehicle=vehicle,
                record=record,
                current_date=current_date
        )


# مسارات حذف سجلات الورشة
@vehicles_bp.route('/workshop/confirm-delete/<int:id>')
@login_required
def confirm_delete_workshop(id):
        """تأكيد حذف سجل ورشة"""
        record = VehicleWorkshop.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(record.vehicle_id)

        # تنسيق التواريخ
        record.formatted_entry_date = format_date_arabic(record.entry_date)
        if record.exit_date:
                record.formatted_exit_date = format_date_arabic(record.exit_date)

        return render_template(
                'vehicles/confirm_delete_workshop.html',
                record=record,
                vehicle=vehicle
        )


@vehicles_bp.route('/workshop/delete/<int:id>', methods=['POST'])
@login_required
def delete_workshop(id):
        """حذف سجل ورشة"""
        record = VehicleWorkshop.query.get_or_404(id)
        vehicle_id = record.vehicle_id

        # التحقق من وجود كلمة التأكيد الصحيحة
        confirmation = request.form.get('confirmation', '')
        if confirmation != 'تأكيد':
                flash('كلمة التأكيد غير صحيحة. لم يتم حذف السجل.', 'danger')
                return redirect(url_for('vehicles.confirm_delete_workshop', id=id))

        # تسجيل الإجراء قبل الحذف
        log_audit('delete', 'VehicleWorkshop', id, f'تم حذف سجل الورشة للسيارة رقم {vehicle_id}')

        try:
                # حذف سجل الورشة سيحذف تلقائياً جميع الصور المرتبطة به بفضل cascade='all, delete-orphan'
                db.session.delete(record)
                db.session.commit()
                flash('تم حذف سجل الورشة بنجاح', 'success')
        except Exception as e:
                db.session.rollback()
                flash(f'حدث خطأ أثناء حذف سجل الورشة: {str(e)}', 'danger')

        return redirect(url_for('vehicles.view', id=vehicle_id))


# مسارات التصدير والمشاركة
@vehicles_bp.route('/<int:id>/export/pdf')
@login_required
def export_vehicle_to_pdf(id):
        """تصدير بيانات السيارة إلى ملف PDF"""
        vehicle = Vehicle.query.get_or_404(id)
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
        rental_records = VehicleRental.query.filter_by(vehicle_id=id).order_by(VehicleRental.start_date.desc()).all()

        # إنشاء ملف PDF
        pdf_buffer = export_vehicle_pdf(vehicle, workshop_records, rental_records)

        # تسجيل الإجراء
        log_audit('export', 'vehicle', id, f'تم تصدير بيانات السيارة {vehicle.plate_number} إلى PDF')

        return send_file(
                pdf_buffer,
                download_name=f'vehicle_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.pdf',
                as_attachment=True,
                mimetype='application/pdf'
        )


@vehicles_bp.route('/<int:id>/export/workshop/pdf')
@login_required
def export_workshop_to_pdf(id):
        """تصدير سجلات الورشة للسيارة إلى ملف PDF"""
        try:
                # جلب بيانات المركبة
                vehicle = Vehicle.query.get_or_404(id)

                # جلب سجلات دخول الورشة
                workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(
                        VehicleWorkshop.entry_date.desc()
                ).all()

                # التحقق من وجود سجلات
                if not workshop_records:
                        flash('لا توجد سجلات ورشة لهذه المركبة!', 'warning')
                        return redirect(url_for('vehicles.view', id=id))

                # إنشاء تقرير PDF باستخدام FPDF
                from utils.fpdf_arabic_report import generate_workshop_report_pdf_fpdf
                pdf_buffer = generate_workshop_report_pdf_fpdf(vehicle, workshop_records)

                # اسم الملف
                filename = f"workshop_report_{vehicle.plate_number}_{datetime.now().strftime('%Y%m%d')}.pdf"

                # تسجيل الإجراء
                log_audit('export', 'vehicle_workshop', id, f'تم تصدير سجلات ورشة السيارة {vehicle.plate_number} إلى PDF')

                # إرسال الملف
                return send_file(
                        pdf_buffer,
                        download_name=filename,
                        as_attachment=True,
                        mimetype='application/pdf'
                )
        except Exception as e:
                import logging
                logging.error(f"خطأ في إنشاء تقرير الورشة: {str(e)}")
                flash(f'حدث خطأ أثناء إنشاء التقرير: {str(e)}', 'danger')
                return redirect(url_for('vehicles.view', id=id))


@vehicles_bp.route('/<int:id>/export/excel')
@login_required
def export_vehicle_to_excel(id):
        """تصدير بيانات السيارة إلى ملف Excel"""
        vehicle = Vehicle.query.get_or_404(id)
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
        rental_records = VehicleRental.query.filter_by(vehicle_id=id).order_by(VehicleRental.start_date.desc()).all()

        # إنشاء ملف Excel
        excel_buffer = export_vehicle_excel(vehicle, workshop_records, rental_records)

        # تسجيل الإجراء
        log_audit('export', 'vehicle', id, f'تم تصدير بيانات السيارة {vehicle.plate_number} إلى Excel')

        return send_file(
                excel_buffer,
                download_name=f'vehicle_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.xlsx',
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


@vehicles_bp.route('/<int:id>/export/workshop/excel')
@login_required
def export_workshop_to_excel(id):
        """تصدير سجلات الورشة للسيارة إلى ملف Excel"""
        vehicle = Vehicle.query.get_or_404(id)
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()

        # إنشاء ملف Excel
        excel_buffer = export_workshop_records_excel(vehicle, workshop_records)

        # تسجيل الإجراء
        log_audit('export', 'vehicle_workshop', id, f'تم تصدير سجلات ورشة السيارة {vehicle.plate_number} إلى Excel')

        return send_file(
                excel_buffer,
                download_name=f'vehicle_workshop_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.xlsx',
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


@vehicles_bp.route('/<int:id>/share/workshop')
@login_required
def share_workshop_options(id):
        """خيارات مشاركة سجلات الورشة للسيارة"""
        vehicle = Vehicle.query.get_or_404(id)

        # إنشاء روابط التصدير والمشاركة
        app_url = request.host_url.rstrip('/')
        pdf_url = f"{app_url}{url_for('vehicles.export_workshop_to_pdf', id=id)}"
        excel_url = f"{app_url}{url_for('vehicles.export_workshop_to_excel', id=id)}"

        # إنشاء روابط المشاركة
        whatsapp_text = f"سجلات ورشة السيارة: {vehicle.plate_number} - {vehicle.make} {vehicle.model}"
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)} PDF: {urllib.parse.quote(pdf_url)}"

        email_subject = f"سجلات ورشة السيارة: {vehicle.plate_number}"
        email_body = f"مرفق سجلات ورشة السيارة: {vehicle.plate_number} - {vehicle.make} {vehicle.model}\n\nرابط تحميل PDF: {pdf_url}\n\nرابط تحميل Excel: {excel_url}"
        email_url = f"mailto:?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"

        return render_template(
                'vehicles/share_workshop.html',
                vehicle=vehicle,
                pdf_url=pdf_url,
                excel_url=excel_url,
                whatsapp_url=whatsapp_url,
                email_url=email_url
        )


@vehicles_bp.route('/<int:id>/print/workshop')
@login_required
def print_workshop_records(id):
        """عرض سجلات الورشة للطباعة"""
        vehicle = Vehicle.query.get_or_404(id)
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()

        # تنسيق التواريخ
        for record in workshop_records:
                record.formatted_entry_date = format_date_arabic(record.entry_date)
                if record.exit_date:
                        record.formatted_exit_date = format_date_arabic(record.exit_date)

        # حساب تكلفة الإصلاحات الإجمالية
        total_maintenance_cost = db.session.query(func.sum(VehicleWorkshop.cost)).filter_by(vehicle_id=id).scalar() or 0

        # حساب عدد الأيام في الورشة
        days_in_workshop = 0
        for record in workshop_records:
                if record.exit_date:
                        days_in_workshop += (record.exit_date - record.entry_date).days
                else:
                        days_in_workshop += (datetime.now().date() - record.entry_date).days

        return render_template(
                'vehicles/print_workshop.html',
                vehicle=vehicle,
                workshop_records=workshop_records,
                total_maintenance_cost=total_maintenance_cost,
                days_in_workshop=days_in_workshop,
                current_date=format_date_arabic(datetime.now().date())
        )


# إنشاء تقرير شامل للسيارة (PDF) - محتفظ به ولكن قد لا يعمل بشكل صحيح مع النصوص العربية
@vehicles_bp.route('/vehicle-report-pdf/<int:id>')
@login_required
def generate_vehicle_report_pdf(id):
        """إنشاء تقرير شامل للسيارة بصيغة PDF"""
        from flask import send_file, flash, redirect, url_for, make_response
        import io

        try:
                # الحصول على بيانات المركبة
                vehicle = Vehicle.query.get_or_404(id)

                # الحصول على بيانات الإيجار النشط
                rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()

                # الحصول على سجلات الورشة
                workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(
                        VehicleWorkshop.entry_date.desc()
                ).all()

                # هذا الموديل قد لا يكون موجودًا، لذلك سنتجاهله الآن
                documents = None

                # إنشاء التقرير الشامل
                pdf_bytes = generate_complete_vehicle_report(
                        vehicle, 
                        rental=rental, 
                        workshop_records=workshop_records,
                        documents=documents
                )

                # إرسال الملف للمستخدم
                buffer = io.BytesIO(pdf_bytes)
                response = make_response(send_file(
                        buffer,
                        download_name=f'تقرير_شامل_{vehicle.plate_number}.pdf',
                        mimetype='application/pdf',
                        as_attachment=True
                ))

                # تسجيل الإجراء
                log_audit('generate_report', 'vehicle', id, f'تم إنشاء تقرير شامل للسيارة (PDF): {vehicle.plate_number}')

                return response

        except Exception as e:
                flash(f'حدث خطأ أثناء إنشاء التقرير PDF: {str(e)}', 'danger')
                return redirect(url_for('vehicles.view', id=id))


# مسارات إدارة الفحص الدوري
@vehicles_bp.route('/<int:id>/inspections', methods=['GET'])
@login_required
def vehicle_inspections(id):
        """عرض سجلات الفحص الدوري لسيارة محددة"""
        vehicle = Vehicle.query.get_or_404(id)
        inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=id).order_by(VehiclePeriodicInspection.inspection_date.desc()).all()

        # تنسيق التواريخ
        for inspection in inspections:
                inspection.formatted_inspection_date = format_date_arabic(inspection.inspection_date)
                inspection.formatted_expiry_date = format_date_arabic(inspection.expiry_date)

        return render_template(
                'vehicles/inspections.html',
                vehicle=vehicle,
                inspections=inspections,
                inspection_types=INSPECTION_TYPE_CHOICES,
                inspection_statuses=INSPECTION_STATUS_CHOICES
        )

@vehicles_bp.route('/<int:id>/inspections/create', methods=['GET', 'POST'])
@login_required
def create_inspection(id):
        """إضافة سجل فحص دوري جديد"""
        vehicle = Vehicle.query.get_or_404(id)

        if request.method == 'POST':
                inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
                expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
                inspection_center = request.form.get('inspection_center')
                supervisor_name = request.form.get('supervisor_name')
                result = request.form.get('result')
                inspection_status = 'valid'  # الحالة الافتراضية ساري
                cost = float(request.form.get('cost') or 0)
                results = request.form.get('results')
                recommendations = request.form.get('recommendations')
                notes = request.form.get('notes')

                # حفظ شهادة الفحص إذا تم تحميلها
                certificate_file = None
                if 'certificate_file' in request.files and request.files['certificate_file']:
                        certificate_file = save_image(request.files['certificate_file'], 'inspections')

                # إنشاء سجل فحص جديد
                inspection = VehiclePeriodicInspection(
                        vehicle_id=id,
                        inspection_date=inspection_date,
                        expiry_date=expiry_date,
                        inspection_center=inspection_center,
                        supervisor_name=supervisor_name,
                        result=result,
                        # القيم القديمة للتوافق مع قاعدة البيانات
                        inspection_number=inspection_center,
                        inspector_name=supervisor_name,
                        inspection_type=result,
                        inspection_status=inspection_status,
                        cost=cost,
                        results=results,
                        recommendations=recommendations,
                        certificate_file=certificate_file,
                        notes=notes
                )

                db.session.add(inspection)
                db.session.commit()

                # تسجيل الإجراء
                log_audit('create', 'vehicle_inspection', inspection.id, f'تم إضافة سجل فحص دوري للسيارة: {vehicle.plate_number}')

                flash('تم إضافة سجل الفحص الدوري بنجاح!', 'success')
                return redirect(url_for('vehicles.vehicle_inspections', id=id))

        return render_template(
                'vehicles/inspection_create.html',
                vehicle=vehicle,
                inspection_types=INSPECTION_TYPE_CHOICES
        )

@vehicles_bp.route('/inspection/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inspection(id):
        """تعديل سجل فحص دوري"""
        inspection = VehiclePeriodicInspection.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(inspection.vehicle_id)

        if request.method == 'POST':
                inspection.inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
                inspection.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
                inspection.inspection_center = request.form.get('inspection_center')
                inspection.supervisor_name = request.form.get('supervisor_name')
                inspection.result = request.form.get('result')

                # حفظ القيم القديمة أيضًا للتوافق مع قاعدة البيانات
                inspection.inspection_number = request.form.get('inspection_center')
                inspection.inspector_name = request.form.get('supervisor_name')
                inspection.inspection_type = request.form.get('result')

                inspection.inspection_status = request.form.get('inspection_status')
                inspection.cost = float(request.form.get('cost') or 0)
                inspection.results = request.form.get('results')
                inspection.recommendations = request.form.get('recommendations')
                inspection.notes = request.form.get('notes')
                inspection.updated_at = datetime.utcnow()

                # حفظ شهادة الفحص الجديدة إذا تم تحميلها
                if 'certificate_file' in request.files and request.files['certificate_file']:
                        inspection.certificate_file = save_image(request.files['certificate_file'], 'inspections')

                db.session.commit()

                # تسجيل الإجراء
                log_audit('update', 'vehicle_inspection', inspection.id, f'تم تعديل سجل فحص دوري للسيارة: {vehicle.plate_number}')

                flash('تم تعديل سجل الفحص الدوري بنجاح!', 'success')
                return redirect(url_for('vehicles.vehicle_inspections', id=vehicle.id))

        return render_template(
                'vehicles/inspection_edit.html',
                inspection=inspection,
                vehicle=vehicle,
                inspection_types=INSPECTION_TYPE_CHOICES,
                inspection_statuses=INSPECTION_STATUS_CHOICES
        )

@vehicles_bp.route('/inspection/<int:id>/confirm-delete')
@login_required
def confirm_delete_inspection(id):
        """عرض صفحة تأكيد حذف سجل فحص دوري"""
        inspection = VehiclePeriodicInspection.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(inspection.vehicle_id)

        # تنسيق التاريخ
        inspection.formatted_inspection_date = format_date_arabic(inspection.inspection_date)

        return render_template(
                'vehicles/confirm_delete_inspection.html',
                inspection=inspection,
                vehicle=vehicle
        )

@vehicles_bp.route('/inspection/<int:id>/delete', methods=['POST'])
@login_required
def delete_inspection(id):
        """حذف سجل فحص دوري"""
        inspection = VehiclePeriodicInspection.query.get_or_404(id)
        vehicle_id = inspection.vehicle_id
        vehicle = Vehicle.query.get_or_404(vehicle_id)

        # تسجيل الإجراء قبل الحذف
        log_audit('delete', 'vehicle_inspection', id, f'تم حذف سجل فحص دوري للسيارة: {vehicle.plate_number}')

        db.session.delete(inspection)
        db.session.commit()

        flash('تم حذف سجل الفحص الدوري بنجاح!', 'success')
        return redirect(url_for('vehicles.vehicle_inspections', id=vehicle_id))

# مسارات إدارة فحص السلامة
@vehicles_bp.route('/<int:id>/safety-checks', methods=['GET'])
@login_required
def vehicle_safety_checks(id):
        """عرض سجلات فحص السلامة لسيارة محددة"""
        vehicle = Vehicle.query.get_or_404(id)
        checks = VehicleSafetyCheck.query.filter_by(vehicle_id=id).order_by(VehicleSafetyCheck.check_date.desc()).all()

        # تنسيق التواريخ
        for check in checks:
                check.formatted_check_date = format_date_arabic(check.check_date)

        return render_template(
                'vehicles/safety_checks.html',
                vehicle=vehicle,
                checks=checks,
                check_types=SAFETY_CHECK_TYPE_CHOICES,
                check_statuses=SAFETY_CHECK_STATUS_CHOICES
        )

@vehicles_bp.route('/<int:id>/safety-checks/create', methods=['GET', 'POST'])
@login_required
def create_safety_check(id):
        """إضافة سجل فحص سلامة جديد"""
        vehicle = Vehicle.query.get_or_404(id)

        # الحصول على قائمة السائقين والمشرفين
        supervisors = Employee.query.filter(Employee.job_title.contains('مشرف')).all()

        if request.method == 'POST':
                check_date = datetime.strptime(request.form.get('check_date'), '%Y-%m-%d').date()
                check_type = request.form.get('check_type')

                # معلومات السائق
                driver_id = request.form.get('driver_id')
                driver_name = request.form.get('driver_name')
                # تحويل قيمة فارغة إلى None
                if not driver_id or driver_id == '':
                        driver_id = None
                else:
                        driver = Employee.query.get(driver_id)
                        if driver:
                                driver_name = driver.name

                # معلومات المشرف
                supervisor_id = request.form.get('supervisor_id')
                supervisor_name = request.form.get('supervisor_name')
                # تحويل قيمة فارغة إلى None
                if not supervisor_id or supervisor_id == '':
                        supervisor_id = None
                else:
                        supervisor = Employee.query.get(supervisor_id)
                        if supervisor:
                                supervisor_name = supervisor.name

                status = request.form.get('status')
                check_form_link = request.form.get('check_form_link')
                issues_found = bool(request.form.get('issues_found'))
                issues_description = request.form.get('issues_description')
                actions_taken = request.form.get('actions_taken')
                notes = request.form.get('notes')

                # إنشاء سجل فحص سلامة جديد
                safety_check = VehicleSafetyCheck(
                        vehicle_id=id,
                        check_date=check_date,
                        check_type=check_type,
                        driver_id=driver_id,
                        driver_name=driver_name,
                        supervisor_id=supervisor_id,
                        supervisor_name=supervisor_name,
                        status=status,
                        check_form_link=check_form_link,
                        issues_found=issues_found,
                        issues_description=issues_description,
                        actions_taken=actions_taken,
                        notes=notes
                )

                db.session.add(safety_check)
                db.session.commit()

                # تسجيل الإجراء
                log_audit('create', 'vehicle_safety_check', safety_check.id, f'تم إضافة سجل فحص سلامة للسيارة: {vehicle.plate_number}')

                flash('تم إضافة سجل فحص السلامة بنجاح!', 'success')
                return redirect(url_for('vehicles.vehicle_safety_checks', id=id))

        return render_template(
                'vehicles/safety_check_create.html',
                vehicle=vehicle,
                supervisors=supervisors,
                check_types=SAFETY_CHECK_TYPE_CHOICES,
                check_statuses=SAFETY_CHECK_STATUS_CHOICES
        )

@vehicles_bp.route('/safety-check/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_safety_check(id):
        """تعديل سجل فحص سلامة"""
        safety_check = VehicleSafetyCheck.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(safety_check.vehicle_id)

        # الحصول على قائمة السائقين والمشرفين
        supervisors = Employee.query.filter(Employee.job_title.contains('مشرف')).all()

        if request.method == 'POST':
                safety_check.check_date = datetime.strptime(request.form.get('check_date'), '%Y-%m-%d').date()
                safety_check.check_type = request.form.get('check_type')

                # معلومات السائق
                driver_id = request.form.get('driver_id')
                safety_check.driver_name = request.form.get('driver_name')

                # تحويل قيمة فارغة إلى None
                if not driver_id or driver_id == '':
                        safety_check.driver_id = None
                else:
                        safety_check.driver_id = driver_id
                        driver = Employee.query.get(driver_id)
                        if driver:
                                safety_check.driver_name = driver.name

                # معلومات المشرف
                supervisor_id = request.form.get('supervisor_id')
                safety_check.supervisor_name = request.form.get('supervisor_name')

                # تحويل قيمة فارغة إلى None
                if not supervisor_id or supervisor_id == '':
                        safety_check.supervisor_id = None
                else:
                        safety_check.supervisor_id = supervisor_id
                        supervisor = Employee.query.get(supervisor_id)
                        if supervisor:
                                safety_check.supervisor_name = supervisor.name

                safety_check.status = request.form.get('status')
                safety_check.check_form_link = request.form.get('check_form_link')
                safety_check.issues_found = bool(request.form.get('issues_found'))
                safety_check.issues_description = request.form.get('issues_description')
                safety_check.actions_taken = request.form.get('actions_taken')
                safety_check.notes = request.form.get('notes')
                safety_check.updated_at = datetime.utcnow()

                db.session.commit()

                # تسجيل الإجراء
                log_audit('update', 'vehicle_safety_check', safety_check.id, f'تم تعديل سجل فحص سلامة للسيارة: {vehicle.plate_number}')

                flash('تم تعديل سجل فحص السلامة بنجاح!', 'success')
                return redirect(url_for('vehicles.vehicle_safety_checks', id=vehicle.id))

        return render_template(
                'vehicles/safety_check_edit.html',
                safety_check=safety_check,
                vehicle=vehicle,
                supervisors=supervisors,
                check_types=SAFETY_CHECK_TYPE_CHOICES,
                check_statuses=SAFETY_CHECK_STATUS_CHOICES
        )

@vehicles_bp.route('/safety-check/<int:id>/confirm-delete')
@login_required
def confirm_delete_safety_check(id):
        """عرض صفحة تأكيد حذف سجل فحص سلامة"""
        safety_check = VehicleSafetyCheck.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(safety_check.vehicle_id)

        # تنسيق التاريخ
        safety_check.formatted_check_date = format_date_arabic(safety_check.check_date)

        return render_template(
                'vehicles/confirm_delete_safety_check.html',
                check=safety_check,
                vehicle=vehicle
        )

@vehicles_bp.route('/safety-check/<int:id>/delete', methods=['POST'])
@login_required
def delete_safety_check(id):
        """حذف سجل فحص سلامة"""
        safety_check = VehicleSafetyCheck.query.get_or_404(id)
        vehicle_id = safety_check.vehicle_id
        vehicle = Vehicle.query.get_or_404(vehicle_id)

        # تسجيل الإجراء قبل الحذف
        log_audit('delete', 'vehicle_safety_check', id, f'تم حذف سجل فحص سلامة للسيارة: {vehicle.plate_number}')

        db.session.delete(safety_check)
        db.session.commit()

        flash('تم حذف سجل فحص السلامة بنجاح!', 'success')
        return redirect(url_for('vehicles.vehicle_safety_checks', id=vehicle_id))

# إنشاء تقرير Excel شامل للسيارة
@vehicles_bp.route('/<int:vehicle_id>/external-authorization/create', methods=['GET', 'POST'])
@login_required
def create_external_authorization(vehicle_id):
    """إنشاء تفويض خارجي جديد"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # فحص قيود العمليات للسيارات خارج الخدمة
    restrictions = check_vehicle_operation_restrictions(vehicle)
    if restrictions['blocked']:
        flash(restrictions['message'], 'error')
        return redirect(url_for('vehicles.view', id=vehicle_id))

    if request.method == 'POST':
        try:
            # إنشاء التفويض الجديد
            external_auth = ExternalAuthorization(
                vehicle_id=vehicle_id,
                employee_id=request.form.get('employee_id'),
                project_name=request.form.get('project_name'),
                authorization_type=request.form.get('authorization_type'),
                status='pending',
                external_link=request.form.get('form_link'),
                notes=request.form.get('notes'),
                city=request.form.get('city')
            )

            # معالجة رفع الملف
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # إنشاء مجلد للتفويضات إذا لم يكن موجوداً
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'authorizations')
                    os.makedirs(upload_dir, exist_ok=True)

                    # حفظ الملف
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    external_auth.file_path = filename

            db.session.add(external_auth)
            db.session.commit()

            flash('تم إنشاء التفويض الخارجي بنجاح', 'success')
            return redirect(url_for('vehicles.view', id=vehicle_id))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء التفويض: {str(e)}', 'error')

    # الحصول على البيانات للنموذج
    departments = Department.query.all()
    employees = Employee.query.all()

    return render_template('vehicles/create_external_authorization.html',
                         vehicle=vehicle,
                         departments=departments,
                         employees=employees)

@vehicles_bp.route('/<int:vehicle_id>/external-authorization/<int:auth_id>/view')
@login_required
def view_external_authorization(vehicle_id, auth_id):
    """عرض تفاصيل التفويض الخارجي"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    auth = ExternalAuthorization.query.get_or_404(auth_id)

    return render_template('vehicles/view_external_authorization.html',
                         vehicle=vehicle,
                         authorization=auth)

@vehicles_bp.route('/<int:vehicle_id>/external-authorization/<int:auth_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_external_authorization(vehicle_id, auth_id):
    """تعديل التفويض الخارجي"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    auth = ExternalAuthorization.query.get_or_404(auth_id)

    if request.method == 'POST':
        try:
            # تحديث البيانات
            auth.employee_id = request.form.get('employee_id')
            auth.project_name = request.form.get('project_name')
            auth.authorization_type = request.form.get('authorization_type')
            auth.city = request.form.get('city')
            auth.external_link = request.form.get('form_link')
            auth.notes = request.form.get('notes')

            # معالجة رفع الملف الجديد
            if 'file' in request.files and request.files['file'].filename:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"

                    # إنشاء مجلد الرفع إذا لم يكن موجوداً
                    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'authorizations')
                    os.makedirs(upload_dir, exist_ok=True)

                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)

                    # حذف الملف القديم إذا كان موجوداً
                    if auth.file_path:
                        old_file_path = os.path.join(current_app.static_folder, 'uploads', 'authorizations', auth.file_path.split('/')[-1])
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)

                    auth.file_path = f"uploads/authorizations/{filename}"

            db.session.commit()
            flash('تم تحديث التفويض بنجاح', 'success')
            return redirect(url_for('vehicles.view', id=vehicle_id))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث التفويض: {str(e)}', 'error')

    # الحصول على البيانات للنموذج
    departments = Department.query.all()
    employees = Employee.query.all()

    return render_template('vehicles/edit_external_authorization.html',
                         vehicle=vehicle,
                         authorization=auth,
                         departments=departments,
                         employees=employees)

@vehicles_bp.route('/<int:vehicle_id>/external-authorization/<int:auth_id>/approve')
@login_required
def approve_external_authorization(vehicle_id, auth_id):
    """الموافقة على التفويض الخارجي"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    auth = ExternalAuthorization.query.get_or_404(auth_id)

    try:
        auth.status = 'approved'
        db.session.commit()
        flash('تم الموافقة على التفويض بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء الموافقة على التفويض: {str(e)}', 'error')

    return redirect(url_for('vehicles.view', id=vehicle_id))

@vehicles_bp.route('/<int:vehicle_id>/external-authorization/<int:auth_id>/reject')
@login_required
def reject_external_authorization(vehicle_id, auth_id):
    """رفض التفويض الخارجي"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    auth = ExternalAuthorization.query.get_or_404(auth_id)

    try:
        auth.status = 'rejected'
        db.session.commit()
        flash('تم رفض التفويض', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء رفض التفويض: {str(e)}', 'error')

    return redirect(url_for('vehicles.view', id=vehicle_id))

@vehicles_bp.route('/<int:vehicle_id>/external-authorization/<int:auth_id>/delete')
@login_required
def delete_external_authorization(vehicle_id, auth_id):
    """حذف التفويض الخارجي"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    auth = ExternalAuthorization.query.get_or_404(auth_id)

    try:
        # حذف الملف المرفق إذا كان موجوداً
        if auth.file_path:
            file_path = os.path.join(current_app.static_folder, 'uploads', 'authorizations', auth.file_path.split('/')[-1])
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(auth)
        db.session.commit()
        flash('تم حذف التفويض بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف التفويض: {str(e)}', 'error')

    return redirect(url_for('vehicles.view', id=vehicle_id))

@vehicles_bp.route('/vehicle-report/<int:id>')
@login_required
def generate_vehicle_report(id):
        """إنشاء تقرير شامل للسيارة بصيغة Excel"""
        from flask import send_file, flash, redirect, url_for, make_response
        import io

        try:
                # الحصول على بيانات المركبة
                vehicle = Vehicle.query.get_or_404(id)

                # الحصول على بيانات الإيجار النشط
                rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()

                # الحصول على سجلات الورشة
                workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(
                        VehicleWorkshop.entry_date.desc()
                ).all()

                # الحصول على سجلات التسليم/الاستلام
                handovers = VehicleHandover.query.filter_by(vehicle_id=id).order_by(
                        VehicleHandover.handover_date.desc()
                ).all()

                # الحصول على سجلات الفحص
                inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=id).order_by(
                        VehiclePeriodicInspection.inspection_date.desc()
                ).all()

                # هذا الموديل قد لا يكون موجودًا، لذلك سنتجاهله الآن
                documents = None

                # إنشاء التقرير الشامل
                excel_bytes = generate_complete_vehicle_excel_report(
                        vehicle, 
                        rental=rental, 
                        workshop_records=workshop_records,
                        documents=documents,
                        handovers=handovers,
                        inspections=inspections
                )

                # إرسال الملف للمستخدم
                buffer = io.BytesIO(excel_bytes)
                buffer.seek(0)  # إعادة تعيين موضع القراءة إلى بداية البيانات
                response = make_response(send_file(
                        buffer,
                        download_name=f'تقرير_شامل_{vehicle.plate_number}.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True
                ))

                # تسجيل الإجراء
                log_audit('generate_report', 'vehicle', id, f'تم إنشاء تقرير شامل للسيارة (Excel): {vehicle.plate_number}')

                return response

        except Exception as e:
                flash(f'حدث خطأ أثناء إنشاء تقرير Excel: {str(e)}', 'danger')
                return redirect(url_for('vehicles.view', id=id))

@vehicles_bp.route('/update-drivers', methods=['POST'])
@login_required
def update_drivers():
        """تحديث جميع أسماء السائقين من سجلات التسليم"""
        try:
                updated_count = update_all_vehicle_drivers()
                flash(f'تم تحديث أسماء السائقين لـ {updated_count} سيارة بنجاح!', 'success')
        except Exception as e:
                flash(f'حدث خطأ أثناء التحديث: {str(e)}', 'danger')

        return redirect(url_for('vehicles.detailed'))

@vehicles_bp.route('/<int:vehicle_id>/current_employee')
@login_required
def get_current_employee(vehicle_id):
        """الحصول على معرف الموظف الحالي للسيارة"""
        try:
                employee_id = get_vehicle_current_employee_id(vehicle_id)
                return jsonify({
                        'employee_id': employee_id
                })
        except Exception as e:
                return jsonify({
                        'employee_id': None,
                        'error': str(e)
                }), 500

@vehicles_bp.route('/handovers')
@login_required
def handovers_list():
        """عرض جميع السيارات مع حالات التسليم والاستلام"""
        try:
                # الحصول على جميع السيارات مع معلومات التسليم
                vehicles = Vehicle.query.all()

                vehicles_data = []
                for vehicle in vehicles:
                        # الحصول على آخر سجل تسليم وآخر سجل استلام
                        latest_delivery = VehicleHandover.query.filter_by(
                                vehicle_id=vehicle.id, 
                                handover_type='delivery'
                        ).order_by(VehicleHandover.handover_date.desc()).first()

                        latest_return = VehicleHandover.query.filter_by(
                                vehicle_id=vehicle.id, 
                                handover_type='return'
                        ).order_by(VehicleHandover.handover_date.desc()).first()

                        # تحديد الحالة الحالية
                        current_status = 'متاح'
                        current_employee = None

                        if latest_delivery:
                                if not latest_return or latest_delivery.handover_date > latest_return.handover_date:
                                        current_status = 'مُسلم'
                                        current_employee = latest_delivery.person_name

                        vehicles_data.append({
                                'vehicle': vehicle,
                                'latest_delivery': latest_delivery,
                                'latest_return': latest_return,
                                'current_status': current_status,
                                'current_employee': current_employee
                        })

                return render_template('vehicles/handovers_list.html', vehicles_data=vehicles_data)

        except Exception as e:
                flash(f'حدث خطأ أثناء تحميل البيانات: {str(e)}', 'danger')
                return redirect(url_for('vehicles.index'))

@vehicles_bp.route('/handover/<int:handover_id>/form')
@login_required
def view_handover_form(handover_id):
        """عرض النموذج الإلكتروني لسجل التسليم/الاستلام"""
        try:
                handover = VehicleHandover.query.get_or_404(handover_id)
                vehicle = Vehicle.query.get_or_404(handover.vehicle_id)

                return render_template('vehicles/handover_form_view.html', 
                                                         handover=handover, 
                                                         vehicle=vehicle)

        except Exception as e:
                flash(f'حدث خطأ أثناء عرض النموذج: {str(e)}', 'danger')
                return redirect(url_for('vehicles.handovers_list'))

@vehicles_bp.route('/handover/<int:handover_id>/update_link', methods=['GET', 'POST'])
@login_required
def update_handover_link(handover_id):
        """تحديث الرابط الخارجي لنموذج التسليم/الاستلام"""
        handover = VehicleHandover.query.get_or_404(handover_id)
        vehicle = Vehicle.query.get_or_404(handover.vehicle_id)

        if request.method == 'POST':
                form_link = request.form.get('form_link', '').strip()
                handover.form_link = form_link if form_link else None

                try:
                        db.session.commit()
                        flash(f'تم تحديث الرابط الخارجي بنجاح', 'success')
                        log_audit(
                                action='تحديث رابط نموذج خارجي',
                                entity_type='VehicleHandover',
                                entity_id=handover.id,
                                details=f'تحديث الرابط الخارجي لنموذج {handover.handover_type} السيارة {vehicle.plate_number}'
                        )
                except Exception as e:
                        db.session.rollback()
                        flash(f'خطأ في تحديث الرابط: {str(e)}', 'error')

                return redirect(url_for('vehicles.view_handover', id=handover_id))

        return render_template('vehicles/update_handover_link.html', 
                                                 handover=handover, 
                                                 vehicle=vehicle)

# ========== مسارات إدارة صور رخص السيارات ==========

@vehicles_bp.route('/<int:vehicle_id>/license-image', methods=['GET', 'POST'])
@login_required
def vehicle_license_image(vehicle_id):
    """عرض وإدارة صورة رخصة السيارة"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        # طباعة معلومات debug لفهم المشكلة
        print(f"POST request received for vehicle {vehicle_id}")
        print(f"Form data: {request.form}")
        print(f"Files in request: {list(request.files.keys())}")

        # التحقق من نوع العملية
        action = request.form.get('action')

        if action == 'delete':
            # حذف صورة الرخصة
            if vehicle.license_image:
                try:
                    # حذف الملف من النظام
                    file_path = os.path.join('static', 'uploads', 'vehicles', vehicle.license_image)
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    # حذف المرجع من قاعدة البيانات
                    vehicle.license_image = None
                    db.session.commit()

                    # تسجيل العملية
                    log_audit(
                        action='delete',
                        entity_type='vehicle',
                        entity_id=vehicle.id,
                        details=f'تم حذف صورة رخصة السيارة {vehicle.plate_number}'
                    )

                    flash('تم حذف صورة الرخصة بنجاح', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'خطأ في حذف صورة الرخصة: {str(e)}', 'error')
            else:
                flash('لا توجد صورة رخصة لحذفها', 'warning')

            return redirect(url_for('vehicles.vehicle_license_image', vehicle_id=vehicle_id))

        # رفع صورة جديدة
        if 'license_image' not in request.files:
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(url_for('vehicles.vehicle_license_image', vehicle_id=vehicle_id))

        file = request.files['license_image']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(url_for('vehicles.vehicle_license_image', vehicle_id=vehicle_id))

        

        if file and allowed_file(file.filename, ['png', 'jpg', 'jpeg', 'gif', 'webp']):

            try:
                # إنشاء مجلد الرفع إذا لم يكن موجوداً
                upload_dir = os.path.join('static', 'uploads', 'vehicles')
                os.makedirs(upload_dir, exist_ok=True)

                # حذف الصورة القديمة إذا كانت موجودة
                if vehicle.license_image:
                    old_file_path = os.path.join(upload_dir, vehicle.license_image)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                # تأمين اسم الملف وإضافة timestamp لتجنب التضارب
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"license_{vehicle.plate_number}_{timestamp}_{filename}"
                filepath = os.path.join(upload_dir, filename)

                # حفظ الملف
                file.save(filepath)

                # ضغط الصورة إذا كانت كبيرة
                try:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        # تحويل إلى RGB إذا كانت الصورة RGBA
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')

                        # تصغير الصورة إذا كانت أكبر من 1500x1500
                        if img.width > 1500 or img.height > 1500:
                            img.thumbnail((1500, 1500), Image.Resampling.LANCZOS)
                            img.save(filepath, 'JPEG', quality=85, optimize=True)
                except Exception as e:
                    print(f"خطأ في معالجة الصورة: {e}")

                # تحديث قاعدة البيانات
                vehicle.license_image = filename
                db.session.commit()

                # تسجيل العملية
                action_text = 'update' if vehicle.license_image else 'create'
                log_audit(
                    action=action_text,
                    entity_type='vehicle',
                    entity_id=vehicle.id,
                    details=f'تم {"تحديث" if action_text == "update" else "رفع"} صورة رخصة للسيارة {vehicle.plate_number}'
                )

                flash('تم رفع صورة الرخصة بنجاح', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'خطأ في رفع صورة الرخصة: {str(e)}', 'error')
        else:
            flash('نوع الملف غير مدعوم. يرجى رفع صورة بصيغة JPG, PNG, GIF أو WEBP', 'error')

        return redirect(url_for('vehicles.vehicle_license_image', vehicle_id=vehicle_id))

    return render_template('vehicles/license_image.html', vehicle=vehicle)



def allowed_file(filename, allowed_extensions):
    """التحقق من أن امتداد الملف مسموح"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# ========== مسارات إدارة Google Drive ==========

@vehicles_bp.route('/<int:vehicle_id>/drive-link', methods=['POST'])
@login_required
def update_drive_link(vehicle_id):
    """تحديث أو حذف رابط Google Drive"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    action = request.form.get('action')

    if action == 'remove':
        # حذف الرابط
        vehicle.drive_folder_link = None
        db.session.commit()

        log_audit('delete', 'vehicle', vehicle.id, f'تم حذف رابط Google Drive للسيارة {vehicle.plate_number}')
        flash('تم حذف رابط Google Drive بنجاح', 'success')

    else:
        # حفظ أو تحديث الرابط
        drive_link = request.form.get('drive_link', '').strip()

        if not drive_link:
            flash('يرجى إدخال رابط Google Drive', 'danger')
            return redirect(url_for('vehicles.view', id=vehicle_id))

        # التحقق من صحة الرابط
        if not (drive_link.startswith('https://drive.google.com') or drive_link.startswith('https://docs.google.com')):
            flash('يرجى إدخال رابط Google Drive صحيح', 'danger')
            return redirect(url_for('vehicles.view', id=vehicle_id))

        # حفظ الرابط
        old_link = vehicle.drive_folder_link
        vehicle.drive_folder_link = drive_link
        db.session.commit()

        # تسجيل العملية
        if old_link:
            log_audit('update', 'vehicle', vehicle.id, f'تم تحديث رابط Google Drive للسيارة {vehicle.plate_number}')
            flash('تم تحديث رابط Google Drive بنجاح', 'success')
        else:
            log_audit('create', 'vehicle', vehicle.id, f'تم إضافة رابط Google Drive للسيارة {vehicle.plate_number}')
            flash('تم إضافة رابط Google Drive بنجاح', 'success')

    return redirect(url_for('vehicles.view', id=vehicle_id))

@vehicles_bp.route('/<int:vehicle_id>/drive-files')
@login_required
def vehicle_drive_files(vehicle_id):
    """صفحة منفصلة لإدارة ملفات Google Drive"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template('vehicles/drive_files.html', 
                         title=f'ملفات Google Drive - {vehicle.plate_number}',
                         vehicle=vehicle)

@vehicles_bp.route('/<int:vehicle_id>/drive-management', methods=['GET', 'POST'])
@vehicles_bp.route('/<int:vehicle_id>/drive-management', methods=['GET', 'POST'])
@login_required
def drive_management(vehicle_id):
    """صفحة منفصلة لإدخال وإدارة بيانات Google Drive"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete':
            # حذف الرابط
            old_link = vehicle.drive_folder_link
            vehicle.drive_folder_link = None
            db.session.commit()

            # تسجيل العملية
            log_audit('delete', 'vehicle', vehicle.id, f'تم حذف رابط Google Drive للسيارة {vehicle.plate_number}')
            flash('تم حذف رابط Google Drive بنجاح', 'success')

        elif action == 'save':
            # حفظ أو تحديث الرابط
            drive_link = request.form.get('drive_link', '').strip()

            if not drive_link:
                flash('يرجى إدخال رابط Google Drive', 'danger')
                return render_template('vehicles/drive_management.html', vehicle=vehicle)

            # التحقق من صحة الرابط
            if not (drive_link.startswith('https://drive.google.com') or drive_link.startswith('https://docs.google.com')):
                flash('يرجى إدخال رابط Google Drive صحيح', 'danger')
                return render_template('vehicles/drive_management.html', vehicle=vehicle)

            # حفظ الرابط
            old_link = vehicle.drive_folder_link
            vehicle.drive_folder_link = drive_link
            db.session.commit()

            # تسجيل العملية
            if old_link:
                log_audit('update', 'vehicle', vehicle.id, f'تم تحديث رابط Google Drive للسيارة {vehicle.plate_number}')
                flash('تم تحديث رابط Google Drive بنجاح', 'success')
            else:
                log_audit('create', 'vehicle', vehicle.id, f'تم إضافة رابط Google Drive للسيارة {vehicle.plate_number}')
                flash('تم إضافة رابط Google Drive بنجاح', 'success')

        return redirect(url_for('vehicles.drive_management', vehicle_id=vehicle_id))

    return render_template('vehicles/drive_management.html', vehicle=vehicle)


@vehicles_bp.route('/<int:id>/upload-document', methods=['POST'])
@login_required
def upload_document(id):
    """رفع الوثائق (استمارة، لوحة، تأمين)"""
    vehicle = Vehicle.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    try:
        if not current_user.has_permission(Module.VEHICLES, Permission.EDIT):
            flash('ليس لديك صلاحية لتعديل بيانات السيارات', 'error')
            return redirect(url_for('vehicles.view', id=id))
    except:
        # في حالة عدم وجود صلاحيات، السماح للمديرين أو تخطي للتجربة
        if not hasattr(current_user, 'role') or current_user.role != UserRole.ADMIN:
            flash('ليس لديك صلاحية لتعديل بيانات السيارات', 'error')
            return redirect(url_for('vehicles.view', id=id))

    document_type = request.form.get('document_type')
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'error')
        return redirect(url_for('vehicles.view', id=id))

    file = request.files['file']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'error')
        return redirect(url_for('vehicles.view', id=id))

    if file and allowed_file(file.filename):
        # إنشاء اسم ملف فريد
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # إنشاء المسار المناسب حسب نوع الوثيقة
        if document_type == 'registration_form':
            upload_folder = 'static/uploads/vehicles/registration_forms'
            field_name = 'registration_form_image'
        elif document_type == 'plate':
            upload_folder = 'static/uploads/vehicles/plates'
            field_name = 'plate_image'
        elif document_type == 'insurance':
            upload_folder = 'static/uploads/vehicles/insurance'
            field_name = 'insurance_file'
        else:
            flash('نوع الوثيقة غير صحيح', 'error')
            return redirect(url_for('vehicles.view', id=id))

        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(upload_folder, exist_ok=True)

        # حفظ الملف
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # تحديث قاعدة البيانات
        setattr(vehicle, field_name, file_path)

        try:
            db.session.commit()
            flash('تم رفع الوثيقة بنجاح', 'success')

            # تسجيل النشاط
            log_activity(
                action='upload',
                entity_type='Vehicle',
                entity_id=vehicle.id,
                details=f'رفع وثيقة {document_type} للسيارة {vehicle.plate_number}'
            )

        except Exception as e:
            db.session.rollback()
            # حذف الملف إذا فشل الحفظ في قاعدة البيانات
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'خطأ في حفظ الوثيقة: {str(e)}', 'error')

    return redirect(url_for('vehicles.view', id=id))


@vehicles_bp.route('/<int:id>/delete-document', methods=['POST'])
@login_required
def delete_document(id):
    """حذف الوثائق"""
    vehicle = Vehicle.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    try:
        if not current_user.has_permission(Module.VEHICLES, Permission.DELETE):
            flash('ليس لديك صلاحية لحذف بيانات السيارات', 'error')
            return redirect(url_for('vehicles.view', id=id))
    except:
        # في حالة عدم وجود صلاحيات، السماح للمديرين أو تخطي للتجربة
        if not hasattr(current_user, 'role') or current_user.role != UserRole.ADMIN:
            flash('ليس لديك صلاحية لحذف بيانات السيارات', 'error')
            return redirect(url_for('vehicles.view', id=id))

    document_type = request.form.get('document_type')

    if document_type == 'registration_form':
        field_name = 'registration_form_image'
    elif document_type == 'plate':
        field_name = 'plate_image'
    elif document_type == 'insurance':
        field_name = 'insurance_file'
    else:
        flash('نوع الوثيقة غير صحيح', 'error')
        return redirect(url_for('vehicles.view', id=id))

    # الحصول على مسار الملف
    file_path = getattr(vehicle, field_name)

    if file_path:
        # حذف الملف من النظام
        if os.path.exists(file_path):
            os.remove(file_path)

        # حذف المرجع من قاعدة البيانات
        setattr(vehicle, field_name, None)

        try:
            db.session.commit()
            flash('تم حذف الوثيقة بنجاح', 'success')

            # تسجيل النشاط
            log_activity(
                action='delete',
                entity_type='Vehicle',
                entity_id=vehicle.id,
                details=f'حذف وثيقة {document_type} للسيارة {vehicle.plate_number}'
            )

        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في حذف الوثيقة: {str(e)}', 'error')

    return redirect(url_for('vehicles.view', id=id))


def allowed_file(filename):
    """التحقق من أنواع الملفات المسموحة"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_vehicle_operational(vehicle):
    """فحص إذا كانت السيارة قابلة للتشغيل أم خارج الخدمة"""
    return vehicle.status != 'out_of_service'

def check_vehicle_operation_restrictions(vehicle):
    """فحص قيود التشغيل وإرجاع رسالة تحذير إذا كانت السيارة خارج الخدمة"""
    if not is_vehicle_operational(vehicle):
        return {
            'blocked': True,
            'message': f'❌ عذراً، السيارة "{vehicle.plate_number}" خارج الخدمة ولا يمكن تنفيذ أي عمليات عليها حالياً. يرجى تغيير حالة السيارة أولاً.',
            'status': 'out_of_service'
        }
    return {'blocked': False}

