from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

# إنشاء blueprint للمصادقة
auth_bp = Blueprint('auth', __name__)

# مسار افتراضي لإعادة التوجيه للمسجلين
@auth_bp.route('/index')
def index():
    # إعادة توجيه المستخدم إلى المسار الرئيسي حيث سيتم التحقق من صلاحياته
    return redirect(url_for('root'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول بالبريد الإلكتروني وكلمة المرور أو Firebase"""
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        if not email or not password:
            flash('الرجاء إدخال البريد الإلكتروني وكلمة المرور', 'danger')
            return redirect(url_for('auth.login'))
        
        try:
            # التحقق من صحة البريد الإلكتروني
            valid_email = validate_email(email)
            email = valid_email.email
        except EmailNotValidError:
            flash('البريد الإلكتروني غير صالح', 'danger')
            return redirect(url_for('auth.login'))
        
        # البحث عن المستخدم
        user = User.query.filter_by(email=email).first()
        
        # التحقق من وجود المستخدم وصحة كلمة المرور
        if not user or not user.check_password(password):
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('auth.login'))
        
        # تسجيل الدخول
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('root'))
    
    return render_template(
        'auth/login.html',
        firebase_api_key=current_app.config['FIREBASE_API_KEY'],
        firebase_project_id=current_app.config['FIREBASE_PROJECT_ID'],
        firebase_app_id=current_app.config['FIREBASE_APP_ID']
    )

@auth_bp.route('/auth/process', methods=['POST'])
def process_auth():
    """معالجة بيانات المصادقة من Firebase"""
    data = request.json
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    # تحقق من وجود البيانات المطلوبة
    required_fields = ['uid', 'email', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
    
    # إذا كان الصورة غير موجودة، استخدم قيمة فارغة
    if 'picture' not in data:
        data['picture'] = ''
    
    # محاولة البحث عن المستخدم حسب معرف Firebase
    user = User.query.filter_by(firebase_uid=data['uid']).first()
    
    # إذا لم يتم العثور عليه، ابحث حسب البريد الإلكتروني (للمستخدمين الموجودين بالفعل)
    if not user:
        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            # تحديث معرف Firebase للمستخدم الموجود
            user.firebase_uid = data['uid']
            user.auth_type = 'firebase'
            if data['picture']:
                user.profile_picture = data['picture']
            db.session.commit()
            current_app.logger.info(f"تم تحديث معرف Firebase للمستخدم: {user.email}")
        else:
            # إنشاء مستخدم جديد
            user = User(
                firebase_uid=data['uid'],
                email=data['email'],
                name=data['name'],
                profile_picture=data['picture'],
                role=UserRole.USER,  # الدور الافتراضي للمستخدمين الجدد
                auth_type='firebase',
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"تم إنشاء مستخدم جديد: {user.email}")
    
    # تحديث آخر تسجيل دخول
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # تسجيل الدخول باستخدام Flask-Login
    login_user(user)
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'redirect': url_for('root')
    })

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج من النظام"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """عرض ملف المستخدم الشخصي"""
    return render_template('auth/profile.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """تم إلغاء وظيفة تسجيل مستخدم جديد"""
    # إعادة توجيه جميع الطلبات إلى صفحة تسجيل الدخول
    flash('لا يسمح بإنشاء حسابات جديدة في الوقت الحالي', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/unauthorized')
def unauthorized():
    """صفحة غير مصرح بها"""
    return render_template('auth/unauthorized.html'), 403