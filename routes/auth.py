from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User

# إنشاء blueprint للمصادقة
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    """صفحة تسجيل الدخول باستخدام Firebase"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
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
    required_fields = ['uid', 'email', 'name', 'picture']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
    
    # البحث عن المستخدم أو إنشائه
    user = User.query.filter_by(firebase_uid=data['uid']).first()
    
    if not user:
        # إنشاء مستخدم جديد
        user = User(
            firebase_uid=data['uid'],
            email=data['email'],
            name=data['name'],
            profile_picture=data['picture'],
            role='user',  # الدور الافتراضي للمستخدمين الجدد
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
    
    # تحديث آخر تسجيل دخول
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # تسجيل الدخول باستخدام Flask-Login
    login_user(user)
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'redirect': url_for('dashboard.index')
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

@auth_bp.route('/unauthorized')
def unauthorized():
    """صفحة غير مصرح بها"""
    return render_template('auth/unauthorized.html'), 403