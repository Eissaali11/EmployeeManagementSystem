from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, send_file
from werkzeug.utils import secure_filename
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import io
from io import BytesIO
import csv
import xlsxwriter
from flask_login import current_user
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import arabic_reshaper
from bidi.algorithm import get_display
from app import db
from models import Document, Employee, Department, SystemAudit
from utils.excel import parse_document_excel
from utils.date_converter import parse_date, format_date_hijri, format_date_gregorian

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/')
def index():
    """List document records with filtering options"""
    # Get filter parameters
    document_type = request.args.get('document_type', '')
    employee_id = request.args.get('employee_id', '')
    department_id = request.args.get('department_id', '')
    expiring = request.args.get('expiring', '')
    show_all = request.args.get('show_all', 'false')
    
    # Build query
    query = Document.query
    
    # Apply filters
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if employee_id and employee_id.isdigit():
        query = query.filter(Document.employee_id == int(employee_id))
    
    # تصفية حسب القسم
    if department_id and department_id.isdigit():
        query = query.join(Employee).filter(Employee.department_id == int(department_id))
    
    if expiring:
        # Get documents expiring in the next 30, 60, or 90 days
        days = 30
        if expiring == '60':
            days = 60
        elif expiring == '90':
            days = 90
        
        future_date = datetime.now().date() + timedelta(days=days)
        query = query.filter(Document.expiry_date <= future_date, 
                             Document.expiry_date >= datetime.now().date())
    
    # فلترة الوثائق التي باقي على انتهائها أكثر من 30 يوماً
    today = datetime.now().date()
    if show_all.lower() != 'true':
        # عرض الوثائق التي تنتهي في خلال 30 يوم أو أقل أو المنتهية بالفعل
        future_date_30_days = today + timedelta(days=30)
        query = query.filter(
            (Document.expiry_date <= future_date_30_days) | 
            (Document.expiry_date < today)
        )
    
    # Execute query
    documents = query.all()
    
    # احسب عدد الوثائق الكلي والمنتهية والقريبة من الانتهاء
    total_docs = Document.query.count()
    expired_docs = Document.query.filter(Document.expiry_date < today).count()
    expiring_soon = Document.query.filter(
        Document.expiry_date <= today + timedelta(days=30),
        Document.expiry_date >= today
    ).count()
    safe_docs = total_docs - expired_docs - expiring_soon
    
    # Get all employees for filter dropdown
    employees = Employee.query.all()
    
    # Get all departments for filter dropdown
    departments = Department.query.all()
    
    # Get document types for filter dropdown
    document_types = [
        'national_id', 'passport', 'health_certificate', 
        'work_permit', 'education_certificate', 'driving_license',
        'annual_leave', 'other'
    ]
    
    return render_template('documents/index.html',
                          documents=documents,
                          employees=employees,
                          departments=departments,
                          document_types=document_types,
                          selected_type=document_type,
                          selected_employee=employee_id,
                          selected_department=department_id,
                          selected_expiring=expiring,
                          show_all=show_all.lower() == 'true',
                          total_docs=total_docs,
                          expired_docs=expired_docs,
                          expiring_soon=expiring_soon,
                          safe_docs=safe_docs,
                          now=datetime.now())

