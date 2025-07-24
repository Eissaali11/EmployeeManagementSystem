from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response
from sqlalchemy import func, and_, or_
from models import db, MobileDevice, Employee, Department
from datetime import datetime
import io
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
# from utils.audit_logger import audit_log

device_management_bp = Blueprint('device_management', __name__)

@device_management_bp.route('/')
def index():
    """عرض صفحة قائمة الأجهزة المحمولة مع الفلاتر والإحصائيات"""
    try:
        # استلام الفلاتر من الطلب
        department_filter = request.args.get('department', '')
        brand_filter = request.args.get('brand', '')
        status_filter = request.args.get('status', '')
        search_term = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        
        # بناء الاستعلام
        query = MobileDevice.query
        
        # تطبيق الفلاتر
        if department_filter:
            query = query.join(Employee).join(Employee.departments).filter(Department.id == department_filter)
        
        if brand_filter:
            query = query.filter(MobileDevice.device_brand.like(f'%{brand_filter}%'))
        
        if status_filter:
            if status_filter == 'available':
                query = query.filter(MobileDevice.employee_id.is_(None))
            elif status_filter == 'assigned':
                query = query.filter(MobileDevice.employee_id.isnot(None))
            elif status_filter == 'no_phone':
                query = query.filter(or_(MobileDevice.phone_number.is_(None), MobileDevice.phone_number == ''))
            elif status_filter == 'with_phone':
                query = query.filter(and_(MobileDevice.phone_number.isnot(None), MobileDevice.phone_number != ''))
        
        if search_term:
            query = query.filter(
                or_(
                    MobileDevice.imei.like(f'%{search_term}%'),
                    MobileDevice.phone_number.like(f'%{search_term}%')
                )
            )
        
        # ترتيب وصفحة
        devices = query.order_by(MobileDevice.created_at.desc()).all()
        
        # حساب الإحصائيات
        total_devices = MobileDevice.query.count()
        available_devices = MobileDevice.query.filter(MobileDevice.employee_id.is_(None)).count()
        assigned_devices = MobileDevice.query.filter(MobileDevice.employee_id.isnot(None)).count()
        
        # إحصائيات الأرقام
        devices_with_phone = MobileDevice.query.filter(and_(MobileDevice.phone_number.isnot(None), MobileDevice.phone_number != '')).count()
        devices_without_phone = MobileDevice.query.filter(or_(MobileDevice.phone_number.is_(None), MobileDevice.phone_number == '')).count()
        
        # إحصائيات العلامات التجارية
        iphone_count = MobileDevice.query.filter(MobileDevice.device_brand.like('%iPhone%')).count()
        samsung_count = MobileDevice.query.filter(MobileDevice.device_brand.like('%Samsung%')).count()
        
        stats = {
            'total_devices': total_devices,
            'available_devices': available_devices,
            'assigned_devices': assigned_devices,
            'devices_with_phone': devices_with_phone,
            'devices_without_phone': devices_without_phone,
            'iphone_count': iphone_count,
            'samsung_count': samsung_count
        }
        
        # جلب قائمة الأقسام والموظفين
        departments = Department.query.all()
        employees = Employee.query.filter_by(status='نشط').all()
        
        return render_template('device_management/index.html',
                             devices=devices,
                             stats=stats,
                             departments=departments,
                             employees=employees,
                             department_filter=department_filter,
                             brand_filter=brand_filter,
                             status_filter=status_filter,
                             search_term=search_term)
    
    except Exception as e:
        flash(f'حدث خطأ في تحميل البيانات: {str(e)}', 'error')
        return render_template('device_management/index.html', devices=[], stats={}, departments=[])

