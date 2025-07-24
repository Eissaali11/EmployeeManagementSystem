from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from models import SimCard, ImportedPhoneNumber, Employee, Department, db, UserRole
from datetime import datetime
import logging
from utils.audit_logger import log_activity
import pandas as pd
from flask import send_file
import os
import tempfile
from werkzeug.utils import secure_filename

sim_management_bp = Blueprint('sim_management', __name__)

@sim_management_bp.route('/')
@login_required
def index():
    """صفحة عرض جميع بطاقات SIM"""
    try:
        # فلاتر البحث
        department_filter = request.args.get('department_id', '')
        carrier_filter = request.args.get('carrier', '')
        status_filter = request.args.get('status', '')
        search_term = request.args.get('search', '')
        
        # استعلام أساسي
        query = SimCard.query
        
        # تطبيق فلاتر
        if search_term:
            query = query.filter(SimCard.phone_number.contains(search_term))
        
        if carrier_filter:
            query = query.filter(SimCard.carrier == carrier_filter)
            
        if status_filter == 'available':
            query = query.filter(SimCard.employee_id.is_(None))
        elif status_filter == 'assigned':
            query = query.filter(SimCard.employee_id.isnot(None))
        
        # ترتيب البيانات
        sim_cards = query.order_by(SimCard.id.desc()).all()
        
        # الحصول على قائمة الأقسام للفلترة
        departments = Department.query.order_by(Department.name).all()
        
        # إحصائيات
        stats = {
            'total_sims': SimCard.query.count(),
            'available_sims': SimCard.query.filter(SimCard.employee_id.is_(None)).count(),
            'assigned_sims': SimCard.query.filter(SimCard.employee_id.isnot(None)).count(),
            'stc_count': SimCard.query.filter(SimCard.carrier == 'STC').count(),
            'mobily_count': SimCard.query.filter(SimCard.carrier == 'موبايلي').count(),
            'zain_count': SimCard.query.filter(SimCard.carrier == 'زين').count(),
        }
        
        return render_template('sim_management/index.html', 
                             sim_cards=sim_cards, 
                             departments=departments,
                             stats=stats,
                             department_filter=department_filter,
                             carrier_filter=carrier_filter,
                             status_filter=status_filter,
                             search_term=search_term)
    
    except Exception as e:
        current_app.logger.error(f"Error in sim_management index: {str(e)}")
        flash('حدث خطأ أثناء تحميل البيانات', 'danger')
        return render_template('sim_management/index.html', 
                             sim_cards=[], 
                             departments=[],
                             stats={},
                             department_filter='',
                             carrier_filter='',
                             status_filter='',
                             search_term='')

