# دليل المطور - نُظم

## البدء السريع

### إعداد بيئة التطوير
```bash
# استنساخ المشروع
git clone <repository-url>
cd nuzum-system

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# تثبيت المتطلبات
pip install -r requirements.txt
```

### إعداد قاعدة البيانات
```bash
# إنشاء قاعدة بيانات PostgreSQL
createdb nuzum_db

# تصدير متغيرات البيئة
export DATABASE_URL=postgresql://username:password@localhost/nuzum_db
export SESSION_SECRET=your-secret-key
```

### تشغيل النظام
```bash
# للتطوير
python app.py

# للإنتاج
gunicorn --bind 0.0.0.0:5000 main:app
```

## إضافة وحدة جديدة

### 1. إنشاء النموذج (Model)
```python
# في models.py
class NewEntity(db.Model):
    __tablename__ = 'new_entity'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewEntity {self.name}>'
```

### 2. إنشاء النماذج (Forms)
```python
# في forms/new_entity_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NewEntityForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired()])
    submit = SubmitField('حفظ')
```

### 3. إنشاء الخدمة (Service)
```python
# في services/new_entity_service.py
from models import NewEntity
from core.extensions import db
from utils.audit_logger import log_activity

class NewEntityService:
    @staticmethod
    def create_entity(name):
        entity = NewEntity(name=name)
        db.session.add(entity)
        db.session.commit()
        
        log_activity(
            action='create',
            entity_type='new_entity',
            entity_id=entity.id,
            details=f'تم إنشاء كيان جديد: {name}'
        )
        
        return entity
```

### 4. إنشاء المسارات (Routes)
```python
# في routes/new_entity.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from services.new_entity_service import NewEntityService
from forms.new_entity_forms import NewEntityForm

new_entity_bp = Blueprint('new_entity', __name__, url_prefix='/new_entity')

@new_entity_bp.route('/')
@login_required
def index():
    entities = NewEntity.query.all()
    return render_template('new_entity/index.html', entities=entities)

@new_entity_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = NewEntityForm()
    if form.validate_on_submit():
        entity = NewEntityService.create_entity(form.name.data)
        flash('تم إنشاء الكيان بنجاح', 'success')
        return redirect(url_for('new_entity.index'))
    return render_template('new_entity/add.html', form=form)
```

### 5. إنشاء القوالب (Templates)
```html
<!-- في templates/new_entity/index.html -->
{% extends "base.html" %}

{% block title %}إدارة الكيانات الجديدة{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>إدارة الكيانات الجديدة</h2>
        <a href="{{ url_for('new_entity.add') }}" class="btn btn-primary">
            <i class="fas fa-plus me-2"></i>إضافة كيان جديد
        </a>
    </div>
    
    <!-- محتوى الجدول هنا -->
</div>
{% endblock %}
```

### 6. تسجيل المسار في التطبيق
```python
# في core/app_factory.py - دالة register_blueprints
from routes.new_entity import new_entity_bp
app.register_blueprint(new_entity_bp)
```

## إضافة صلاحيات جديدة

### 1. تحديث enum الوحدات
```python
# في models.py
class Module(enum.Enum):
    EMPLOYEES = "employees"
    ATTENDANCE = "attendance"
    # ... وحدات أخرى
    NEW_MODULE = "new_module"  # الوحدة الجديدة
```

### 2. إنشاء decorator للصلاحيات
```python
# في routes/new_entity.py
from functools import wraps
from flask_login import current_user
from models import Module, Permission

def new_entity_permission_required(permission=Permission.VIEW):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can_access_module(Module.NEW_MODULE, permission):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 3. استخدام الصلاحيات
```python
@new_entity_bp.route('/add')
@login_required
@new_entity_permission_required(Permission.CREATE)
def add():
    # منطق الإضافة
    pass
```

## إضافة تقرير جديد

### 1. تحديث خدمة التقارير
```python
# في services/report_service.py
@staticmethod
def get_new_entity_report():
    entities = NewEntity.query.all()
    return [
        {
            'id': entity.id,
            'name': entity.name,
            'created_at': entity.created_at.strftime('%Y-%m-%d')
        }
        for entity in entities
    ]
```

### 2. إضافة مسار التقرير
```python
# في routes/reports.py
@reports_bp.route('/new_entity')
@login_required
def new_entity_report():
    data = ReportService.get_new_entity_report()
    return render_template('reports/new_entity.html', data=data)