@device_management_bp.route('/create', methods=['GET', 'POST'])
def create():
    """إضافة جهاز محمول جديد"""
    if request.method == 'POST':
        try:
            # استلام البيانات من النموذج
            imei = request.form.get('imei')
            brand = request.form.get('brand')
            model = request.form.get('model')
            phone_number = request.form.get('phone_number')
            serial_number = request.form.get('serial_number')
            purchase_date = request.form.get('purchase_date')
            warranty_expiry = request.form.get('warranty_expiry')
            description = request.form.get('description')
            
            # التحقق من صحة IMEI
            if not imei or len(imei) != 15:
                flash('رقم IMEI يجب أن يكون 15 رقم بالضبط', 'error')
                return render_template('device_management/create.html')
            
            # التحقق من عدم تكرار IMEI
            existing_device = MobileDevice.query.filter_by(imei=imei).first()
            if existing_device:
                flash('رقم IMEI موجود مسبقاً في النظام', 'error')
                return render_template('device_management/create.html')
            
            # إنشاء الجهاز الجديد
            device = MobileDevice(
                imei=imei,
                device_brand=brand,
                device_model=model,
                phone_number=phone_number or None,
                notes=description
            )
            
            # إضافة التواريخ إذا تم إدخالها
            if purchase_date:
                device.assigned_date = datetime.strptime(purchase_date, '%Y-%m-%d')
            
            db.session.add(device)
            db.session.commit()
            
            # تسجيل العملية في السجل
            # audit_log('device_created', f'تم إضافة جهاز جديد: {brand} {model} - IMEI: {imei}')
            
            flash('تم إضافة الجهاز بنجاح', 'success')
            return redirect(url_for('device_management.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ في إضافة الجهاز: {str(e)}', 'error')
    
    return render_template('device_management/create.html')

@device_management_bp.route('/edit/<int:device_id>', methods=['GET', 'POST'])
def edit(device_id):
    """تعديل بيانات جهاز محمول"""
    device = MobileDevice.query.get_or_404(device_id)
    
    if request.method == 'POST':
        try:
            # التحقق من IMEI الجديد
            new_imei = request.form.get('imei')
            if not new_imei or len(new_imei) != 15:
                flash('رقم IMEI يجب أن يكون 15 رقم بالضبط', 'error')
                return render_template('device_management/edit.html', device=device)
            
            # التحقق من عدم تكرار IMEI
            if new_imei != device.imei:
                existing_device = MobileDevice.query.filter_by(imei=new_imei).first()
                if existing_device:
                    flash('رقم IMEI موجود مسبقاً في النظام', 'error')
                    return render_template('device_management/edit.html', device=device)
            
            # تحديث البيانات
            device.imei = new_imei
            device.device_brand = request.form.get('brand')
            device.device_model = request.form.get('model')
            device.phone_number = request.form.get('phone_number') or None
            device.notes = request.form.get('description')
            device.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # تسجيل العملية
            # audit_log('device_updated', f'تم تحديث الجهاز: {device.device_brand} {device.device_model} - IMEI: {device.imei}')
            
            flash('تم تحديث بيانات الجهاز بنجاح', 'success')
            return redirect(url_for('device_management.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ في تحديث الجهاز: {str(e)}', 'error')
    
    return render_template('device_management/edit.html', device=device)

@device_management_bp.route('/delete/<int:device_id>', methods=['POST'])
def delete(device_id):
    """حذف جهاز محمول"""
    try:
        device = MobileDevice.query.get_or_404(device_id)
        
        # التحقق من أن الجهاز غير مربوط بموظف
        if device.employee_id:
            flash('لا يمكن حذف جهاز مربوط بموظف. يرجى فك الربط أولاً', 'error')
            return redirect(url_for('device_management.index'))
        
        device_info = f'{device.device_brand} {device.device_model} - IMEI: {device.imei}'
        
        db.session.delete(device)
        db.session.commit()
        
        # تسجيل العملية
        # audit_log('device_deleted', f'تم حذف الجهاز: {device_info}')
        
        flash('تم حذف الجهاز بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ في حذف الجهاز: {str(e)}', 'error')
    
    return redirect(url_for('device_management.index'))

@device_management_bp.route('/assign/<int:device_id>', methods=['POST'])
def assign_to_employee(device_id):
    """ربط الجهاز بموظف"""
    try:
        device = MobileDevice.query.get_or_404(device_id)
        employee_id = request.form.get('employee_id')
        
        if not employee_id:
            flash('يرجى اختيار موظف', 'error')
            return redirect(url_for('device_management.index'))
        
        employee = Employee.query.get_or_404(employee_id)
        
        # التحقق من أن الجهاز متاح
        if device.employee_id:
            flash('الجهاز مربوط بموظف آخر بالفعل', 'error')
            return redirect(url_for('device_management.index'))
        
        # ربط الجهاز
        device.employee_id = employee_id
        device.status = 'مرتبط'
        device.assigned_date = datetime.utcnow()
        device.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل العملية
        # audit_log('device_assigned', f'تم ربط الجهاز {device.device_brand} {device.device_model} بالموظف {employee.name}')
        
        flash(f'تم ربط الجهاز بالموظف {employee.name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ في ربط الجهاز: {str(e)}', 'error')
    
    return redirect(url_for('device_management.index'))

@device_management_bp.route('/unassign/<int:device_id>', methods=['POST'])
def unassign_from_employee(device_id):
    """فك ربط الجهاز من الموظف"""
    try:
        device = MobileDevice.query.get_or_404(device_id)
        
        if not device.employee_id:
            flash('الجهاز غير مربوط بأي موظف', 'error')
            return redirect(url_for('device_management.index'))
        
        employee_name = device.employee.name if device.employee else 'غير معروف'
        
        # فك الربط
        device.employee_id = None
        device.status = 'متاح'
        device.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل العملية
        # audit_log('device_unassigned', f'تم فك ربط الجهاز {device.device_brand} {device.device_model} من الموظف {employee_name}')
        
        flash(f'تم فك ربط الجهاز من الموظف {employee_name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ في فك ربط الجهاز: {str(e)}', 'error')
    
    return redirect(url_for('device_management.index'))

@device_management_bp.route('/export-excel')
def export_excel():
    """تصدير بيانات الأجهزة إلى Excel"""
    try:
        # إنشاء workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "الأجهزة المحمولة"
        
        # إعداد الرؤوس
        headers = ['IMEI', 'العلامة التجارية', 'الموديل', 'رقم الهاتف', 'الحالة', 'الموظف المرتبط', 'تاريخ الربط', 'ملاحظات']
        ws.append(headers)
        
        # تنسيق الرؤوس
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
        
        # جلب البيانات وإضافتها
        devices = MobileDevice.query.all()
        for device in devices:
            employee_name = device.employee.name if device.employee else ''
            assigned_date = device.assigned_date.strftime('%Y-%m-%d') if device.assigned_date else ''
            
            row_data = [
                device.imei,
                device.device_brand or '',
                device.device_model or '',
                device.phone_number or '',
                device.status,
                employee_name,
                assigned_date,
                device.notes or ''
            ]
            ws.append(row_data)
        
        # ضبط عرض الأعمدة
        column_widths = [20, 15, 20, 15, 12, 20, 15, 30]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = width
        
        # حفظ في memory
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # تسجيل العملية
        # audit_log('devices_exported', f'تم تصدير {len(devices)} جهاز إلى Excel')
        
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename=mobile_devices.xlsx'}
        )
        
    except Exception as e:
        flash(f'حدث خطأ في تصدير البيانات: {str(e)}', 'error')
        return redirect(url_for('device_management.index'))

@device_management_bp.route('/devices-only')
def devices_only():
    """صفحة الأجهزة بدون أرقام هاتف فقط"""
    try:
        # جلب جميع الأجهزة بدون أرقام هاتف
        devices = MobileDevice.query.filter(
            or_(MobileDevice.phone_number.is_(None), MobileDevice.phone_number == '')
        ).order_by(MobileDevice.created_at.desc()).all()
        
        # جلب الأقسام للفلاتر
        departments = Department.query.order_by(Department.name).all()
        
        # إحصائيات خاصة بالأجهزة بدون أرقام
        total_devices_only = len(devices)
        available_devices_only = len([d for d in devices if d.employee_id is None])
        assigned_devices_only = len([d for d in devices if d.employee_id is not None])
        
        # إحصائيات العلامات التجارية للأجهزة بدون أرقام
        iphone_count = len([d for d in devices if d.device_brand and 'iPhone' in d.device_brand])
        samsung_count = len([d for d in devices if d.device_brand and 'Samsung' in d.device_brand])
        
        stats = {
            'total_devices': total_devices_only,
            'available_devices': available_devices_only,
            'assigned_devices': assigned_devices_only,
            'iphone_count': iphone_count,
            'samsung_count': samsung_count
        }
        
        return render_template('device_management/devices_only.html',
                             devices=devices,
                             departments=departments,
                             stats=stats)
                             
    except Exception as e:
        print(f"Error in devices_only: {str(e)}")
        flash('حدث خطأ في تحميل البيانات', 'error')
        return redirect(url_for('device_management.index'))

@device_management_bp.route('/import-excel', methods=['GET', 'POST'])
def import_excel():
    """استيراد الأجهزة من ملف Excel"""
    if request.method == 'POST':
        try:
            if 'excel_file' not in request.files:
                flash('لم يتم اختيار ملف', 'error')
                return render_template('device_management/import_excel.html')
            
            file = request.files['excel_file']
            if file.filename == '':
                flash('لم يتم اختيار ملف', 'error')
                return render_template('device_management/import_excel.html')
            
            # قراءة الملف
            df = pd.read_excel(file)
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # استخراج البيانات
                    imei = str(row.get('IMEI', '')).strip()
                    brand = str(row.get('العلامة التجارية', '')).strip()
                    model = str(row.get('الموديل', '')).strip()
                    phone_number = str(row.get('رقم الهاتف', '')).strip()
                    description = str(row.get('الوصف', '')).strip()
                    
                    # التحقق من البيانات الأساسية
                    if not imei or not brand or not model:
                        errors.append(f'الصف {index + 2}: IMEI أو العلامة التجارية أو الموديل مفقود')
                        continue
                    
                    if len(imei) != 15:
                        errors.append(f'الصف {index + 2}: رقم IMEI يجب أن يكون 15 رقم')
                        continue
                    
                    # التحقق من عدم وجود الجهاز
                    existing_device = MobileDevice.query.filter_by(imei=imei).first()
                    if existing_device:
                        skipped_count += 1
                        continue
                    
                    # إنشاء الجهاز الجديد
                    device = MobileDevice(
                        imei=imei,
                        device_brand=brand,
                        device_model=model,
                        phone_number=phone_number if phone_number and phone_number != 'nan' else None,
                        notes=description if description and description != 'nan' else None
                    )
                    
                    db.session.add(device)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f'الصف {index + 2}: {str(e)}')
            
            if imported_count > 0:
                db.session.commit()
                # audit_log('devices_imported', f'تم استيراد {imported_count} جهاز من Excel')
            
            # إعداد رسائل النتائج
            messages = []
            if imported_count > 0:
                messages.append(f'تم استيراد {imported_count} جهاز بنجاح')
            if skipped_count > 0:
                messages.append(f'تم تخطي {skipped_count} جهاز موجود مسبقاً')
            if errors:
                messages.append(f'فشل في استيراد {len(errors)} جهاز')
                for error in errors[:5]:  # عرض أول 5 أخطاء فقط
                    messages.append(f'- {error}')
            
            if imported_count > 0:
                flash('\n'.join(messages), 'success')
            else:
                flash('\n'.join(messages), 'warning')
            
            return redirect(url_for('device_management.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ في معالجة الملف: {str(e)}', 'error')
    
    return render_template('device_management/import_excel.html')