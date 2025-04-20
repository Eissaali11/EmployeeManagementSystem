"""
نماذج إدارة المستخدمين
توفر هذه الوحدة نماذج لإنشاء وتعديل المستخدمين وصلاحياتهم
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from models import UserRole

class UserForm(FlaskForm):
    """نموذج إنشاء وتعديل المستخدم"""
    name = StringField('الاسم', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('كلمة المرور', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[Optional(), EqualTo('password', message='كلمات المرور غير متطابقة')])
    role = SelectField('الدور', validators=[DataRequired()], coerce=str)
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # تعبئة قائمة الأدوار
        self.role.choices = [(role.value, self._get_role_display_name(role)) for role in UserRole]
    
    def _get_role_display_name(self, role):
        """الحصول على اسم العرض للدور"""
        role_names = {
            UserRole.ADMIN: "مدير النظام",
            UserRole.MANAGER: "مدير",
            UserRole.HR: "موارد بشرية",
            UserRole.FINANCE: "مالية",
            UserRole.FLEET: "مسؤول أسطول",
            UserRole.USER: "مستخدم عادي"
        }
        return role_names.get(role, "مستخدم")

class ProfileForm(FlaskForm):
    """نموذج تعديل الملف الشخصي"""
    name = StringField('الاسم', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email(), Length(max=100)], render_kw={'readonly': True})
    password = PasswordField('كلمة المرور الجديدة', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[Optional(), EqualTo('password', message='كلمات المرور غير متطابقة')])
    submit = SubmitField('تحديث')

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول"""
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class PasswordResetRequestForm(FlaskForm):
    """نموذج طلب إعادة تعيين كلمة المرور"""
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    submit = SubmitField('إرسال رابط إعادة التعيين')

class PasswordResetForm(FlaskForm):
    """نموذج إعادة تعيين كلمة المرور"""
    password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password', message='كلمات المرور غير متطابقة')])
    submit = SubmitField('إعادة تعيين كلمة المرور')