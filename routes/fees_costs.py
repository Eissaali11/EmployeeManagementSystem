from datetime import datetime, timedelta
import os
import xlsxwriter
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app import db
from models import FeesCost, Document, Employee, Department, SystemAudit

fees_costs_bp = Blueprint('fees_costs', __name__, url_prefix='/fees-costs')

@fees_costs_bp.route('/')
@login_required
def index():
    """عرض صفحة قائمة تكاليف الرسوم مع الوثائق المنتهية والمشرفة على الانتهاء"""
    # استخراج الوثائق المنتهية أو التي تقترب من الانتهاء
    today = datetime.now().date()
    expiry_date_limit = today + timedelta(days=90)  # 90 يومًا من الآن
    
    expired_docs = Document.query.filter(Document.expiry_date < today).join(Employee).order_by(Document.expiry_date.desc()).limit(10).all()
    expiring_docs = Document.query.filter(
        Document.expiry_date >= today,
        Document.expiry_date <= expiry_date_limit
    ).join(Employee).order_by(Document.expiry_date).limit(10).all()
    
    # استخراج تكاليف الرسوم المسجلة
    fees_costs = FeesCost.query.join(Document).join(Employee).all()
    
    # إحصائيات
    total_passport_fees = db.session.query(func.sum(FeesCost.passport_fee)).scalar() or 0
    total_labor_fees = db.session.query(func.sum(FeesCost.labor_office_fee)).scalar() or 0
    total_insurance_fees = db.session.query(func.sum(FeesCost.insurance_fee)).scalar() or 0
    total_social_insurance_fees = db.session.query(func.sum(FeesCost.social_insurance_fee)).scalar() or 0
    total_fees = total_passport_fees + total_labor_fees + total_insurance_fees + total_social_insurance_fees
    
    return render_template('fees_costs/index.html',
                          expired_docs=expired_docs,
                          expiring_docs=expiring_docs,
                          fees_costs=fees_costs,
                          total_passport_fees=total_passport_fees,
                          total_labor_fees=total_labor_fees,
                          total_insurance_fees=total_insurance_fees,
                          total_social_insurance_fees=total_social_insurance_fees,
                          total_fees=total_fees,
                          now=datetime.now())

