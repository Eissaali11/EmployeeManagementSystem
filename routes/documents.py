from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from sqlalchemy import func
from datetime import datetime, timedelta
import io
import csv
import pdfkit
from app import db
from models import Document, Employee, SystemAudit
from utils.excel import parse_document_excel
from utils.date_converter import parse_date, format_date_hijri, format_date_gregorian

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/')
def index():
    """List document records with filtering options"""
    # Get filter parameters
    document_type = request.args.get('document_type', '')
    employee_id = request.args.get('employee_id', '')
    expiring = request.args.get('expiring', '')
    
    # Build query
    query = Document.query
    
    # Apply filters
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if employee_id and employee_id.isdigit():
        query = query.filter(Document.employee_id == int(employee_id))
    
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
    
    # Execute query
    documents = query.all()
    
    # Get all employees for filter dropdown
    employees = Employee.query.all()
    
    # Get document types for filter dropdown
    document_types = [
        'national_id', 'passport', 'health_certificate', 
        'work_permit', 'education_certificate', 'driving_license',
        'annual_leave', 'other'
    ]
    
    return render_template('documents/index.html',
                          documents=documents,
                          employees=employees,
                          document_types=document_types,
                          selected_type=document_type,
                          selected_employee=employee_id,
                          selected_expiring=expiring)

@documents_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new document record"""
    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            document_type = request.form['document_type']
            document_number = request.form['document_number']
            issue_date_str = request.form['issue_date']
            expiry_date_str = request.form['expiry_date']
            
            # Parse dates
            issue_date = parse_date(issue_date_str)
            expiry_date = parse_date(expiry_date_str)
            
            # Create new document record
            document = Document(
                employee_id=employee_id,
                document_type=document_type,
                document_number=document_number,
                issue_date=issue_date,
                expiry_date=expiry_date,
                notes=request.form.get('notes', '')
            )
            
            db.session.add(document)
            
            # Log the action
            employee = Employee.query.get(employee_id)
            audit = SystemAudit(
                action='create',
                entity_type='document',
                entity_id=employee_id,
                details=f'تم إضافة وثيقة جديدة من نوع {document_type} للموظف: {employee.name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم إضافة الوثيقة بنجاح', 'success')
            return redirect(url_for('documents.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all employees for dropdown
    employees = Employee.query.all()
    
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
                          document_types=document_types,
                          today=today,
                          hijri_today=hijri_today,
                          gregorian_today=gregorian_today)

@documents_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a document record"""
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
            details=f'تم حذف وثيقة من نوع {document_type} للموظف: {employee_name}'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('تم حذف الوثيقة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الوثيقة: {str(e)}', 'danger')
    
    return redirect(url_for('documents.index'))