```

## إضافة إشعار جديد

### 1. تحديث خدمة الإشعارات
```python
# في services/notification_service.py
def send_new_entity_notification(entity, phone_number):
    message = f"""
إشعار كيان جديد

الكيان: {entity.name}
تاريخ الإنشاء: {entity.created_at.strftime('%Y-%m-%d')}

تم إنشاء كيان جديد في النظام.
    """.strip()
    
    return self.send_sms(phone_number, message)
```

## أفضل الممارسات

### 1. تسمية الملفات والمجلدات
- استخدم أسماء واضحة ووصفية
- اتبع نمط التسمية المتسق
- استخدم snake_case للملفات والمجلدات

### 2. تنظيم الكود
```python
# ترتيب الاستيرادات
# 1. مكتبات Python الأساسية
import os
from datetime import datetime

# 2. مكتبات خارجية
from flask import Flask, request
from sqlalchemy import func

# 3. مكتبات المشروع
from models import User, Employee
from services.auth_service import AuthService
```

### 3. التعليقات والتوثيق
```python
def complex_function(param1, param2):
    """
    وصف مفصل للدالة
    
    Args:
        param1 (str): وصف المعامل الأول
        param2 (int): وصف المعامل الثاني
    
    Returns:
        dict: وصف القيمة المرجعة
    
    Raises:
        ValueError: متى يتم رفع هذا الاستثناء
    """
    pass
```

### 4. معالجة الأخطاء
```python
try:
    # العملية الرئيسية
    result = some_operation()
    db.session.commit()
    
    # تسجيل النجاح
    log_activity(
        action='operation_success',
        entity_type='entity',
        entity_id=result.id,
        details='تمت العملية بنجاح'
    )
    
    return True, result
    
except Exception as e:
    db.session.rollback()
    
    # تسجيل الخطأ
    log_activity(
        action='operation_failed',
        entity_type='entity',
        entity_id=None,
        details=f'فشلت العملية: {str(e)}'
    )
    
    return False, str(e)
```

### 5. التحقق من البيانات
```python
# في النماذج
class EntityForm(FlaskForm):
    name = StringField('الاسم', validators=[
        DataRequired(message='الاسم مطلوب'),
        Length(min=2, max=100, message='الاسم يجب أن يكون بين 2 و 100 حرف')
    ])

# في الخدمات
def validate_entity_data(data):
    errors = []
    
    if not data.get('name'):
        errors.append('الاسم مطلوب')
    
    if len(data.get('name', '')) > 100:
        errors.append('الاسم طويل جداً')
    
    return errors
```

## اختبار الكود

### 1. اختبارات الوحدة
```python
# في tests/test_new_entity_service.py
import unittest
from services.new_entity_service import NewEntityService

class TestNewEntityService(unittest.TestCase):
    def test_create_entity(self):
        entity = NewEntityService.create_entity('Test Entity')
        self.assertIsNotNone(entity)
        self.assertEqual(entity.name, 'Test Entity')
```

### 2. اختبارات التكامل
```python
# في tests/test_new_entity_routes.py
import unittest
from app import create_app

class TestNewEntityRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_index_route(self):
        response = self.client.get('/new_entity/')
        self.assertEqual(response.status_code, 200)
```

## نشر النظام

### 1. إعداد الإنتاج
```bash
# متغيرات البيئة للإنتاج
export FLASK_ENV=production
export DATABASE_URL=postgresql://prod_user:prod_pass@prod_host/prod_db
export SESSION_SECRET=strong-random-secret
```

### 2. تشغيل الخادم
```bash
# باستخدام Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app

# باستخدام Docker
docker build -t nuzum-system .
docker run -p 5000:5000 nuzum-system
```

## استكشاف الأخطاء

### 1. سجلات النظام
```python
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# استخدام السجلات
logger.info('معلومة مفيدة')
logger.warning('تحذير')
logger.error('خطأ حدث')
```

### 2. تتبع الأخطاء
- راجع سجل الأنشطة في قاعدة البيانات
- تحقق من سجلات الخادم
- استخدم أدوات المطور في المتصفح

هذا الدليل يوفر إطار عمل شامل لتطوير وصيانة النظام بشكل احترافي.