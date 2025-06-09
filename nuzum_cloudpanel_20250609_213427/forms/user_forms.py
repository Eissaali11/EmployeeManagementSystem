from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from models import User, UserRole

class UserForm(FlaskForm):
    """نموذج إضافة/تعديل مستخدم"""
    name = StringField('الاسم', validators=[
        DataRequired(message='الاسم مطلوب'),
        Length(min=3, max=100, message='يجب أن يكون الاسم بين 3 و 100 حرف')
    ])
    
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='البريد الإلكتروني مطلوب'),
        Email(message='يرجى إدخال بريد إلكتروني صالح'),
        Length(max=100, message='يجب أن لا يتجاوز البريد الإلكتروني 100 حرف')
    ])
    
    role = SelectField('الدور', validators=[
        DataRequired(message='الدور مطلوب')
    ], coerce=str)
    
    is_active = BooleanField('نشط', default=True)
    
    # ربط مع الموظف (اختياري)
    employee_id = SelectField('الموظف المرتبط', validators=[Optional()], coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
        # تعيين خيارات الأدوار
        self.role.choices = [(role.value, self.get_role_display_name(role)) for role in UserRole]
        
        # تعيين خيارات الموظفين - سيتم تحديدها في الكود بعد الإنشاء
        self.employee_id.choices = [(-1, 'لا يوجد')]
    
    def get_role_display_name(self, role):
        """الحصول على الاسم المعروض للدور"""
        role_names = {
            UserRole.ADMIN: 'مدير النظام',
            UserRole.MANAGER: 'مدير',
            UserRole.HR: 'موارد بشرية',
            UserRole.FINANCE: 'مالية',
            UserRole.FLEET: 'أسطول',
            UserRole.USER: 'مستخدم عادي'
        }
        return role_names.get(role, role.value)
    
    def validate_email(self, field):
        """التحقق من عدم وجود بريد إلكتروني مكرر"""
        # سيتم التحقق في العرض للتمييز بين الإنشاء والتعديل


class CreateUserForm(UserForm):
    """نموذج إنشاء مستخدم جديد"""
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='كلمة المرور مطلوبة'),
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل')
    ])
    
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='تأكيد كلمة المرور مطلوب'),
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    
    def validate_email(self, field):
        """التحقق من عدم وجود بريد إلكتروني مكرر عند إنشاء مستخدم جديد"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('البريد الإلكتروني مستخدم بالفعل')


class EditUserForm(UserForm):
    """نموذج تعديل مستخدم"""
    password = PasswordField('كلمة المرور الجديدة', validators=[
        Optional(),
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل')
    ])
    
    confirm_password = PasswordField('تأكيد كلمة المرور الجديدة', validators=[
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    
    def __init__(self, *args, user_id=None, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.user_id = user_id
    
    def validate_email(self, field):
        """التحقق من عدم وجود بريد إلكتروني مكرر عند تعديل مستخدم"""
        if self.user_id:
            user = User.query.filter_by(email=field.data).first()
            if user and user.id != self.user_id:
                raise ValidationError('البريد الإلكتروني مستخدم بالفعل')


class UserPermissionsForm(FlaskForm):
    """نموذج لتعديل صلاحيات المستخدم"""
    # سيتم إنشاء الحقول ديناميكيًا في العرض
    pass


class UserSearchForm(FlaskForm):
    """نموذج البحث عن المستخدمين"""
    query = StringField('البحث', validators=[Optional()])
    role = SelectField('الدور', validators=[Optional()], coerce=str)
    status = SelectField('الحالة', validators=[Optional()], coerce=str)
    
    def __init__(self, *args, **kwargs):
        super(UserSearchForm, self).__init__(*args, **kwargs)
        
        # تعيين خيارات الأدوار
        self.role.choices = [('', 'جميع الأدوار')] + [(role.value, self.get_role_display_name(role)) for role in UserRole]
        
        # تعيين خيارات الحالة
        self.status.choices = [
            ('', 'جميع الحالات'),
            ('active', 'نشط'),
            ('inactive', 'غير نشط')
        ]
    
    def get_role_display_name(self, role):
        """الحصول على الاسم المعروض للدور"""
        role_names = {
            UserRole.ADMIN: 'مدير النظام',
            UserRole.MANAGER: 'مدير',
            UserRole.HR: 'موارد بشرية',
            UserRole.FINANCE: 'مالية',
            UserRole.FLEET: 'أسطول',
            UserRole.USER: 'مستخدم عادي'
        }
        return role_names.get(role, role.value)