from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from PIL import Image
from models import VehicleExternalSafetyCheck, VehicleSafetyImage, Vehicle, Employee, User, UserRole
from app import db
from utils.audit_logger import log_audit
from flask_login import current_user

external_safety_bp = Blueprint('external_safety', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, max_size=1200, quality=85):
    """ضغط الصورة لتقليل حجمها"""
    try:
        with Image.open(image_path) as img:
            # تحويل RGBA إلى RGB إذا لزم الأمر
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # تغيير حجم الصورة إذا كانت أكبر من الحد المسموح
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # حفظ الصورة المضغوطة
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        current_app.logger.error(f"خطأ في ضغط الصورة: {str(e)}")
        return False

@external_safety_bp.route('/external-safety-check/<int:vehicle_id>')
def external_safety_check_form(vehicle_id):
    """عرض نموذج فحص السلامة الخارجي للسيارة"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template('external_safety_check.html', vehicle=vehicle)

@external_safety_bp.route('/share-links')
def share_links():
    """صفحة مشاركة روابط النماذج الخارجية لجميع السيارات مع الفلاتر"""
    # الحصول على معاملات الفلترة من الطلب
    status_filter = request.args.get('status', '')
    make_filter = request.args.get('make', '')
    search_plate = request.args.get('search_plate', '')
    project_filter = request.args.get('project', '')
    
    # قاعدة الاستعلام الأساسية
    query = Vehicle.query
    
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
    
    # قائمة حالات السيارات
    statuses = ['available', 'rented', 'in_project', 'in_workshop', 'accident']
    
    return render_template('external_safety_share_links.html', 
                           vehicles=vehicles,
                           status_filter=status_filter,
                           make_filter=make_filter,
                           search_plate=search_plate,
                           project_filter=project_filter,
                           makes=makes,
                           projects=projects,
                           statuses=statuses)

@external_safety_bp.route('/external-safety-check', methods=['POST'])
def submit_external_safety_check():
    """إرسال طلب فحص السلامة الخارجي"""
    try:
        # التحقق من البيانات المطلوبة
        required_fields = ['vehicle_id', 'driver_national_id', 'driver_name', 'driver_department', 'driver_city']
        for field in required_fields:
            if not request.form.get(field):
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من وجود السيارة
        vehicle = Vehicle.query.get(request.form.get('vehicle_id'))
        if not vehicle:
            return jsonify({'error': 'السيارة غير موجودة'}), 404
        
        # إنشاء سجل فحص السلامة
        safety_check = VehicleExternalSafetyCheck(
            vehicle_id=vehicle.id,
            driver_name=request.form.get('driver_name'),
            driver_national_id=request.form.get('driver_national_id'),
            driver_department=request.form.get('driver_department'),
            driver_city=request.form.get('driver_city'),
            vehicle_plate_number=request.form.get('vehicle_plate_number'),
            vehicle_make_model=request.form.get('vehicle_make_model'),
            current_delegate=request.form.get('current_delegate'),
            notes=request.form.get('notes'),
            inspection_date=datetime.now()
        )
        
        db.session.add(safety_check)
        db.session.flush()  # للحصول على ID
        
        # معالجة الصور المرفوعة
        uploaded_files = request.files.getlist('safety_images')
        descriptions = request.form.getlist('image_descriptions')
        
        if uploaded_files:
            # إنشاء مجلد للصور
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'safety_checks')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            for i, file in enumerate(uploaded_files):
                if file and file.filename and allowed_file(file.filename):
                    # إنشاء اسم ملف آمن
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"safety_{safety_check.id}_{uuid.uuid4().hex}.{file_extension}"
                    file_path = os.path.join(upload_folder, filename)
                    
                    # حفظ الملف
                    file.save(file_path)
                    
                    # ضغط الصورة
                    compress_image(file_path)
                    
                    # حفظ معلومات الصورة في قاعدة البيانات
                    description = descriptions[i] if i < len(descriptions) else None
                    
                    safety_image = VehicleSafetyImage(
                        safety_check_id=safety_check.id,
                        image_path=f'uploads/safety_checks/{filename}',
                        image_description=description
                    )
                    
                    db.session.add(safety_image)
        
        # حفظ جميع التغييرات
        db.session.commit()
        
        # تسجيل العملية في سجل المراجعة
        log_audit(
            user_id=current_user.id if current_user.is_authenticated else None,
            action='create',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم إنشاء طلب فحص السلامة الخارجي للسيارة {vehicle.plate_number} بواسطة {safety_check.driver_name}'
        )
        
        return jsonify({'success': True, 'message': 'تم إرسال طلب فحص السلامة بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في إرسال طلب فحص السلامة: {str(e)}")
        return jsonify({'error': 'حدث خطأ في إرسال الطلب'}), 500

@external_safety_bp.route('/api/verify-employee/<national_id>')
def verify_employee(national_id):
    """التحقق من الموظف بواسطة رقم الهوية"""
    try:
        # البحث عن الموظف بواسطة رقم الهوية
        employee = Employee.query.filter_by(national_id=national_id).first()
        
        if not employee:
            return jsonify({'success': False, 'message': 'الموظف غير موجود'}), 404
        
        # الحصول على أسماء الأقسام
        department_names = [dept.name for dept in employee.departments] if employee.departments else []
        
        return jsonify({
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'department': ', '.join(department_names) if department_names else 'غير محدد',
                'city': employee.city if hasattr(employee, 'city') else 'الرياض',
                'national_id': employee.national_id
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"خطأ في التحقق من الموظف: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في التحقق من الموظف'}), 500

@external_safety_bp.route('/external-safety-check/success')
def external_safety_success():
    """صفحة نجاح إرسال طلب فحص السلامة"""
    return render_template('external_safety_success.html')

@external_safety_bp.route('/admin/external-safety-checks')
def admin_external_safety_checks():
    """عرض جميع طلبات فحص السلامة للإدارة"""
    # التحقق من صلاحيات الإدارة
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # جلب جميع طلبات فحص السلامة
    safety_checks = VehicleExternalSafetyCheck.query.order_by(
        VehicleExternalSafetyCheck.created_at.desc()
    ).all()
    
    return render_template('admin_external_safety_checks.html', safety_checks=safety_checks)

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>')
def admin_view_safety_check(check_id):
    """عرض تفاصيل طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
    return render_template('admin_view_safety_check.html', safety_check=safety_check)

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/approve', methods=['POST'])
def approve_safety_check(check_id):
    """اعتماد طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'غير مصرح لك'}), 403
    
    try:
        safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
        
        safety_check.approval_status = 'approved'
        safety_check.approved_by = current_user.id
        safety_check.approved_at = datetime.now()
        
        db.session.commit()
        
        # تسجيل العملية
        log_audit(
            user_id=current_user.id,
            action='approve',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم اعتماد طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number}'
        )
        
        flash('تم اعتماد طلب فحص السلامة بنجاح', 'success')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في اعتماد طلب فحص السلامة: {str(e)}")
        flash('حدث خطأ في اعتماد الطلب', 'error')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/reject', methods=['POST'])
def reject_safety_check(check_id):
    """رفض طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'غير مصرح لك'}), 403
    
    try:
        safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
        
        safety_check.approval_status = 'rejected'
        safety_check.approved_by = current_user.id
        safety_check.approved_at = datetime.now()
        safety_check.rejection_reason = request.form.get('rejection_reason', '')
        
        db.session.commit()
        
        # تسجيل العملية
        log_audit(
            user_id=current_user.id,
            action='reject',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم رفض طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number}. السبب: {safety_check.rejection_reason}'
        )
        
        flash('تم رفض طلب فحص السلامة', 'success')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في رفض طلب فحص السلامة: {str(e)}")
        flash('حدث خطأ في رفض الطلب', 'error')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/edit', methods=['GET', 'POST'])
