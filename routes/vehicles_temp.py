
# إنشاء تفويض خارجي جديد
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
            # التحقق من نوع الإدخال للسائق
            driver_input_type = request.form.get('driver_input_type', 'from_list')
            
            if driver_input_type == 'from_list':
                employee_id = request.form.get('employee_id')
                if not employee_id:
                    flash('يرجى اختيار موظف من القائمة', 'error')
                    return redirect(request.url)
                
                # إنشاء التفويض مع موظف من القائمة
                external_auth = ExternalAuthorization(
                    vehicle_id=vehicle_id,
                    employee_id=employee_id,
                    project_name=request.form.get('project_name'),
                    authorization_type=request.form.get('authorization_type'),
                    status='pending',
                    external_link=request.form.get('form_link'),
                    notes=request.form.get('notes'),
                    city=request.form.get('city')
                )
            else:
                # الإدخال اليدوي
                manual_name = request.form.get('manual_driver_name', '').strip()
                if not manual_name:
                    flash('يرجى إدخال اسم السائق', 'error')
                    return redirect(request.url)
                
                # إنشاء التفويض مع بيانات يدوية
                external_auth = ExternalAuthorization(
                    vehicle_id=vehicle_id,
                    employee_id=None,
                    project_name=request.form.get('project_name'),
                    authorization_type=request.form.get('authorization_type'),
                    status='pending',
                    external_link=request.form.get('form_link'),
                    notes=request.form.get('notes'),
                    city=request.form.get('city'),
                    manual_driver_name=manual_name,
                    manual_driver_phone=request.form.get('manual_driver_phone', '').strip(),
                    manual_driver_position=request.form.get('manual_driver_position', '').strip(),
                    manual_driver_department=request.form.get('manual_driver_department', '').strip()
                )

            # معالجة رفع الملف
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'authorizations')
                    os.makedirs(upload_dir, exist_ok=True)
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