@sim_management_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """إضافة رقم جديد"""
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            phone_number = request.form.get('phone_number', '').strip()
            carrier = request.form.get('carrier', '').strip()
            plan_type = request.form.get('plan_type', '').strip()
            monthly_cost = request.form.get('monthly_cost')
            description = request.form.get('description', '').strip()
            
            # التحقق من البيانات المطلوبة
            if not phone_number:
                flash('رقم الهاتف مطلوب', 'danger')
                return render_template('sim_management/create.html')
            
            if not carrier:
                flash('شركة الاتصالات مطلوبة', 'danger')
                return render_template('sim_management/create.html')
            
            # التحقق من عدم وجود الرقم مسبقاً
            existing_sim = ImportedPhoneNumber.query.filter_by(phone_number=phone_number).first()
            if existing_sim:
                flash('هذا الرقم موجود بالفعل في النظام', 'danger')
                return render_template('sim_management/create.html')
            
            # تحويل التكلفة الشهرية
            try:
                monthly_cost = float(monthly_cost) if monthly_cost else 0.0
            except ValueError:
                monthly_cost = 0.0
            
            # إنشاء رقم جديد
            new_sim = ImportedPhoneNumber(
                phone_number=phone_number,
                carrier=carrier,
                plan_type=plan_type if plan_type else None,
                monthly_cost=monthly_cost,
                description=description if description else None,
                import_date=datetime.now(),
                status='متاح'
            )
            
            db.session.add(new_sim)
            db.session.commit()
            
            # تسجيل العملية
            log_activity(
                action="create",
                entity_type="SIM",
                entity_id=new_sim.id,
                details=f"إضافة رقم SIM جديد: {phone_number} - الشركة: {carrier}, النوع: {plan_type or 'غير محدد'}, التكلفة: {monthly_cost} ريال"
            )
            
            flash(f'تم إضافة الرقم {phone_number} بنجاح', 'success')
            return redirect(url_for('sim_management.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating SIM card: {str(e)}")
            flash('حدث خطأ أثناء إضافة الرقم', 'danger')
            return render_template('sim_management/create.html')
    
    return render_template('sim_management/create.html')

@sim_management_bp.route('/edit/<int:sim_id>', methods=['GET', 'POST'])
@login_required
def edit(sim_id):
    """تعديل بيانات رقم"""
    sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
    
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            phone_number = request.form.get('phone_number', '').strip()
            carrier = request.form.get('carrier', '').strip()
            plan_type = request.form.get('plan_type', '').strip()
            monthly_cost = request.form.get('monthly_cost')
            description = request.form.get('description', '').strip()
            
            # التحقق من البيانات المطلوبة
            if not phone_number:
                flash('رقم الهاتف مطلوب', 'danger')
                return render_template('sim_management/edit.html', sim_card=sim_card)
            
            if not carrier:
                flash('شركة الاتصالات مطلوبة', 'danger')
                return render_template('sim_management/edit.html', sim_card=sim_card)
            
            # التحقق من عدم تكرار الرقم (باستثناء الرقم الحالي)
            existing_sim = ImportedPhoneNumber.query.filter(
                ImportedPhoneNumber.phone_number == phone_number,
                ImportedPhoneNumber.id != sim_id
            ).first()
            if existing_sim:
                flash('هذا الرقم موجود بالفعل في النظام', 'danger')
                return render_template('sim_management/edit.html', sim_card=sim_card)
            
            # تحويل التكلفة الشهرية
            try:
                monthly_cost = float(monthly_cost) if monthly_cost else 0.0
            except ValueError:
                monthly_cost = 0.0
            
            # حفظ البيانات القديمة للمقارنة
            old_data = {
                'phone_number': sim_card.phone_number,
                'carrier': sim_card.carrier,
                'plan_type': sim_card.plan_type,
                'monthly_cost': sim_card.monthly_cost
            }
            
            # تحديث البيانات
            sim_card.phone_number = phone_number
            sim_card.carrier = carrier
            sim_card.plan_type = plan_type if plan_type else None
            sim_card.monthly_cost = monthly_cost
            sim_card.description = description if description else None
            sim_card.updated_at = datetime.now()
            
            db.session.commit()
            
            # تسجيل العملية
            changes = []
            for key, old_value in old_data.items():
                new_value = getattr(sim_card, key)
                if old_value != new_value:
                    changes.append(f"{key}: {old_value} → {new_value}")
            
            if changes:
                log_activity(
                    action="update",
                    entity_type="SIM",
                    entity_id=sim_id,
                    details=f"تعديل رقم SIM: {phone_number} - التغييرات: {', '.join(changes)}"
                )
            
            flash(f'تم تحديث بيانات الرقم {phone_number} بنجاح', 'success')
            return redirect(url_for('sim_management.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating SIM card: {str(e)}")
            flash('حدث خطأ أثناء تحديث الرقم', 'danger')
            return render_template('sim_management/edit.html', sim_card=sim_card)
    
    return render_template('sim_management/edit.html', sim_card=sim_card)

@sim_management_bp.route('/delete/<int:sim_id>', methods=['POST'])
@login_required
def delete(sim_id):
    """حذف رقم"""
    try:
        sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
        
        # التحقق من عدم ربط الرقم بموظف
        if sim_card.employee_id:
            flash('لا يمكن حذف الرقم لأنه مربوط بموظف. يرجى فك الربط أولاً', 'danger')
            return redirect(url_for('sim_management.index'))
        
        # حفظ معلومات الرقم قبل الحذف
        phone_number = sim_card.phone_number
        carrier = sim_card.carrier
        
        db.session.delete(sim_card)
        db.session.commit()
        
        # تسجيل العملية
        log_activity(
            action="delete",
            entity_type="SIM",
            entity_id=sim_id,
            details=f"حذف رقم SIM: {phone_number} - الشركة: {carrier}"
        )
        
        flash(f'تم حذف الرقم {phone_number} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting SIM card: {str(e)}")
        flash('حدث خطأ أثناء حذف الرقم', 'danger')
    
    return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/assign/<int:sim_id>', methods=['POST'])
@login_required
def assign_to_employee(sim_id):
    """ربط رقم بموظف"""
    try:
        sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
        employee_id = request.form.get('employee_id')
        
        if not employee_id:
            flash('يرجى اختيار موظف', 'danger')
            return redirect(url_for('sim_management.index'))
        
        employee = Employee.query.get_or_404(employee_id)
        
        # التحقق من عدم ربط الرقم بموظف آخر
        if sim_card.employee_id:
            flash('هذا الرقم مربوط بموظف آخر بالفعل', 'danger')
            return redirect(url_for('sim_management.index'))
        
        # ربط الرقم بالموظف
        sim_card.employee_id = employee_id
        sim_card.assignment_date = datetime.now()
        sim_card.status = 'مربوط'
        
        db.session.commit()
        
        # تسجيل العملية
        log_activity(
            action="update",
            entity_type="SIM",
            entity_id=sim_id,
            details=f"ربط رقم SIM بموظف - الرقم: {sim_card.phone_number}, الموظف: {employee.name} ({employee.employee_id})"
        )
        
        flash(f'تم ربط الرقم {sim_card.phone_number} بالموظف {employee.name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning SIM card: {str(e)}")
        flash('حدث خطأ أثناء ربط الرقم', 'danger')
    
    return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/unassign/<int:sim_id>', methods=['POST'])
@login_required
def unassign_from_employee(sim_id):
    """فك ربط رقم من موظف"""
    try:
        sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
        
        if not sim_card.employee_id:
            flash('هذا الرقم غير مربوط بأي موظف', 'danger')
            return redirect(url_for('sim_management.index'))
        
        # الحصول على معلومات الموظف قبل فك الربط
        employee = Employee.query.get(sim_card.employee_id)
        employee_name = employee.name if employee else "غير معروف"
        employee_id_num = employee.employee_id if employee else "غير معروف"
        
        # فك الربط
        sim_card.employee_id = None
        sim_card.assignment_date = None
        sim_card.status = 'متاح'
        
        db.session.commit()
        
        # تسجيل العملية
        log_activity(
            action="update",
            entity_type="SIM",
            entity_id=sim_id,
            details=f"فك ربط رقم SIM من موظف - الرقم: {sim_card.phone_number}, الموظف السابق: {employee_name} ({employee_id_num})"
        )
        
        flash(f'تم فك ربط الرقم {sim_card.phone_number} من الموظف {employee_name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unassigning SIM card: {str(e)}")
        flash('حدث خطأ أثناء فك ربط الرقم', 'danger')
    
    return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/api/available', methods=['GET'])
@login_required
def api_available_sims():
    """API للحصول على الأرقام المتاحة"""
    try:
        available_sims = ImportedPhoneNumber.query.filter(
            ImportedPhoneNumber.employee_id.is_(None)
        ).order_by(ImportedPhoneNumber.phone_number).all()
        
        sims_data = []
        for sim in available_sims:
            sims_data.append({
                'id': sim.id,
                'phone_number': sim.phone_number,
                'carrier': sim.carrier,
                'plan_type': sim.plan_type,
                'monthly_cost': sim.monthly_cost,
                'status_class': 'success'
            })
        
        return jsonify({
            'success': True,
            'sims': sims_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting available SIMs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء جلب البيانات'
        }), 500

@sim_management_bp.route('/export-excel')
@login_required
def export_excel():
    """تصدير أرقام SIM إلى ملف Excel"""
    try:
        # جلب جميع أرقام SIM مع معلومات الموظفين
        sim_cards = db.session.query(SimCard, Employee).outerjoin(
            Employee, SimCard.employee_id == Employee.id
        ).order_by(SimCard.id).all()
        
        # إعداد البيانات للتصدير
        data = []
        for sim_card, employee in sim_cards:
            data.append({
                'رقم الهاتف': sim_card.phone_number,
                'شركة الاتصالات': sim_card.carrier,
                'نوع الخطة': sim_card.plan_type or '',
                'التكلفة الشهرية': sim_card.monthly_cost or 0,
                'الحالة': 'مربوط' if sim_card.employee_id else 'متاح',
                'اسم الموظف': employee.name if employee else '',
                'رقم الموظف': employee.employee_id if employee else '',
                'القسم': ', '.join([dept.name for dept in employee.departments]) if employee and employee.departments else '',
                'تاريخ الاستيراد': sim_card.import_date.strftime('%Y-%m-%d') if sim_card.import_date else '',
                'تاريخ الربط': sim_card.assignment_date.strftime('%Y-%m-%d') if sim_card.assignment_date else '',
                'الوصف': sim_card.description or ''
            })
        
        # إنشاء DataFrame
        df = pd.DataFrame(data)
        
        # إنشاء ملف مؤقت
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_filename = temp_file.name
        temp_file.close()
        
        # كتابة البيانات إلى Excel
        with pd.ExcelWriter(temp_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='أرقام SIM', index=False, encoding='utf-8')
            
            # تنسيق الورقة
            worksheet = writer.sheets['أرقام SIM']
            
            # تعديل عرض الأعمدة
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # تسجيل العملية
        log_activity(
            action="export",
            entity_type="SIM",
            details=f"تصدير {len(data)} رقم SIM إلى Excel"
        )
        
        # إرسال الملف
        return send_file(
            temp_filename,
            as_attachment=True,
            download_name=f'sim_cards_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exporting SIM cards: {str(e)}")
        flash('حدث خطأ أثناء تصدير البيانات', 'danger')
        return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/import-excel', methods=['GET', 'POST'])
@login_required
def import_excel():
    """استيراد أرقام SIM من ملف Excel"""
    if request.method == 'POST':
        try:
            # التحقق من وجود الملف
            if 'excel_file' not in request.files:
                flash('يرجى اختيار ملف Excel', 'danger')
                return render_template('sim_management/import_excel.html')
            
            file = request.files['excel_file']
            if file.filename == '':
                flash('يرجى اختيار ملف', 'danger')
                return render_template('sim_management/import_excel.html')
            
            # التحقق من نوع الملف
            if not file.filename.lower().endswith(('.xlsx', '.xls')):
                flash('يرجى اختيار ملف Excel صحيح (.xlsx أو .xls)', 'danger')
                return render_template('sim_management/import_excel.html')
            
            # قراءة الملف
            df = pd.read_excel(file)
            
            # التحقق من وجود الأعمدة المطلوبة
            required_columns = ['رقم الهاتف', 'شركة الاتصالات']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                flash(f'الأعمدة التالية مفقودة: {", ".join(missing_columns)}', 'danger')
                return render_template('sim_management/import_excel.html')
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    phone_number = str(row['رقم الهاتف']).strip()
                    carrier = str(row['شركة الاتصالات']).strip()
                    
                    # تخطي الصفوف الفارغة
                    if not phone_number or phone_number == 'nan':
                        continue
                    
                    # التحقق من وجود الرقم
                    existing_sim = SimCard.query.filter_by(phone_number=phone_number).first()
                    if existing_sim:
                        skipped_count += 1
                        continue
                    
                    # إنشاء رقم جديد
                    new_sim = SimCard(
                        phone_number=phone_number,
                        carrier=carrier,
                        plan_type=str(row.get('نوع الخطة', '')).strip() if pd.notna(row.get('نوع الخطة')) else None,
                        monthly_cost=float(row.get('التكلفة الشهرية', 0)) if pd.notna(row.get('التكلفة الشهرية')) else 0.0,
                        description=str(row.get('الوصف', '')).strip() if pd.notna(row.get('الوصف')) else None,
                        import_date=datetime.now(),
                        status='متاح'
                    )
                    
                    db.session.add(new_sim)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"صف {index + 2}: {str(e)}")
                    continue
            
            # حفظ التغييرات
            db.session.commit()
            
            # تسجيل العملية
            log_activity(
                action="import",
                entity_type="SIM",
                details=f"استيراد {imported_count} رقم SIM من Excel، تم تخطي {skipped_count} رقم موجود مسبقاً"
            )
            
            # إعداد رسالة النتيجة
            if imported_count > 0:
                flash(f'تم استيراد {imported_count} رقم بنجاح', 'success')
            if skipped_count > 0:
                flash(f'تم تخطي {skipped_count} رقم موجود مسبقاً', 'info')
            if errors:
                flash(f'حدثت أخطاء في {len(errors)} صف', 'warning')
            
            return redirect(url_for('sim_management.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error importing SIM cards: {str(e)}")
            flash('حدث خطأ أثناء استيراد البيانات', 'danger')
            return render_template('sim_management/import_excel.html')
    
    return render_template('sim_management/import_excel.html')