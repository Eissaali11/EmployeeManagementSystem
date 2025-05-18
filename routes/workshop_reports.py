"""
وحدة مخصصة لإنشاء تقارير الورشة بصيغة PDF
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
import io
import os

from app import db
from models import Vehicle, VehicleWorkshop, SystemAudit
from utils.simple_workshop_pdf import generate_workshop_pdf

# إنشاء blueprint
workshop_reports_bp = Blueprint('workshop_reports', __name__, url_prefix='/workshop-reports')

@workshop_reports_bp.route('/vehicle/<int:id>/pdf')
@login_required
def vehicle_workshop_pdf(id):
    """تصدير تقرير سجلات الورشة للمركبة كملف PDF"""
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
        
        # إنشاء تقرير PDF
        pdf_buffer = generate_workshop_report_pdf(vehicle, workshop_records)
        
        # اسم الملف
        filename = f"workshop_report_{vehicle.plate_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # تسجيل نشاط النظام
        audit = SystemAudit(
            user_id=current_user.id if current_user.is_authenticated else None,
            username=current_user.username if current_user.is_authenticated else 'guest',
            action_type='export',
            resource_type='vehicle_workshop',
            resource_id=id,
            description=f'تم تصدير تقرير الورشة للمركبة {vehicle.plate_number}',
            ip_address=request.remote_addr,
            timestamp=datetime.now()
        )
        db.session.add(audit)
        db.session.commit()
        
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
        flash(f'حدث خطأ أثناء إنشاء التقرير: {str(e)}', 'error')
        return redirect(url_for('vehicles.view', id=id))