@documents_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new document record"""
    if request.method == 'POST':
        try:
            # تحقق من وجود CSRF token
            if 'csrf_token' not in request.form:
                flash('خطأ في التحقق من الأمان. يرجى المحاولة مرة أخرى.', 'danger')
                return redirect(url_for('documents.create'))
                
            document_type = request.form['document_type']
            document_number = request.form['document_number']
            issue_date_str = request.form['issue_date']
            expiry_date_str = request.form['expiry_date']
            notes = request.form.get('notes', '')
            add_type = request.form.get('add_type', 'single')
            
            # Parse dates
            issue_date = parse_date(issue_date_str)
            expiry_date = parse_date(expiry_date_str)
            
            # تحديد ما إذا كان الإضافة لموظف واحد أو لقسم كامل
            if add_type == 'single':
                # إضافة وثيقة لموظف واحد
                employee_id = request.form.get('employee_id')
                if not employee_id:
                    flash('يرجى اختيار الموظف', 'danger')
                    return redirect(url_for('documents.create'))
                
                # Create new document record
                document = Document(
                    employee_id=employee_id,
                    document_type=document_type,
                    document_number=document_number,
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    notes=notes
                )
                
                db.session.add(document)
                
                # Log the action
                employee = Employee.query.get(employee_id)
                audit = SystemAudit(
                    action='create',
                    entity_type='document',
                    entity_id=employee_id,
                    details=f'تم إضافة وثيقة جديدة من نوع {document_type} للموظف: {employee.name}',
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(audit)
                db.session.commit()
                
                flash('تم إضافة الوثيقة بنجاح', 'success')
            
            else:
                # إضافة وثيقة لقسم كامل
                department_id = request.form.get('department_id')
                if not department_id:
                    flash('يرجى اختيار القسم', 'danger')
                    return redirect(url_for('documents.create'))
                
                # الحصول على جميع موظفي القسم
                department = Department.query.get(department_id)
                employees = department.employees
                
                if not employees:
                    flash(f'لا يوجد موظفين في قسم "{department.name}"', 'warning')
                    return redirect(url_for('documents.create'))
                
                # إنشاء وثيقة لكل موظف في القسم
                document_count = 0
                for employee in employees:
                    # تخصيص رقم الوثيقة لكل موظف (إضافة الرقم الوظيفي في نهاية رقم الوثيقة)
                    employee_document_number = f"{document_number}-{employee.employee_id}"
                    
                    document = Document(
                        employee_id=employee.id,
                        document_type=document_type,
                        document_number=employee_document_number,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        notes=notes
                    )
                    
                    db.session.add(document)
                    document_count += 1
                
                # إنشاء سجل تدقيق للعملية
                audit = SystemAudit(
                    action='create_bulk',
                    entity_type='document',
                    entity_id=department_id,
                    details=f'تم إضافة {document_count} وثيقة من نوع {document_type} لقسم: {department.name}',
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(audit)
                db.session.commit()
                
                flash(f'تم إضافة {document_count} وثائق بنجاح لجميع موظفي قسم "{department.name}"', 'success')
            
            return redirect(url_for('documents.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all employees for dropdown
    employees = Employee.query.all()
    
    # Get all departments for dropdown
    departments = Department.query.all()
    
    # Get document types for dropdown
    document_types = [
        'national_id', 'passport', 'health_certificate', 
        'work_permit', 'education_certificate', 'driving_license',
        'annual_leave', 'other'
    ]
    
    # Default dates
    today = datetime.now().date()
    hijri_today = format_date_hijri(today)
    gregorian_today = format_date_gregorian(today)
    
    return render_template('documents/create.html',
                          employees=employees,
                          departments=departments,
                          document_types=document_types,
                          today=today,
                          hijri_today=hijri_today,
                          gregorian_today=gregorian_today)

@documents_bp.route('/<int:id>/confirm-delete')
def confirm_delete(id):
    """صفحة تأكيد حذف وثيقة"""
    document = Document.query.get_or_404(id)
    return render_template('documents/confirm_delete.html', document=document)

@documents_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a document record"""
    # تحقق من وجود CSRF token
    if 'csrf_token' not in request.form:
        flash('خطأ في التحقق من الأمان. يرجى المحاولة مرة أخرى.', 'danger')
        return redirect(url_for('documents.index'))
    
    document = Document.query.get_or_404(id)
    employee_name = document.employee.name
    document_type = document.document_type
    
    try:
        db.session.delete(document)
        
        # Log the action
        audit = SystemAudit(
            action='delete',
            entity_type='document',
            entity_id=id,
            details=f'تم حذف وثيقة من نوع {document_type} للموظف: {employee_name}',
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('تم حذف الوثيقة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الوثيقة: {str(e)}', 'danger')
    
    return redirect(url_for('documents.index'))

@documents_bp.route('/<int:id>/update_expiry', methods=['GET', 'POST'])
def update_expiry(id):
    """تحديث تاريخ انتهاء الوثيقة"""
    document = Document.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # تحقق من وجود CSRF token
            if 'csrf_token' not in request.form:
                flash('خطأ في التحقق من الأمان. يرجى المحاولة مرة أخرى.', 'danger')
                return redirect(url_for('documents.update_expiry', id=id))
            
            expiry_date_str = request.form['expiry_date']
            # تحليل التاريخ
            expiry_date = parse_date(expiry_date_str)
            
            # حفظ التاريخ القديم للسجل
            old_expiry_date = document.expiry_date
            
            # تحديث تاريخ الانتهاء
            document.expiry_date = expiry_date
            
            # إضافة سجل للتدقيق
            audit = SystemAudit(
                action='update',
                entity_type='document',
                entity_id=id,
                details=f'تم تحديث تاريخ انتهاء وثيقة {document.document_type} للموظف: {document.employee.name} من {old_expiry_date} إلى {expiry_date}',
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم تحديث تاريخ انتهاء الوثيقة بنجاح', 'success')
            return redirect(url_for('documents.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث تاريخ انتهاء الوثيقة: {str(e)}', 'danger')
            return redirect(url_for('documents.update_expiry', id=id))
    
    # Get document types for dropdown
    document_types_map = {
        'national_id': 'الهوية الوطنية',
        'passport': 'جواز السفر',
        'health_certificate': 'الشهادة الصحية',
        'work_permit': 'تصريح العمل',
        'education_certificate': 'الشهادة الدراسية',
        'driving_license': 'رخصة القيادة',
        'annual_leave': 'الإجازة السنوية',
        'other': 'أخرى'
    }
    
    # احصل على اسم نوع الوثيقة بالعربية
    doc_type_ar = document_types_map.get(document.document_type, document.document_type)
    
    # Default dates
    today = datetime.now().date()
    hijri_today = format_date_hijri(today)
    gregorian_today = format_date_gregorian(today)
    
    return render_template('documents/update_expiry.html',
                          document=document,
                          document_type_ar=doc_type_ar,
                          today=today,
                          hijri_today=hijri_today,
                          gregorian_today=gregorian_today)

@documents_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Import document records from Excel file"""
    if request.method == 'POST':
        # تحقق من وجود CSRF token
        if 'csrf_token' not in request.form:
            flash('خطأ في التحقق من الأمان. يرجى المحاولة مرة أخرى.', 'danger')
            return redirect(request.url)
            
        if 'file' not in request.files:
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            try:
                # Parse Excel file
                documents_data = parse_document_excel(file)
                success_count = 0
                error_count = 0
                
                for data in documents_data:
                    try:
                        document = Document(**data)
                        db.session.add(document)
                        db.session.commit()
                        success_count += 1
                    except Exception:
                        db.session.rollback()
                        error_count += 1
                
                # Log the import
                audit = SystemAudit(
                    action='import',
                    entity_type='document',
                    entity_id=0,
                    details=f'تم استيراد {success_count} وثيقة بنجاح و {error_count} فشل',
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(audit)
                db.session.commit()
                
                if error_count > 0:
                    flash(f'تم استيراد {success_count} وثيقة بنجاح و {error_count} فشل', 'warning')
                else:
                    flash(f'تم استيراد {success_count} وثيقة بنجاح', 'success')
                return redirect(url_for('documents.index'))
            except Exception as e:
                flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
        else:
            flash('الملف يجب أن يكون بصيغة Excel (.xlsx, .xls)', 'danger')
    
    return render_template('documents/import.html')

@documents_bp.route('/expiring')
def expiring():
    """Show documents that are about to expire"""
    days = int(request.args.get('days', '30'))
    document_type = request.args.get('document_type', '')
    
    # Calculate expiry date range
    today = datetime.now().date()
    future_date = today + timedelta(days=days)
    
    # Build query for expiring documents
    query = Document.query.filter(
        Document.expiry_date <= future_date,
        Document.expiry_date >= today
    )
    
    # Apply document type filter if provided
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Execute query
    documents = query.all()
    
    # Get document types for filter dropdown
    document_types = [
        'national_id', 'passport', 'health_certificate', 
        'work_permit', 'education_certificate', 'driving_license',
        'annual_leave', 'other'
    ]
    
    return render_template('documents/expiring.html',
                          documents=documents,
                          days=days,
                          document_types=document_types,
                          selected_type=document_type)

@documents_bp.route('/expiry_stats')
def expiry_stats():
    """Get document expiry statistics"""
    # Calculate expiry date ranges
    today = datetime.now().date()
    thirty_days = today + timedelta(days=30)
    sixty_days = today + timedelta(days=60)
    ninety_days = today + timedelta(days=90)
    
    # Get count of documents expiring in different periods
    expiring_30 = Document.query.filter(
        Document.expiry_date <= thirty_days,
        Document.expiry_date >= today
    ).count()
    
    expiring_60 = Document.query.filter(
        Document.expiry_date <= sixty_days,
        Document.expiry_date > thirty_days
    ).count()
    
    expiring_90 = Document.query.filter(
        Document.expiry_date <= ninety_days,
        Document.expiry_date > sixty_days
    ).count()
    
    expired = Document.query.filter(
        Document.expiry_date < today
    ).count()
    
    # Get document counts by type
    type_counts = db.session.query(
        Document.document_type,
        func.count(Document.id).label('count')
    ).group_by(Document.document_type).all()
    
    # Format for response
    type_stats = {}
    for doc_type, count in type_counts:
        type_stats[doc_type] = count
    
    return jsonify({
        'expiring_30': expiring_30,
        'expiring_60': expiring_60,
        'expiring_90': expiring_90,
        'expired': expired,
        'type_stats': type_stats
    })

@documents_bp.route('/employee/<int:employee_id>/export_pdf')
def export_employee_documents_pdf(employee_id):
    """Export employee documents to PDF"""
    employee = Employee.query.get_or_404(employee_id)
    documents = Document.query.filter_by(employee_id=employee_id).all()
    
    # إنشاء ملف PDF
    buffer = BytesIO()
    
    # تسجيل الخط العربي
    try:
        # محاولة تسجيل الخط العربي إذا لم يكن مسجلاً مسبقًا
        pdfmetrics.registerFont(TTFont('Arabic', 'static/fonts/Arial.ttf'))
    except:
        # إذا كان هناك خطأ، نستخدم الخط الافتراضي
        pass
    
    # تعيين أبعاد الصفحة واتجاهها
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # إعداد الأنماط
    styles = getSampleStyleSheet()
    # إنشاء نمط للنص العربي
    arabic_style = ParagraphStyle(
        name='Arabic',
        parent=styles['Normal'],
        fontName='Arabic',
        fontSize=10,
        alignment=2, # يمين (RTL)
        textColor=colors.black
    )
    
    # إنشاء نمط للعناوين
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontName='Arabic',
        fontSize=16,
        alignment=1, # وسط
        textColor=colors.black
    )
    
    # إنشاء نمط للعناوين الفرعية
    subtitle_style = ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontName='Arabic',
        fontSize=14,
        alignment=2, # يمين (RTL)
        textColor=colors.blue
    )
    
    # إعداد المحتوى
    elements = []
    
    # إضافة العنوان
    title = f"وثائق الموظف: {employee.name}"
    # تهيئة النص العربي للعرض في PDF
    title = get_display(arabic_reshaper.reshape(title))
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    # إضافة بيانات الموظف في جدول
    employee_data = [
        [get_display(arabic_reshaper.reshape("بيانات الموظف")), "", get_display(arabic_reshaper.reshape("معلومات العمل")), ""],
        [
            get_display(arabic_reshaper.reshape("الاسم:")), 
            get_display(arabic_reshaper.reshape(employee.name)), 
            get_display(arabic_reshaper.reshape("المسمى الوظيفي:")), 
            get_display(arabic_reshaper.reshape(employee.job_title))
        ],
        [
            get_display(arabic_reshaper.reshape("الرقم الوظيفي:")), 
            employee.employee_id, 
            get_display(arabic_reshaper.reshape("القسم:")), 
            get_display(arabic_reshaper.reshape(employee.department.name if employee.department else '-'))
        ],
        [
            get_display(arabic_reshaper.reshape("رقم الهوية:")), 
            employee.national_id, 
            get_display(arabic_reshaper.reshape("الحالة:")), 
            get_display(arabic_reshaper.reshape(employee.status))
        ],
        [
            get_display(arabic_reshaper.reshape("رقم الجوال:")), 
            employee.mobile, 
            get_display(arabic_reshaper.reshape("الموقع:")), 
            get_display(arabic_reshaper.reshape(employee.location or '-'))
        ]
    ]
    
    # إنشاء جدول بيانات الموظف
    employee_table = Table(employee_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('BACKGROUND', (2, 0), (3, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
        ('FONTNAME', (0, 0), (3, 0), 'Arabic'),
        ('FONTSIZE', (0, 0), (3, 0), 12),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('VALIGN', (0, 0), (3, 4), 'MIDDLE'),
        ('GRID', (0, 0), (3, 4), 0.5, colors.grey),
        ('BOX', (0, 0), (1, 4), 1, colors.black),
        ('BOX', (2, 0), (3, 4), 1, colors.black),
    ]))
    elements.append(employee_table)
    elements.append(Spacer(1, 20))
    
    # إضافة عنوان قائمة الوثائق
    subtitle = get_display(arabic_reshaper.reshape("قائمة الوثائق"))
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 10))
    
    # إنشاء جدول الوثائق
    headers = [
        get_display(arabic_reshaper.reshape("نوع الوثيقة")),
        get_display(arabic_reshaper.reshape("رقم الوثيقة")),
        get_display(arabic_reshaper.reshape("تاريخ الإصدار")),
        get_display(arabic_reshaper.reshape("تاريخ الانتهاء")),
        get_display(arabic_reshaper.reshape("الحالة")),
        get_display(arabic_reshaper.reshape("ملاحظات"))
    ]
    
    data = [headers]
    
    # إضافة صفوف الوثائق
    today = datetime.now().date()
    
    # ترجمة أنواع الوثائق
    document_types_map = {
        'national_id': 'الهوية الوطنية',
        'passport': 'جواز السفر',
        'health_certificate': 'الشهادة الصحية',
        'work_permit': 'تصريح العمل',
        'education_certificate': 'الشهادة الدراسية',
        'driving_license': 'رخصة القيادة',
        'annual_leave': 'الإجازة السنوية'
    }
    
    for doc in documents:
        # الحصول على نوع الوثيقة بالعربية
        doc_type_ar = document_types_map.get(doc.document_type, doc.document_type)
        
        # التحقق من حالة انتهاء الصلاحية
        days_to_expiry = (doc.expiry_date - today).days
        if days_to_expiry < 0:
            status_text = "منتهية"
        elif days_to_expiry < 30:
            status_text = f"تنتهي خلال {days_to_expiry} يوم"
        else:
            status_text = "سارية"
        
        # إضافة صف للجدول
        row = [
            get_display(arabic_reshaper.reshape(doc_type_ar)),
            doc.document_number,
            format_date_gregorian(doc.issue_date),
            format_date_gregorian(doc.expiry_date),
            get_display(arabic_reshaper.reshape(status_text)),
            get_display(arabic_reshaper.reshape(doc.notes or '-'))
        ]
        data.append(row)
    
    # إنشاء جدول الوثائق إذا كان هناك وثائق
    if len(data) > 1:
        # حساب عرض الأعمدة بناءً على عرض الصفحة
        table_width = A4[0] - 4*cm  # العرض الإجمالي ناقص الهوامش
        col_widths = [3.5*cm, 3*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm]
        documents_table = Table(data, colWidths=col_widths)
        
        # تنسيق الجدول
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # تطبيق التناوب في ألوان الصفوف
        for i in range(1, len(data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)
            
            # إضافة ألوان حالة انتهاء الصلاحية
            days_to_expiry = (documents[i-1].expiry_date - today).days
            if days_to_expiry < 0:
                table_style.add('TEXTCOLOR', (4, i), (4, i), colors.red)
                table_style.add('FONTSIZE', (4, i), (4, i), 10)
            elif days_to_expiry < 30:
                table_style.add('TEXTCOLOR', (4, i), (4, i), colors.orange)
        
        documents_table.setStyle(table_style)
        elements.append(documents_table)
    else:
        # إذا لم تكن هناك وثائق
        no_data_text = get_display(arabic_reshaper.reshape("لا توجد وثائق مسجلة لهذا الموظف"))
        elements.append(Paragraph(no_data_text, arabic_style))
    
    # إضافة معلومات التقرير في أسفل الصفحة
    elements.append(Spacer(1, 30))
    footer_text = f"تم إنشاء هذا التقرير بتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    footer_text = get_display(arabic_reshaper.reshape(footer_text))
    elements.append(Paragraph(footer_text, arabic_style))
    
    # بناء المستند
    doc.build(elements)
    
    # إعادة المؤشر إلى بداية البايت
    buffer.seek(0)
    
    # إنشاء استجابة تحميل
    buffer.seek(0)
    return make_response(send_file(
        buffer,
        as_attachment=True,
        download_name=f'employee_{employee_id}_documents.pdf',
        mimetype='application/pdf'
    ))

@documents_bp.route('/employee/<int:employee_id>/export_excel')
def export_employee_documents_excel(employee_id):
    """Export employee documents to Excel"""
    employee = Employee.query.get_or_404(employee_id)
    documents = Document.query.filter_by(employee_id=employee_id).all()
    
    # Create Excel in memory
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("الوثائق")
    
    # Add formatting
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#D3E0EA',
        'border': 1,
        'font_size': 13
    })
    
    # RTL format for workbook
    worksheet.right_to_left()
    
    # Add cell formats
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11,
        'num_format': 'dd/mm/yyyy'
    })
    
    # Write headers
    headers = ['نوع الوثيقة', 'رقم الوثيقة', 'تاريخ الإصدار', 'تاريخ الانتهاء', 'ملاحظات']
    for col_num, data in enumerate(headers):
        worksheet.write(0, col_num, data, header_format)
    
    # Adjust column widths
    worksheet.set_column(0, 0, 20)  # نوع الوثيقة
    worksheet.set_column(1, 1, 20)  # رقم الوثيقة
    worksheet.set_column(2, 2, 15)  # تاريخ الإصدار
    worksheet.set_column(3, 3, 15)  # تاريخ الانتهاء
    worksheet.set_column(4, 4, 30)  # ملاحظات
    
    # Map for document types
    document_types_map = {
        'national_id': 'الهوية الوطنية',
        'passport': 'جواز السفر',
        'health_certificate': 'الشهادة الصحية',
        'work_permit': 'تصريح العمل',
        'education_certificate': 'الشهادة الدراسية',
        'driving_license': 'رخصة القيادة',
        'annual_leave': 'الإجازة السنوية'
    }
    
    # Write data
    for row_num, doc in enumerate(documents, 1):
        # Get document type in Arabic
        doc_type_ar = document_types_map.get(doc.document_type, doc.document_type)
            
        worksheet.write(row_num, 0, doc_type_ar, cell_format)
        worksheet.write(row_num, 1, doc.document_number, cell_format)
        worksheet.write_datetime(row_num, 2, doc.issue_date, date_format)
        worksheet.write_datetime(row_num, 3, doc.expiry_date, date_format)
        worksheet.write(row_num, 4, doc.notes or '', cell_format)
    
    # Add title with employee info
    info_worksheet = workbook.add_worksheet("معلومات الموظف")
    info_worksheet.right_to_left()
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#B8D9EB',
        'border': 2
    })
    
    info_worksheet.merge_range('A1:B1', f'بيانات الموظف: {employee.name}', title_format)
    info_worksheet.set_column(0, 0, 20)
    info_worksheet.set_column(1, 1, 30)
    
    field_format = workbook.add_format({
        'bold': True,
        'align': 'right',
        'valign': 'vcenter',
        'bg_color': '#F0F0F0',
        'border': 1
    })
    
    info_fields = [
        ['الاسم', employee.name],
        ['الرقم الوظيفي', employee.employee_id],
        ['رقم الهوية', employee.national_id],
        ['رقم الجوال', employee.mobile],
        ['القسم', employee.department.name if employee.department else ''],
        ['المسمى الوظيفي', employee.job_title],
        ['الحالة', employee.status],
        ['الموقع', employee.location or '']
    ]
    
    for row_num, (field, value) in enumerate(info_fields):
        info_worksheet.write(row_num + 1, 0, field, field_format)
        info_worksheet.write(row_num + 1, 1, value, cell_format)
    
    # Close workbook
    workbook.close()
    
    # Create response
    output.seek(0)
    return make_response(send_file(
        output,
        as_attachment=True,
        download_name=f'employee_{employee_id}_documents.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ))

@documents_bp.route('/export_excel')
def export_excel():
    """Export all documents to Excel"""
    # Get filter parameters
    document_type = request.args.get('document_type', '')
    days = int(request.args.get('days', '0'))
    show_all = request.args.get('show_all', 'false').lower() == 'true'
    
    # Build query
    query = Document.query
    
    # Apply document type filter
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Apply days filter for expiration
    if days > 0 and not show_all:
        today = datetime.now().date()
        future_date = today + timedelta(days=days)
        query = query.filter(
            Document.expiry_date <= future_date,
            Document.expiry_date >= today
        )
    
    # Get documents with employee information
    query = query.join(Employee).options(selectinload(Document.employee))
    documents = query.order_by(Document.expiry_date).all()
    
    # Create Excel in memory
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Get today's date for remaining days calculation
    today = datetime.now().date()
    
    # Create document status lists
    expired_docs = []
    expiring_soon_docs = []
    valid_docs = []
    
    # Categorize documents
    for doc in documents:
        days_remaining = (doc.expiry_date - today).days
        if days_remaining < 0:
            expired_docs.append(doc)
        elif days_remaining < 30:
            expiring_soon_docs.append(doc)
        else:
            valid_docs.append(doc)
    
    # Map for document types
    document_types_map = {
        'national_id': 'الهوية الوطنية',
        'passport': 'جواز السفر',
        'health_certificate': 'الشهادة الصحية',
        'work_permit': 'تصريح العمل',
        'education_certificate': 'الشهادة الدراسية',
        'driving_license': 'رخصة القيادة',
        'annual_leave': 'الإجازة السنوية'
    }
    
    # Format definitions
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#D3E0EA',
        'border': 1,
        'font_size': 13
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11,
        'num_format': 'dd/mm/yyyy'
    })
    
    expired_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11,
        'bg_color': '#FFC7CE',  # Light red
        'font_color': '#9C0006'  # Dark red
    })
    
    warning_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11,
        'bg_color': '#FFEB9C',  # Light yellow
        'font_color': '#9C6500'  # Dark orange
    })
    
    valid_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'font_size': 11,
        'bg_color': '#C6EFCE',  # Light green
        'font_color': '#006100'  # Dark green
    })
    
    # Headers definition
    headers = ['اسم الموظف', 'الرقم الوظيفي', 'القسم', 'نوع الوثيقة', 'رقم الوثيقة', 'تاريخ الإصدار', 'تاريخ الانتهاء', 'الأيام المتبقية', 'ملاحظات']
    
    # Add main worksheet with all documents (sorted by expiry date)
    main_worksheet = workbook.add_worksheet("جميع الوثائق")
    main_worksheet.right_to_left()
    
    # Set column widths for main worksheet
    main_worksheet.set_column(0, 0, 25)  # اسم الموظف
    main_worksheet.set_column(1, 1, 15)  # الرقم الوظيفي
    main_worksheet.set_column(2, 2, 20)  # القسم
    main_worksheet.set_column(3, 3, 20)  # نوع الوثيقة
    main_worksheet.set_column(4, 4, 20)  # رقم الوثيقة
    main_worksheet.set_column(5, 5, 15)  # تاريخ الإصدار
    main_worksheet.set_column(6, 6, 15)  # تاريخ الانتهاء
    main_worksheet.set_column(7, 7, 15)  # الأيام المتبقية
    main_worksheet.set_column(8, 8, 30)  # ملاحظات
    
    # Write headers for main worksheet
    for col_num, data in enumerate(headers):
        main_worksheet.write(0, col_num, data, header_format)
    
    # Write all documents to main worksheet
    row_num = 1
    for doc in sorted(documents, key=lambda x: x.expiry_date):
        # Get employee information
        employee_name = doc.employee.name if doc.employee else "غير متوفر"
        employee_id = doc.employee.employee_id if doc.employee else "غير متوفر"
        department_name = doc.employee.department.name if doc.employee and doc.employee.department else "غير متوفر"
        
        # Get document type in Arabic
        doc_type_ar = document_types_map.get(doc.document_type, doc.document_type)
        
        # Calculate remaining days
        days_remaining = (doc.expiry_date - today).days
        
        # Determine format for days remaining
        days_format = cell_format
        if days_remaining < 0:
            days_format = expired_format
        elif days_remaining < 30:
            days_format = warning_format
        else:
            days_format = valid_format
        
        # Write data
        main_worksheet.write(row_num, 0, employee_name, cell_format)
        main_worksheet.write(row_num, 1, employee_id, cell_format)
        main_worksheet.write(row_num, 2, department_name, cell_format)
        main_worksheet.write(row_num, 3, doc_type_ar, cell_format)
        main_worksheet.write(row_num, 4, doc.document_number, cell_format)
        main_worksheet.write_datetime(row_num, 5, doc.issue_date, date_format)
        main_worksheet.write_datetime(row_num, 6, doc.expiry_date, date_format)
        main_worksheet.write(row_num, 7, days_remaining, days_format)
        main_worksheet.write(row_num, 8, doc.notes or '', cell_format)
        row_num += 1
        
    # Function to create a worksheet for a category of documents
    def create_category_worksheet(docs, name, title_bg_color, sheet_icon=''):
        if not docs:  # Skip if no documents in this category
            return
            
        ws = workbook.add_worksheet(f"{sheet_icon}{name}")
        ws.right_to_left()
        
        # Set column widths
        for i, width in enumerate([25, 15, 20, 20, 20, 15, 15, 15, 30]):
            ws.set_column(i, i, width)
        
        # Custom title format for this category
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': title_bg_color,
            'border': 2
        })
        
        # Add title
        ws.merge_range('A1:I1', f"{name} ({len(docs)})", title_format)
        
        # Write headers
        for col_num, data in enumerate(headers):
            ws.write(1, col_num, data, header_format)
        
        # Write data
        for row_num, doc in enumerate(sorted(docs, key=lambda x: x.expiry_date), 2):
            # Get employee information
            employee_name = doc.employee.name if doc.employee else "غير متوفر"
            employee_id = doc.employee.employee_id if doc.employee else "غير متوفر"
            department_name = doc.employee.department.name if doc.employee and doc.employee.department else "غير متوفر"
            
            # Get document type in Arabic
            doc_type_ar = document_types_map.get(doc.document_type, doc.document_type)
            
            # Calculate remaining days
            days_remaining = (doc.expiry_date - today).days
            
            # Write data
            ws.write(row_num, 0, employee_name, cell_format)
            ws.write(row_num, 1, employee_id, cell_format)
            ws.write(row_num, 2, department_name, cell_format)
            ws.write(row_num, 3, doc_type_ar, cell_format)
            ws.write(row_num, 4, doc.document_number, cell_format)
            ws.write_datetime(row_num, 5, doc.issue_date, date_format)
            ws.write_datetime(row_num, 6, doc.expiry_date, date_format)
            ws.write(row_num, 7, days_remaining, 
                    expired_format if days_remaining < 0 else 
                    warning_format if days_remaining < 30 else 
                    valid_format)
            ws.write(row_num, 8, doc.notes or '', cell_format)
    
    # Create worksheets for each category
    create_category_worksheet(expired_docs, "وثائق منتهية", '#FFD9D9', '🔴 ')
    create_category_worksheet(expiring_soon_docs, "وثائق تنتهي قريباً", '#FFF4D9', '🟠 ')
    create_category_worksheet(valid_docs, "وثائق سارية", '#E8FFE8', '🟢 ')
    
    # Add statistics worksheet
    stats_worksheet = workbook.add_worksheet("إحصائيات")
    stats_worksheet.right_to_left()
    
    # Set up statistics
    expired_count = sum(1 for doc in documents if (doc.expiry_date - today).days < 0)
    expiring_30_count = sum(1 for doc in documents if 0 <= (doc.expiry_date - today).days < 30)
    expiring_60_count = sum(1 for doc in documents if 30 <= (doc.expiry_date - today).days < 60)
    expiring_90_count = sum(1 for doc in documents if 60 <= (doc.expiry_date - today).days < 90)
    valid_count = sum(1 for doc in documents if (doc.expiry_date - today).days >= 90)
    
    # Document counts by type
    doc_type_counts = {}
    for doc in documents:
        doc_type = document_types_map.get(doc.document_type, doc.document_type)
        if doc_type in doc_type_counts:
            doc_type_counts[doc_type] += 1
        else:
            doc_type_counts[doc_type] = 1
    
    # Write statistics
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#B8D9EB',
        'border': 2
    })
    
    stats_worksheet.merge_range('A1:B1', 'إحصائيات الوثائق', title_format)
    stats_worksheet.set_column(0, 0, 25)
    stats_worksheet.set_column(1, 1, 15)
    
    stat_header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#E6E6E6',
        'border': 1,
        'font_size': 12
    })
    
    # تنسيق للحقول
    field_format = workbook.add_format({
        'bold': True,
        'align': 'right',
        'valign': 'vcenter',
        'bg_color': '#F0F0F0',
        'border': 1
    })
    
    # Write expiry statistics
    stats_worksheet.write(2, 0, 'حالة صلاحية الوثائق', stat_header_format)
    stats_worksheet.write(2, 1, 'العدد', stat_header_format)
    
    row = 3
    # تنسيق خاص لإجمالي الوثائق
    total_format = workbook.add_format({
        'bold': True, 
        'border': 1, 
        'bg_color': '#D9D9D9'
    })
    
    stats_data = [
        ['وثائق منتهية', expired_count, expired_format],
        ['تنتهي خلال 30 يوم', expiring_30_count, warning_format],
        ['تنتهي خلال 60 يوم', expiring_60_count, cell_format],
        ['تنتهي خلال 90 يوم', expiring_90_count, cell_format],
        ['صالحة لأكثر من 90 يوم', valid_count, cell_format],
        ['المجموع', len(documents), total_format]
    ]
    
    for label, count, fmt in stats_data:
        stats_worksheet.write(row, 0, label, field_format)
        stats_worksheet.write(row, 1, count, fmt)
        row += 1
    
    # Add some space
    row += 2
    
    # Write document type statistics
    stats_worksheet.write(row, 0, 'أنواع الوثائق', stat_header_format)
    stats_worksheet.write(row, 1, 'العدد', stat_header_format)
    row += 1
    
    # Sort document types by count (descending)
    sorted_doc_types = sorted(doc_type_counts.items(), key=lambda x: x[1], reverse=True)
    
    for doc_type, count in sorted_doc_types:
        stats_worksheet.write(row, 0, doc_type, cell_format)
        stats_worksheet.write(row, 1, count, cell_format)
        row += 1
    
    # Close workbook
    workbook.close()
    
    # Create response
    output.seek(0)
    
    # Generate a descriptive filename
    filename_parts = []
    if document_type:
        filename_parts.append(document_types_map.get(document_type, document_type))
    if days > 0 and not show_all:
        filename_parts.append(f"خلال_{days}_يوم")
    if not filename_parts:
        filename_parts.append("جميع_الوثائق")
    
    filename = "_".join(filename_parts) + ".xlsx"
    
    return make_response(send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ))
