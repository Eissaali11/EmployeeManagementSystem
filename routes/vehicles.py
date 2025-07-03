"""
مسارات إدارة المركبات
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from models import Vehicle, Employee, VehicleHandover, db
from datetime import datetime
import os

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@vehicles_bp.route('/')
@login_required
def index():
    """صفحة عرض جميع المركبات"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', '', type=str)
    
    query = Vehicle.query
    
    if search:
        query = query.filter(Vehicle.plate_number.contains(search) | 
                           Vehicle.make.contains(search) | 
                           Vehicle.model.contains(search))
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    vehicles = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('vehicles/index.html', 
                         vehicles=vehicles,
                         search=search,
                         status=status)

@vehicles_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """إضافة مركبة جديدة"""
    if request.method == 'POST':
        vehicle = Vehicle(
            plate_number=request.form['plate_number'],
            make=request.form['make'],
            model=request.form['model'],
            year=int(request.form['year']),
            color=request.form['color'],
            engine_number=request.form.get('engine_number'),
            chassis_number=request.form.get('chassis_number'),
            fuel_type=request.form.get('fuel_type', 'بنزين'),
            mileage=int(request.form.get('mileage', 0)),
            status=request.form.get('status', 'متاحة'),
            notes=request.form.get('notes')
        )
        
        try:
            db.session.add(vehicle)
            db.session.commit()
            flash('تم إضافة المركبة بنجاح', 'success')
            return redirect(url_for('vehicles.index'))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في إضافة المركبة', 'error')
    
    return render_template('vehicles/new.html')

@vehicles_bp.route('/<int:id>')
@login_required
def show(id):
    """عرض تفاصيل مركبة"""
    vehicle = Vehicle.query.get_or_404(id)
    handovers = VehicleHandover.query.filter_by(vehicle_id=id).order_by(VehicleHandover.handover_date.desc()).limit(10).all()
    return render_template('vehicles/show.html', vehicle=vehicle, handovers=handovers)

@vehicles_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل مركبة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        vehicle.plate_number = request.form['plate_number']
        vehicle.make = request.form['make']
        vehicle.model = request.form['model']
        vehicle.year = int(request.form['year'])
        vehicle.color = request.form['color']
        vehicle.engine_number = request.form.get('engine_number')
        vehicle.chassis_number = request.form.get('chassis_number')
        vehicle.fuel_type = request.form.get('fuel_type')
        vehicle.mileage = int(request.form.get('mileage', 0))
        vehicle.status = request.form.get('status')
        vehicle.notes = request.form.get('notes')
        
        try:
            db.session.commit()
            flash('تم تحديث المركبة بنجاح', 'success')
            return redirect(url_for('vehicles.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في تحديث المركبة', 'error')
    
    return render_template('vehicles/edit.html', vehicle=vehicle)

@vehicles_bp.route('/<int:id>/handover', methods=['GET', 'POST'])
@login_required
def handover(id):
    """تسليم مركبة لموظف"""
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        handover = VehicleHandover(
            vehicle_id=id,
            employee_id=request.form['employee_id'],
            handover_date=datetime.strptime(request.form['handover_date'], '%Y-%m-%d').date(),
            return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d').date() if request.form.get('return_date') else None,
            purpose=request.form['purpose'],
            mileage_out=int(request.form.get('mileage_out', 0)),
            mileage_in=int(request.form.get('mileage_in', 0)) if request.form.get('mileage_in') else None,
            notes=request.form.get('notes')
        )
        
        try:
            db.session.add(handover)
            vehicle.status = 'مستلمة'
            db.session.commit()
            flash('تم تسليم المركبة بنجاح', 'success')
            return redirect(url_for('vehicles.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في تسليم المركبة', 'error')
    
    employees = Employee.query.all()
    return render_template('vehicles/handover.html', vehicle=vehicle, employees=employees)

@vehicles_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف مركبة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        flash('تم حذف المركبة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('خطأ في حذف المركبة', 'error')
    
    return redirect(url_for('vehicles.index'))