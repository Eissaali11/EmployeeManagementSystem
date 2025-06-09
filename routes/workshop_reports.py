"""
وحدة مخصصة لإنشاء تقارير الورشة بصيغة PDF
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, make_response
from flask_login import login_required, current_user
import io
import os

from app import db
from models import Vehicle, VehicleWorkshop, SystemAudit
from utils.simple_html_pdf import generate_workshop_pdf

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
        
        # إنشاء تقرير HTML قابل للطباعة
        html_content = generate_workshop_pdf(vehicle, workshop_records)
        
        # تسجيل نشاط بسيط في السجل
        import logging
        logging.info(f'تم عرض تقرير الورشة للمركبة {vehicle.plate_number} بواسطة المستخدم {current_user.email if current_user.is_authenticated else "ضيف"}')
        
        # إرجاع صفحة HTML مع ترميز UTF-8
        response = make_response(html_content.decode('utf-8'))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    
    except Exception as e:
        import logging
        logging.error(f"خطأ في إنشاء تقرير الورشة: {str(e)}")
        flash(f'حدث خطأ أثناء إنشاء التقرير: {str(e)}', 'error')
        return redirect(url_for('vehicles.view', id=id))