@fees_costs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """إضافة تكاليف رسوم جديدة"""
    if request.method == 'POST':
        document_id = request.form.get('document_id')
        document_type = request.form.get('document_type')
        passport_fee = float(request.form.get('passport_fee', 0))
        labor_office_fee = float(request.form.get('labor_office_fee', 0))
        insurance_fee = float(request.form.get('insurance_fee', 0))
        social_insurance_fee = float(request.form.get('social_insurance_fee', 0))
        transfer_sponsorship = True if request.form.get('transfer_sponsorship') else False
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        payment_status = request.form.get('payment_status')
        payment_date = None
        payment_date_str = request.form.get('payment_date')
        if payment_date_str:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        notes = request.form.get('notes')
        
        try:
            # التحقق من وجود الوثيقة
            document = Document.query.get_or_404(document_id)
            
            # إنشاء كائن تكاليف الرسوم
            fees_cost = FeesCost(
                document_id=document_id,
                document_type=document_type,
                passport_fee=passport_fee,
                labor_office_fee=labor_office_fee,
                insurance_fee=insurance_fee,
                social_insurance_fee=social_insurance_fee,
                transfer_sponsorship=transfer_sponsorship,
                due_date=due_date,
                payment_status=payment_status,
                payment_date=payment_date,
                notes=notes
            )
            
            # حفظ البيانات
            db.session.add(fees_cost)
            db.session.commit()
            
            # سجل التدقيق
            audit = SystemAudit(
                action='create',
                entity_type='fees_cost',
                entity_id=fees_cost.id,
                details=f'تم إضافة تكاليف رسوم جديدة للوثيقة رقم {document_id}',
                user_id=current_user.id
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تمت إضافة تكاليف الرسوم بنجاح', 'success')
            return redirect(url_for('fees_costs.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة تكاليف الرسوم: {str(e)}', 'danger')
    
    # عرض نموذج إضافة تكاليف رسوم
    # الحصول على الوثائق المنتهية أو المشرفة على الانتهاء
    today = datetime.now().date()
    expiry_date_limit = today + timedelta(days=90)
    
    documents = Document.query.filter(
        (Document.expiry_date < today) | 
        ((Document.expiry_date >= today) & (Document.expiry_date <= expiry_date_limit))
    ).join(Employee).all()
    
    return render_template('fees_costs/create.html',
                          documents=documents,
                          today=today.strftime('%Y-%m-%d'),
                          next_month=today.replace(month=today.month+1 if today.month < 12 else 1, year=today.year+1 if today.month==12 else today.year).strftime('%Y-%m-%d'))

@fees_costs_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل تكاليف رسوم موجودة"""
    fees_cost = FeesCost.query.get_or_404(id)
    
    if request.method == 'POST':
        fees_cost.passport_fee = float(request.form.get('passport_fee', 0))
        fees_cost.labor_office_fee = float(request.form.get('labor_office_fee', 0))
        fees_cost.insurance_fee = float(request.form.get('insurance_fee', 0))
        fees_cost.social_insurance_fee = float(request.form.get('social_insurance_fee', 0))
        fees_cost.transfer_sponsorship = True if request.form.get('transfer_sponsorship') else False
        due_date_str = request.form.get('due_date')
        if due_date_str:
            fees_cost.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        fees_cost.payment_status = request.form.get('payment_status')
        
        payment_date_str = request.form.get('payment_date')
        if payment_date_str:
            fees_cost.payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        else:
            fees_cost.payment_date = None
        
        fees_cost.notes = request.form.get('notes')
        
        try:
            # سجل التدقيق
            audit = SystemAudit(
                action='update',
                entity_type='fees_cost',
                entity_id=fees_cost.id,
                details=f'تم تحديث تكاليف الرسوم للوثيقة رقم {fees_cost.document_id}',
                user_id=current_user.id
            )
            db.session.add(audit)
            
            # حفظ التغييرات
            db.session.commit()
            
            flash('تم تحديث تكاليف الرسوم بنجاح', 'success')
            return redirect(url_for('fees_costs.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث تكاليف الرسوم: {str(e)}', 'danger')
    
    return render_template('fees_costs/edit.html',
                          fees_cost=fees_cost,
                          today=datetime.now().date().strftime('%Y-%m-%d'))

@fees_costs_bp.route('/confirm-delete/<int:id>')
@login_required
def confirm_delete(id):
    """تأكيد حذف تكاليف رسوم"""
    fees_cost = FeesCost.query.get_or_404(id)
    return render_template('fees_costs/confirm_delete.html', fees_cost=fees_cost)

@fees_costs_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف تكاليف رسوم"""
    try:
        fees_cost = FeesCost.query.get_or_404(id)
        document_id = fees_cost.document_id
        
        # سجل التدقيق
        audit = SystemAudit(
            action='delete',
            entity_type='fees_cost',
            entity_id=id,
            details=f'تم حذف تكاليف الرسوم للوثيقة رقم {document_id}',
            user_id=current_user.id
        )
        db.session.add(audit)
        
        # حذف تكاليف الرسوم
        db.session.delete(fees_cost)
        db.session.commit()
        
        flash('تم حذف تكاليف الرسوم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف تكاليف الرسوم: {str(e)}', 'danger')
    
    return redirect(url_for('fees_costs.index'))

@fees_costs_bp.route('/document/<int:document_id>')
@login_required
def document_details(document_id):
    """عرض تفاصيل الوثيقة وتكاليف الرسوم المرتبطة بها"""
    document = Document.query.get_or_404(document_id)
    fees_costs = FeesCost.query.filter_by(document_id=document_id).all()
    
    return render_template('fees_costs/document_details.html',
                          document=document,
                          fees_costs=fees_costs,
                          now=datetime.now(),
                          timedelta=timedelta)

@fees_costs_bp.route('/expiring-documents')
@login_required
def expiring_documents():
    """عرض الوثائق التي تقترب من انتهاء صلاحيتها"""
    days = int(request.args.get('days', 90))
    
    today = datetime.now().date()
    expiry_date_limit = today + timedelta(days=days)
    
    documents = Document.query.filter(
        Document.expiry_date >= today,
        Document.expiry_date <= expiry_date_limit
    ).join(Employee).order_by(Document.expiry_date).all()
    
    return render_template('fees_costs/expiring_documents.html',
                          documents=documents,
                          days=days,
                          today=today,
                          timedelta=timedelta)

@fees_costs_bp.route('/expired-documents')
@login_required
def expired_documents():
    """عرض الوثائق المنتهية"""
    today = datetime.now().date()
    
    documents = Document.query.filter(Document.expiry_date < today).join(Employee).order_by(Document.expiry_date.desc()).all()
    
    return render_template('fees_costs/expired_documents.html',
                          documents=documents,
                          today=today)

@fees_costs_bp.route('/export-to-excel')
@login_required
def export_to_excel():
    """تصدير بيانات تكاليف الرسوم وبيانات الموظفين كملف إكسل"""
    try:
        # إنشاء بايت ستريم لتخزين ملف الإكسل
        output = BytesIO()
        
        # إنشاء مصنف إكسل جديد
        workbook = xlsxwriter.Workbook(output)
        
        # إضافة ورقة عمل
        worksheet = workbook.add_worksheet('تكاليف الرسوم')
        
        # تنسيق العناوين
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'bg_color': '#1e3a8a',
            'border': 1
        })
        
        # تنسيق الخلايا العادية
        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # تنسيق الأرقام
        number_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00'
        })
        
        # تنسيق التواريخ
        date_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'yyyy-mm-dd'
        })
        
        # تنسيق العناوين
        worksheet.right_to_left()  # تمكين الكتابة من اليمين إلى اليسار للغة العربية
        
        # العناوين
        headers = [
            'الرقم', 'اسم الموظف', 'الرقم الوظيفي', 'الجنسية', 'القسم',
            'نوع المستند', 'رقم المستند', 'تاريخ الإصدار', 'تاريخ الانتهاء',
            'رسوم الجوازات', 'رسوم مكتب العمل', 'رسوم التأمين', 'رسوم التأمينات',
            'نقل كفالة', 'إجمالي الرسوم', 'حالة السداد', 'تاريخ الاستحقاق', 'تاريخ السداد',
            'ملاحظات'
        ]
        
        # كتابة الترويسة
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)
            worksheet.set_column(col_num, col_num, 18)  # تعيين عرض العمود
        
        # الحصول على البيانات
        fees_costs = FeesCost.query.join(Document).join(Employee).order_by(FeesCost.id).all()
        
        # كتابة البيانات
        for row_num, fee in enumerate(fees_costs, 1):
            worksheet.write(row_num, 0, row_num, cell_format)
            worksheet.write(row_num, 1, fee.document.employee.name, cell_format)
            worksheet.write(row_num, 2, fee.document.employee.employee_id, cell_format)
            worksheet.write(row_num, 3, fee.document.employee.nationality, cell_format)
            if fee.document.employee.department:
                worksheet.write(row_num, 4, fee.document.employee.department.name, cell_format)
            else:
                worksheet.write(row_num, 4, "-", cell_format)
            worksheet.write(row_num, 5, fee.document_type, cell_format)
            worksheet.write(row_num, 6, fee.document.document_number, cell_format)
            worksheet.write(row_num, 7, fee.document.issue_date, date_format)
            worksheet.write(row_num, 8, fee.document.expiry_date, date_format)
            worksheet.write(row_num, 9, fee.passport_fee, number_format)
            worksheet.write(row_num, 10, fee.labor_office_fee, number_format)
            worksheet.write(row_num, 11, fee.insurance_fee, number_format)
            worksheet.write(row_num, 12, fee.social_insurance_fee, number_format)
            worksheet.write(row_num, 13, "نعم" if fee.transfer_sponsorship else "لا", cell_format)
            worksheet.write(row_num, 14, fee.total_fees, number_format)
            
            # ترجمة حالة السداد
            payment_status_text = {
                'pending': 'قيد الانتظار',
                'paid': 'تم السداد',
                'overdue': 'متأخر'
            }.get(fee.payment_status, fee.payment_status)
            
            worksheet.write(row_num, 15, payment_status_text, cell_format)
            worksheet.write(row_num, 16, fee.due_date, date_format)
            if fee.payment_date:
                worksheet.write(row_num, 17, fee.payment_date, date_format)
            else:
                worksheet.write(row_num, 17, "-", cell_format)
            worksheet.write(row_num, 18, fee.notes or "", cell_format)
        
        # إضافة صفحة للإحصائيات
        stats_sheet = workbook.add_worksheet('الإحصائيات')
        stats_sheet.right_to_left()
        
        # عناوين الإحصائيات
        stats_headers = ['البند', 'القيمة (ر.س)']
        for col_num, header in enumerate(stats_headers):
            stats_sheet.write(0, col_num, header, header_format)
            stats_sheet.set_column(col_num, col_num, 25)
        
        # حساب الإحصائيات
        total_passport_fees = db.session.query(func.sum(FeesCost.passport_fee)).scalar() or 0
        total_labor_fees = db.session.query(func.sum(FeesCost.labor_office_fee)).scalar() or 0
        total_insurance_fees = db.session.query(func.sum(FeesCost.insurance_fee)).scalar() or 0
        total_social_insurance_fees = db.session.query(func.sum(FeesCost.social_insurance_fee)).scalar() or 0
        total_fees = total_passport_fees + total_labor_fees + total_insurance_fees + total_social_insurance_fees
        
        # كتابة الإحصائيات
        stats_data = [
            ['إجمالي رسوم الجوازات', total_passport_fees],
            ['إجمالي رسوم مكتب العمل', total_labor_fees],
            ['إجمالي رسوم التأمين', total_insurance_fees],
            ['إجمالي رسوم التأمينات الاجتماعية', total_social_insurance_fees],
            ['إجمالي جميع الرسوم', total_fees]
        ]
        
        for row_num, (label, value) in enumerate(stats_data, 1):
            stats_sheet.write(row_num, 0, label, cell_format)
            stats_sheet.write(row_num, 1, value, number_format)
        
        # إغلاق المصنف
        workbook.close()
        
        # إعادة المؤشر إلى بداية الملف للقراءة
        output.seek(0)
        
        # تسجيل التدقيق
        audit = SystemAudit(
            action='export',
            entity_type='fees_costs',
            entity_id=0,
            details='تم تصدير بيانات تكاليف الرسوم وبيانات الموظفين كملف إكسل',
            user_id=current_user.id
        )
        db.session.add(audit)
        db.session.commit()
        
        # إرسال الملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            output,
            as_attachment=True,
            download_name=f'تكاليف_الرسوم_{timestamp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء تصدير البيانات: {str(e)}', 'danger')
        return redirect(url_for('fees_costs.index'))