def edit_safety_check(check_id):
    """تعديل طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
    
    if request.method == 'POST':
        try:
            # تحديث البيانات
            safety_check.current_delegate = request.form.get('current_delegate', '')
            safety_check.inspection_date = datetime.fromisoformat(request.form.get('inspection_date'))
            safety_check.driver_name = request.form.get('driver_name', '')
            safety_check.driver_national_id = request.form.get('driver_national_id', '')
            safety_check.driver_department = request.form.get('driver_department', '')
            safety_check.driver_city = request.form.get('driver_city', '')
            safety_check.notes = request.form.get('notes', '')
            
            # تحديث تاريخ التعديل
            safety_check.updated_at = datetime.now()
            
            db.session.commit()
            
            # تسجيل العملية
            log_audit(
                user_id=current_user.id,
                action='update',
                entity_type='VehicleExternalSafetyCheck',
                entity_id=safety_check.id,
                details=f'تم تحديث طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number}'
            )
            
            flash('تم تحديث طلب فحص السلامة بنجاح', 'success')
            return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"خطأ في تحديث طلب فحص السلامة: {str(e)}")
            flash('حدث خطأ في تحديث الطلب', 'error')
    
    return render_template('admin_edit_safety_check.html', safety_check=safety_check)

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/delete', methods=['POST'])
def delete_safety_check(check_id):
    """حذف طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'غير مصرح لك'}), 403
    
    try:
        safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
        
        # حذف الصور المرفقة
        for image in safety_check.safety_images:
            try:
                if os.path.exists(image.image_path):
                    os.remove(image.image_path)
            except Exception as e:
                current_app.logger.error(f"خطأ في حذف الصورة: {str(e)}")
        
        # تسجيل العملية قبل الحذف
        log_audit(
            user_id=current_user.id,
            action='delete',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم حذف طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number}'
        )
        
        db.session.delete(safety_check)
        db.session.commit()
        
        flash('تم حذف طلب فحص السلامة بنجاح', 'success')
        return redirect(url_for('external_safety.admin_external_safety_checks'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في حذف طلب فحص السلامة: {str(e)}")
        flash('حدث خطأ في حذف الطلب', 'error')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/pdf')
def export_safety_check_pdf(check_id):
    """تصدير طلب فحص السلامة كملف PDF"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    try:
        safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
        
        # استيراد مكتبات ReportLab المطلوبة
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, mm, cm
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        import io
        
        # إنشاء buffer للـ PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
            title=f"تقرير فحص السلامة رقم {safety_check.id}"
        )
        
        # تسجيل خط عربي
        try:
            pdfmetrics.registerFont(TTFont('Arabic', 'Cairo.ttf'))
            arabic_font = 'Arabic'
        except:
            try:
                pdfmetrics.registerFont(TTFont('Arabic', 'static/fonts/NotoSansArabic-Regular.ttf'))
                arabic_font = 'Arabic'
            except:
                arabic_font = 'Helvetica'
        
        # تعريف الأنماط
        styles = getSampleStyleSheet()
        
        # نمط العنوان الرئيسي
        title_style = ParagraphStyle(
            'CustomTitle',
            fontName=arabic_font,
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            borderWidth=2,
            borderColor=colors.HexColor('#3498DB'),
            borderPadding=10,
            backColor=colors.HexColor('#ECF0F1')
        )
        
        # نمط العناوين الفرعية
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            fontName=arabic_font,
            fontSize=14,
            spaceAfter=15,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#2C3E50'),
            borderWidth=1,
            borderColor=colors.HexColor('#BDC3C7'),
            borderPadding=5,
            backColor=colors.HexColor('#F8F9FA')
        )
        
        # نمط النص العادي
        normal_style = ParagraphStyle(
            'CustomNormal',
            fontName=arabic_font,
            fontSize=11,
            spaceAfter=8,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#34495E')
        )
        
        # نمط وصف الصور
        image_desc_style = ParagraphStyle(
            'ImageDesc',
            fontName=arabic_font,
            fontSize=10,
            spaceAfter=5,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7F8C8D'),
            backColor=colors.HexColor('#F8F9FA')
        )
        
        # محتوى الـ PDF
        story = []
        
        # العنوان الرئيسي مع شعار
        story.append(Paragraph(f"تقرير فحص السلامة الخارجي رقم {safety_check.id}", title_style))
        story.append(Spacer(1, 20))
        
        # معلومات السيارة
        story.append(Paragraph("🚗 معلومات السيارة", subtitle_style))
        
        vehicle_data = [
            ['البيان', 'القيمة'],
            ['رقم اللوحة', safety_check.vehicle_plate_number],
            ['نوع السيارة', safety_check.vehicle_make_model],
            ['المفوض الحالي', safety_check.current_delegate or 'غير محدد'],
            ['تاريخ الفحص', safety_check.inspection_date.strftime('%Y-%m-%d %H:%M')]
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[6*cm, 8*cm])
        vehicle_table.setStyle(TableStyle([
            # نمط الرأس
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), arabic_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # نمط الصفوف
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))
        
        story.append(vehicle_table)
        story.append(Spacer(1, 20))
        
        # معلومات السائق
        story.append(Paragraph("👤 معلومات السائق", subtitle_style))
        
        driver_data = [
            ['البيان', 'القيمة'],
            ['اسم السائق', safety_check.driver_name],
            ['رقم الهوية', safety_check.driver_national_id],
            ['القسم', safety_check.driver_department],
            ['المدينة', safety_check.driver_city]
        ]
        
        driver_table = Table(driver_data, colWidths=[6*cm, 8*cm])
        driver_table.setStyle(TableStyle([
            # نمط الرأس
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), arabic_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # نمط الصفوف
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))
        
        story.append(driver_table)
        story.append(Spacer(1, 20))
        
        # الملاحظات
        if safety_check.notes:
            story.append(Paragraph("📝 الملاحظات والتوصيات", subtitle_style))
            notes_para = Paragraph(safety_check.notes, normal_style)
            story.append(notes_para)
            story.append(Spacer(1, 20))
        
        # معلومات الحالة
        if safety_check.approved_by:
            status_text = "معتمدة ✅" if safety_check.is_approved else "مرفوضة ❌"
            status_color = colors.HexColor('#27AE60') if safety_check.is_approved else colors.HexColor('#E74C3C')
            
            status_style = ParagraphStyle(
                'StatusStyle',
                fontName=arabic_font,
                fontSize=14,
                spaceAfter=10,
                alignment=TA_CENTER,
                textColor=status_color,
                borderWidth=2,
                borderColor=status_color,
                borderPadding=8,
                backColor=colors.HexColor('#F8F9FA')
            )
            
            story.append(Paragraph(f"حالة الطلب: {status_text}", status_style))
            story.append(Paragraph(f"تاريخ الاعتماد: {safety_check.approved_at.strftime('%Y-%m-%d %H:%M')}", normal_style))
            story.append(Paragraph(f"تم بواسطة: {safety_check.approver.name if safety_check.approver else 'غير محدد'}", normal_style))
            
            if safety_check.rejection_reason:
                story.append(Paragraph(f"سبب الرفض: {safety_check.rejection_reason}", normal_style))
            
            story.append(Spacer(1, 20))
        
        # صور فحص السلامة
        if safety_check.safety_images:
            story.append(Paragraph(f"📸 صور فحص السلامة ({len(safety_check.safety_images)} صورة)", subtitle_style))
            story.append(Spacer(1, 10))
            
            # تنظيم الصور في صفوف (صورتين في كل صف)
            images_per_row = 2
            current_row = []
            
            for i, image in enumerate(safety_check.safety_images):
                try:
                    # التحقق من وجود الصورة
                    image_path = image.image_path
                    if not os.path.exists(image_path):
                        continue
                    
                    # إنشاء كائن الصورة
                    img = RLImage(image_path)
                    
                    # تحديد حجم الصورة (الحد الأقصى)
                    max_width = 7*cm
                    max_height = 5*cm
                    
                    # حساب النسبة للحفاظ على أبعاد الصورة
                    img_width = img.imageWidth
                    img_height = img.imageHeight
                    
                    ratio = min(max_width/img_width, max_height/img_height)
                    img.drawWidth = img_width * ratio
                    img.drawHeight = img_height * ratio
                    
                    # إضافة الصورة مع الوصف
                    img_data = [
                        [img],
                        [Paragraph(image.image_description or f'صورة رقم {i+1}', image_desc_style)]
                    ]
                    
                    img_table = Table(img_data, colWidths=[max_width])
                    img_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8F9FA')),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
                    ]))
                    
                    current_row.append(img_table)
                    
                    # إذا امتلأ الصف أو كانت هذه آخر صورة
                    if len(current_row) == images_per_row or i == len(safety_check.safety_images) - 1:
                        # إضافة خلايا فارغة لإكمال الصف
                        while len(current_row) < images_per_row:
                            current_row.append('')
                        
                        # إنشاء جدول للصف
                        row_table = Table([current_row], colWidths=[max_width + 1*cm] * images_per_row)
                        row_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 5),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                            ('TOPPADDING', (0, 0), (-1, -1), 5),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
                        ]))
                        
                        story.append(row_table)
                        story.append(Spacer(1, 15))
                        current_row = []
                
                except Exception as e:
                    current_app.logger.error(f"خطأ في إضافة الصورة للـ PDF: {str(e)}")
                    continue
        
        # تذييل التقرير
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'FooterStyle',
            fontName=arabic_font,
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7F8C8D'),
            borderWidth=1,
            borderColor=colors.HexColor('#BDC3C7'),
            borderPadding=5,
            backColor=colors.HexColor('#F8F9FA')
        )
        
        story.append(Paragraph(f"تم إنشاء هذا التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M')}", footer_style))
        story.append(Paragraph("نُظم - نظام إدارة المركبات والموظفين", footer_style))
        
        # بناء الـ PDF
        doc.build(story)
        buffer.seek(0)
        
        # تسجيل العملية
        log_audit(
            user_id=current_user.id,
            action='export_pdf',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم تصدير طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number} كملف PDF'
        )
        
        # إرسال الـ PDF
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'safety_check_{safety_check.id}_{safety_check.vehicle_plate_number}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"خطأ في تصدير طلب فحص السلامة كـ PDF: {str(e)}")
        flash('حدث خطأ في تصدير الطلب', 'error')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))