@documents_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Import document records from Excel file"""
    if request.method == 'POST':
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
                    details=f'تم استيراد {success_count} وثيقة بنجاح و {error_count} فشل'
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
    
    # Prepare HTML content
    html_content = f"""
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>وثائق الموظف - {employee.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; padding: 20px; }}
            h1 {{ color: #2a5885; text-align: center; }}
            h2 {{ color: #2a5885; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #2a5885; color: white; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            .header-item {{ flex: 1; }}
            .expired {{ color: red; font-weight: bold; }}
            .valid {{ color: green; }}
            .warning {{ color: orange; }}
        </style>
    </head>
    <body>
        <h1>وثائق الموظف: {employee.name}</h1>
        
        <div class="header">
            <div class="header-item">
                <h3>بيانات الموظف</h3>
                <p><strong>الاسم:</strong> {employee.name}</p>
                <p><strong>الرقم الوظيفي:</strong> {employee.employee_id}</p>
                <p><strong>رقم الهوية:</strong> {employee.national_id}</p>
                <p><strong>رقم الجوال:</strong> {employee.mobile}</p>
            </div>
            <div class="header-item">
                <h3>معلومات العمل</h3>
                <p><strong>المسمى الوظيفي:</strong> {employee.job_title}</p>
                <p><strong>القسم:</strong> {employee.department.name if employee.department else '-'}</p>
                <p><strong>الحالة:</strong> {employee.status}</p>
                <p><strong>الموقع:</strong> {employee.location or '-'}</p>
            </div>
        </div>
        
        <h2>قائمة الوثائق</h2>
        <table>
            <thead>
                <tr>
                    <th>نوع الوثيقة</th>
                    <th>رقم الوثيقة</th>
                    <th>تاريخ الإصدار</th>
                    <th>تاريخ الانتهاء</th>
                    <th>الحالة</th>
                    <th>ملاحظات</th>
                </tr>
            </thead>
            <tbody>
    """
    
    today = datetime.now().date()
    
    for doc in documents:
        # Get document type in Arabic
        doc_type_ar = ""
        if doc.document_type == 'national_id':
            doc_type_ar = "الهوية الوطنية"
        elif doc.document_type == 'passport':
            doc_type_ar = "جواز السفر"
        elif doc.document_type == 'health_certificate':
            doc_type_ar = "الشهادة الصحية"
        elif doc.document_type == 'work_permit':
            doc_type_ar = "تصريح العمل"
        elif doc.document_type == 'education_certificate':
            doc_type_ar = "الشهادة الدراسية"
        elif doc.document_type == 'driving_license':
            doc_type_ar = "رخصة القيادة"
        elif doc.document_type == 'annual_leave':
            doc_type_ar = "الإجازة السنوية"
        else:
            doc_type_ar = doc.document_type
        
        # Check expiry status
        days_to_expiry = (doc.expiry_date - today).days
        status_class = ""
        status_text = ""
        
        if days_to_expiry < 0:
            status_class = "expired"
            status_text = "منتهية"
        elif days_to_expiry < 30:
            status_class = "warning"
            status_text = f"تنتهي خلال {days_to_expiry} يوم"
        else:
            status_class = "valid"
            status_text = "سارية"
        
        # Add row to table
        html_content += f"""
            <tr>
                <td>{doc_type_ar}</td>
                <td>{doc.document_number}</td>
                <td>{doc.issue_date.strftime('%d/%m/%Y')}</td>
                <td>{doc.expiry_date.strftime('%d/%m/%Y')}</td>
                <td class="{status_class}">{status_text}</td>
                <td>{doc.notes or '-'}</td>
            </tr>
        """
    
    # Close the HTML content
    html_content += """
            </tbody>
        </table>
        
        <div style="text-align: center; margin-top: 30px;">
            <p>تم إنشاء هذا التقرير يوم {}</p>
        </div>
    </body>
    </html>
    """.format(datetime.now().strftime('%d/%m/%Y'))
    
    # Create PDF from HTML
    pdf = pdfkit.from_string(html_content, False)
    
    # Create response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=employee_{employee_id}_documents.pdf'
    
    return response

@documents_bp.route('/employee/<int:employee_id>/export_excel')
def export_employee_documents_excel(employee_id):
    """Export employee documents to Excel"""
    employee = Employee.query.get_or_404(employee_id)
    documents = Document.query.filter_by(employee_id=employee_id).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['نوع الوثيقة', 'رقم الوثيقة', 'تاريخ الإصدار', 'تاريخ الانتهاء', 'ملاحظات'])
    
    # Write data
    for doc in documents:
        # Get document type in Arabic
        doc_type_ar = ""
        if doc.document_type == 'national_id':
            doc_type_ar = "الهوية الوطنية"
        elif doc.document_type == 'passport':
            doc_type_ar = "جواز السفر"
        elif doc.document_type == 'health_certificate':
            doc_type_ar = "الشهادة الصحية"
        elif doc.document_type == 'work_permit':
            doc_type_ar = "تصريح العمل"
        elif doc.document_type == 'education_certificate':
            doc_type_ar = "الشهادة الدراسية"
        elif doc.document_type == 'driving_license':
            doc_type_ar = "رخصة القيادة"
        elif doc.document_type == 'annual_leave':
            doc_type_ar = "الإجازة السنوية"
        else:
            doc_type_ar = doc.document_type
            
        writer.writerow([
            doc_type_ar,
            doc.document_number,
            doc.issue_date.strftime('%d/%m/%Y'),
            doc.expiry_date.strftime('%d/%m/%Y'),
            doc.notes or ''
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=employee_{employee_id}_documents.csv'
    
    return response
