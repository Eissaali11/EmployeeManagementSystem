"""
نماذج وحدة السيارات
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, BooleanField, DecimalField, HiddenField, IntegerField, SubmitField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange, URL, Length
from datetime import date


class VehicleAccidentForm(FlaskForm):
    """نموذج إضافة وتعديل سجل حادث مروري"""
    vehicle_id = HiddenField('معرف السيارة')
    accident_date = DateField('تاريخ الحادث', validators=[DataRequired()], default=date.today)
    driver_name = StringField('اسم السائق', validators=[DataRequired(), Length(min=2, max=100)])
    accident_status = SelectField('حالة الحادث', choices=[
        ('قيد المعالجة', 'قيد المعالجة'),
        ('مغلق', 'مغلق'),
        ('معلق', 'معلق'),
        ('في التأمين', 'في التأمين')
    ], default='قيد المعالجة')
    vehicle_condition = StringField('حالة السيارة', validators=[Optional(), Length(max=100)])
    deduction_amount = DecimalField('مبلغ الخصم على السائق', validators=[Optional(), NumberRange(min=0)], default=0.0)
    deduction_status = BooleanField('تم الخصم')
    accident_file_link = StringField('رابط ملف الحادث', validators=[Optional(), URL()])
    location = StringField('موقع الحادث', validators=[Optional(), Length(max=255)])
    police_report = BooleanField('تم عمل محضر شرطة')
    insurance_claim = BooleanField('تم رفع مطالبة للتأمين')
    description = TextAreaField('وصف الحادث', validators=[Optional()])
    notes = TextAreaField('ملاحظات إضافية', validators=[Optional()])
    submit = SubmitField('حفظ')