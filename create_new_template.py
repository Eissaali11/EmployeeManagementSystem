"""
سكريبت لإنشاء ملف قالب Excel جديد للموظفين بالترتيب الصحيح
"""
import pandas as pd
import xlsxwriter
from io import BytesIO

def create_employee_template():
    """
    إنشاء ملف قالب Excel جديد للموظفين
    """
    # إنشاء DataFrame فارغ بالأعمدة المطلوبة بالترتيب الصحيح
    df = pd.DataFrame(columns=[
        'Name',          # الاسم
        'ID Number',     # رقم الهوية الوطنية
        'Emp .N',        # الرقم الوظيفي
        'No.Mobile',     # رقم الجوال
        'Job Title',     # المسمى الوظيفي
        'Status',        # الحالة
        'Location',      # الموقع
        'Project',       # المشروع
        'Email'          # البريد الإلكتروني
    ])
    
    # إضافة صف واحد كمثال
    df.loc[0] = [
        'محمد أحمد',     # الاسم
        '1234567890',    # رقم الهوية الوطنية
        'EMP123',        # الرقم الوظيفي
        '0512345678',    # رقم الجوال
        'مهندس',         # المسمى الوظيفي
        'active',        # الحالة (active, inactive, on_leave)
        'الرياض',        # الموقع
        'مشروع 1',       # المشروع
        'example@mail.com' # البريد الإلكتروني
    ]
    
    # حفظ الملف
    print("جاري إنشاء ملف قالب Excel جديد...")
    output_file = 'new_employee_template.xlsx'
    
    # إنشاء ملف Excel باستخدام xlsxwriter
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='نموذج الموظفين', index=False)
        
        # تنسيق الملف
        workbook = writer.book
        worksheet = writer.sheets['نموذج الموظفين']
        
        # تنسيق العناوين
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F2F2F2',
            'border': 1
        })
        
        # تطبيق التنسيق على صف العناوين
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
        
        # ضبط عرض الأعمدة
        for i, column in enumerate(df.columns):
            column_width = max(len(column) + 2, 15)
            worksheet.set_column(i, i, column_width)
    
    print(f"تم إنشاء ملف القالب بنجاح: {output_file}")
    print(f"تأكد من ترتيب الأعمدة: الاسم، رقم الهوية، الرقم الوظيفي، رقم الجوال، المسمى الوظيفي")
    return output_file

if __name__ == "__main__":
    create_employee_template()