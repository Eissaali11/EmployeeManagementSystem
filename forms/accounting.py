"""
نماذج النظام المحاسبي - نسخة منظفة
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, BooleanField, IntegerField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, Optional
from wtforms.widgets import TextArea
from decimal import Decimal
from models_accounting import AccountType, TransactionType, PaymentMethod, EntryType


class AccountForm(FlaskForm):
    """نموذج إضافة/تعديل حساب"""
    code = StringField('رمز الحساب', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('اسم الحساب', validators=[DataRequired(), Length(min=2, max=200)])
    name_en = StringField('الاسم بالإنجليزية', validators=[Optional(), Length(max=200)])
    account_type = SelectField('نوع الحساب', 
                              choices=[
                                  ('ASSETS', 'أصول'),
                                  ('LIABILITIES', 'خصوم'),
                                  ('EQUITY', 'حقوق الملكية'),
                                  ('REVENUE', 'إيرادات'),
                                  ('EXPENSES', 'مصروفات')
                              ],
                              validators=[DataRequired()])
    parent_id = SelectField('الحساب الأب', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    description = TextAreaField('وصف الحساب', validators=[Optional()], widget=TextArea())
    is_active = BooleanField('نشط', default=True)


class TransactionEntryForm(FlaskForm):
    """نموذج فرعي لتفاصيل القيد"""
    account_id = SelectField('الحساب', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    entry_type = SelectField('النوع', 
                            choices=[
                                ('DEBIT', 'مدين'),
                                ('CREDIT', 'دائن')
                            ],
                            validators=[DataRequired()])
    amount = DecimalField('المبلغ', validators=[DataRequired(), NumberRange(min=0.01)])
    description = TextAreaField('الوصف', validators=[Optional()])


class TransactionForm(FlaskForm):
    """نموذج إضافة/تعديل قيد محاسبي"""
    transaction_date = DateField('تاريخ القيد', validators=[DataRequired()])
    transaction_type = SelectField('نوع القيد',
                                  choices=[
                                      ('MANUAL', 'قيد يدوي'),
                                      ('SALARY', 'راتب'),
                                      ('VEHICLE_EXPENSE', 'مصروف مركبة'),
                                      ('DEPRECIATION', 'استهلاك'),
                                      ('PAYMENT', 'دفع'),
                                      ('RECEIPT', 'قبض')
                                  ],
                                  validators=[DataRequired()])
    reference_number = StringField('رقم المرجع', validators=[Optional(), Length(max=100)])
    description = TextAreaField('وصف المعاملة', validators=[DataRequired()], widget=TextArea())
    cost_center_id = SelectField('مركز التكلفة', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    vendor_id = SelectField('المورد', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    customer_id = SelectField('العميل', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    
    # تفاصيل القيود - سيتم تعبئتها ديناميكياً
    entries = FieldList(FormField(TransactionEntryForm), min_entries=2)


class SalaryProcessingForm(FlaskForm):
    """نموذج معالجة الرواتب"""
    month = SelectField('الشهر', 
                       choices=[
                           ('1', 'يناير'),
                           ('2', 'فبراير'),
                           ('3', 'مارس'),
                           ('4', 'أبريل'),
                           ('5', 'مايو'),
                           ('6', 'يونيو'),
                           ('7', 'يوليو'),
                           ('8', 'أغسطس'),
                           ('9', 'سبتمبر'),
                           ('10', 'أكتوبر'),
                           ('11', 'نوفمبر'),
                           ('12', 'ديسمبر')
                       ],
                       validators=[DataRequired()])
    year = IntegerField('السنة', validators=[DataRequired(), NumberRange(min=2020, max=2030)])
    department_id = SelectField('القسم', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    salary_account_id = SelectField('حساب الرواتب', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    payable_account_id = SelectField('حساب المستحقات', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    process_all = BooleanField('معالجة جميع الموظفين', default=True)
    submit = SubmitField('معالجة الرواتب')


class VendorForm(FlaskForm):
    """نموذج إضافة/تعديل مورد"""
    code = StringField('رمز المورد', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('اسم المورد', validators=[DataRequired(), Length(min=2, max=200)])
    commercial_register = StringField('السجل التجاري', validators=[Optional(), Length(max=50)])
    tax_number = StringField('الرقم الضريبي', validators=[Optional(), Length(max=50)])
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('العنوان', validators=[Optional()], widget=TextArea())
    contact_person = StringField('الشخص المسؤول', validators=[Optional(), Length(max=100)])
    payment_terms = StringField('شروط الدفع', validators=[Optional(), Length(max=100)])
    credit_limit = DecimalField('حد الائتمان', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    is_active = BooleanField('نشط', default=True)


class CustomerForm(FlaskForm):
    """نموذج إضافة/تعديل عميل"""
    code = StringField('رمز العميل', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('اسم العميل', validators=[DataRequired(), Length(min=2, max=200)])
    commercial_register = StringField('السجل التجاري', validators=[Optional(), Length(max=50)])
    tax_number = StringField('الرقم الضريبي', validators=[Optional(), Length(max=50)])
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('العنوان', validators=[Optional()], widget=TextArea())
    contact_person = StringField('الشخص المسؤول', validators=[Optional(), Length(max=100)])
    credit_limit = DecimalField('حد الائتمان', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    is_active = BooleanField('نشط', default=True)


class CostCenterForm(FlaskForm):
    """نموذج إضافة/تعديل مركز تكلفة"""
    code = StringField('رمز المركز', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('اسم المركز', validators=[DataRequired(), Length(min=2, max=200)])
    name_en = StringField('الاسم بالإنجليزية', validators=[Optional(), Length(max=200)])
    description = TextAreaField('وصف المركز', validators=[Optional()], widget=TextArea())
    parent_id = SelectField('المركز الرئيسي', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    budget_amount = DecimalField('الميزانية المخصصة (ريال)', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    is_active = BooleanField('حالة المركز', default=True)
    submit = SubmitField('حفظ البيانات')


class FiscalYearForm(FlaskForm):
    """نموذج إضافة/تعديل سنة مالية"""
    name = StringField('اسم السنة المالية', validators=[DataRequired(), Length(min=2, max=100)])
    start_date = DateField('تاريخ البداية', validators=[DataRequired()])
    end_date = DateField('تاريخ النهاية', validators=[DataRequired()])
    is_active = BooleanField('نشط', default=True)


class BudgetForm(FlaskForm):
    """نموذج إضافة/تعديل موازنة"""
    fiscal_year_id = SelectField('السنة المالية', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    account_id = SelectField('الحساب', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    cost_center_id = SelectField('مركز التكلفة', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    
    # المبالغ الشهرية
    jan_amount = DecimalField('يناير', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    feb_amount = DecimalField('فبراير', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    mar_amount = DecimalField('مارس', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    apr_amount = DecimalField('أبريل', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    may_amount = DecimalField('مايو', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    jun_amount = DecimalField('يونيو', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    jul_amount = DecimalField('يوليو', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    aug_amount = DecimalField('أغسطس', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    sep_amount = DecimalField('سبتمبر', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    oct_amount = DecimalField('أكتوبر', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    nov_amount = DecimalField('نوفمبر', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    dec_amount = DecimalField('ديسمبر', validators=[Optional(), NumberRange(min=0)], default=Decimal('0'))
    
    notes = TextAreaField('ملاحظات', validators=[Optional()], widget=TextArea())


class AccountingSettingsForm(FlaskForm):
    """نموذج إعدادات النظام المحاسبي"""
    company_name = StringField('اسم الشركة', validators=[DataRequired(), Length(min=2, max=200)])
    tax_number = StringField('الرقم الضريبي', validators=[Optional(), Length(max=50)])
    commercial_register = StringField('السجل التجاري', validators=[Optional(), Length(max=50)])
    address = TextAreaField('العنوان', validators=[Optional()], widget=TextArea())
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(), Length(max=120)])
    
    base_currency = SelectField('العملة الأساسية',
                               choices=[
                                   ('SAR', 'ريال سعودي'),
                                   ('USD', 'دولار أمريكي'),
                                   ('EUR', 'يورو')
                               ],
                               default='SAR')
    decimal_places = IntegerField('عدد المنازل العشرية', validators=[NumberRange(min=0, max=4)], default=2)
    transaction_prefix = StringField('بادئة رقم القيد', validators=[DataRequired(), Length(max=10)], default='JV')
    fiscal_year_start_month = SelectField('شهر بداية السنة المالية',
                                         choices=[
                                             (1, 'يناير'), (2, 'فبراير'), (3, 'مارس'),
                                             (4, 'أبريل'), (5, 'مايو'), (6, 'يونيو'),
                                             (7, 'يوليو'), (8, 'أغسطس'), (9, 'سبتمبر'),
                                             (10, 'أكتوبر'), (11, 'نوفمبر'), (12, 'ديسمبر')
                                         ],
                                         coerce=lambda x: int(x) if x else None,
                                         default=1)


class QuickEntryForm(FlaskForm):
    """نموذج القيد السريع"""
    transaction_date = DateField('التاريخ', validators=[DataRequired()])
    description = StringField('الوصف', validators=[DataRequired(), Length(min=5, max=200)])
    
    # حساب المدين
    debit_account_id = SelectField('الحساب المدين', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    # حساب الدائن  
    credit_account_id = SelectField('الحساب الدائن', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    
    amount = DecimalField('المبلغ', validators=[DataRequired(), NumberRange(min=0.01)])
    reference_number = StringField('رقم المرجع', validators=[Optional(), Length(max=100)])
    cost_center_id = SelectField('مركز التكلفة', coerce=lambda x: int(x) if x else None, validators=[Optional()])


class ReportFiltersForm(FlaskForm):
    """نموذج فلاتر التقارير"""
    from_date = DateField('من تاريخ', validators=[DataRequired()])
    to_date = DateField('إلى تاريخ', validators=[DataRequired()])
    account_id = SelectField('الحساب', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    cost_center_id = SelectField('مركز التكلفة', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    transaction_type = SelectField('نوع المعاملة',
                                  choices=[
                                      ('', 'جميع الأنواع'),
                                      ('MANUAL', 'قيد يدوي'),
                                      ('SALARY', 'راتب'),
                                      ('VEHICLE_EXPENSE', 'مصروف مركبة'),
                                      ('DEPRECIATION', 'استهلاك'),
                                      ('PAYMENT', 'دفع'),
                                      ('RECEIPT', 'قبض')
                                  ],
                                  validators=[Optional()])


class VehicleExpenseForm(FlaskForm):
    """نموذج مصروفات المركبات"""
    vehicle_id = SelectField('المركبة', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    expense_date = DateField('تاريخ المصروف', validators=[DataRequired()])
    expense_type = SelectField('نوع المصروف',
                              choices=[
                                  ('fuel', 'وقود'),
                                  ('maintenance', 'صيانة'),
                                  ('insurance', 'تأمين'),
                                  ('registration', 'تسجيل'),
                                  ('fines', 'مخالفات'),
                                  ('other', 'أخرى')
                              ],
                              validators=[DataRequired()])
    amount = DecimalField('المبلغ', validators=[DataRequired(), NumberRange(min=0.01)])
    vendor_id = SelectField('المورد/المحطة', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    description = TextAreaField('الوصف', validators=[DataRequired()], widget=TextArea())
    receipt_number = StringField('رقم الإيصال', validators=[Optional(), Length(max=100)])
    payment_method = SelectField('طريقة الدفع',
                                choices=[
                                    ('cash', 'نقدي'),
                                    ('bank_transfer', 'تحويل بنكي'),
                                    ('check', 'شيك'),
                                    ('credit_card', 'بطاقة ائتمان')
                                ],
                                validators=[DataRequired()])