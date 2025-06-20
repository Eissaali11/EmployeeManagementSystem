"""
تقرير المعلومات الأساسية للموظف باستخدام WeasyPrint مع دعم العربية
"""
import os
from io import BytesIO
from datetime import datetime
import weasyprint
from flask import render_template_string

def generate_weasy_basic_report(employee_id):
    """إنشاء تقرير أساسي للموظف باستخدام WeasyPrint"""
    try:
        # استيراد داخلي لتجنب المشاكل الدائرية
        from flask import current_app
        with current_app.app_context():
            from sqlalchemy import text
            from app import db
            
            print(f"بدء إنشاء التقرير بـ WeasyPrint للموظف {employee_id}")
            
            # البحث عن الموظف
            employee_query = text("""
                SELECT e.*, d.name as department_name 
                FROM employee e 
                LEFT JOIN department d ON e.department_id = d.id 
                WHERE e.id = :employee_id
            """)
            
            result = db.session.execute(employee_query, {'employee_id': employee_id}).fetchone()
            if not result:
                print(f"لم يتم العثور على الموظف {employee_id}")
                return None, "Employee not found"
            
            # تحويل النتيجة إلى dict
            employee = dict(result._mapping) if hasattr(result, '_mapping') else dict(zip(result.keys(), result))
            print(f"تم العثور على الموظف: {employee.get('name', 'غير معروف')}")
            
            # تحديد مسارات الصور
            static_path = os.path.join(os.getcwd(), 'static')
            
            profile_image_url = ""
            national_id_image_url = ""
            license_image_url = ""
            
            # الصورة الشخصية
            profile_image = employee.get('profile_image')
            if profile_image:
                if profile_image.startswith('uploads/'):
                    profile_image_path = os.path.join(static_path, profile_image)
                else:
                    profile_image_path = os.path.join(static_path, 'uploads', 'employees', profile_image)
                
                if os.path.exists(profile_image_path):
                    profile_image_url = f"file://{profile_image_path}"
            
            # صورة الهوية
            national_id_image = employee.get('national_id_image')
            if national_id_image:
                if national_id_image.startswith('uploads/'):
                    id_image_path = os.path.join(static_path, national_id_image)
                else:
                    id_image_path = os.path.join(static_path, 'uploads', 'employees', national_id_image)
                
                if os.path.exists(id_image_path):
                    national_id_image_url = f"file://{id_image_path}"
            
            # صورة الرخصة
            license_image = employee.get('license_image')
            if license_image:
                if license_image.startswith('uploads/'):
                    license_image_path = os.path.join(static_path, license_image)
                else:
                    license_image_path = os.path.join(static_path, 'uploads', 'employees', license_image)
                
                if os.path.exists(license_image_path):
                    license_image_url = f"file://{license_image_path}"
            
            # إعداد البيانات
            contract_type = employee.get('contract_type', '')
            contract_display = 'سعودي' if contract_type == 'saudi' else 'وافد' if contract_type == 'foreign' else 'غير محدد'
            
            status = employee.get('status', 'unknown')
            status_display = 'نشط' if status == 'active' else 'غير نشط' if status == 'inactive' else 'في إجازة' if status == 'on_leave' else 'غير محدد'
            
            join_date = employee.get('join_date')
            join_date_str = join_date.strftime('%Y/%m/%d') if join_date else 'غير محدد'
            
            basic_salary = employee.get('basic_salary')
            salary_str = f"{basic_salary:,.0f} ريال" if basic_salary else 'غير محدد'
            
            generation_date = datetime.now().strftime('%Y/%m/%d %H:%M')
            
            # HTML template مع CSS للعربية
            html_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير المعلومات الأساسية للموظف</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Noto Sans Arabic', Arial, sans-serif;
            direction: rtl;
            text-align: right;
            font-size: 12px;
            line-height: 1.4;
            color: #333;
            margin: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .main-title {
            font-size: 20px;
            font-weight: bold;
            color: #1a5490;
            margin-bottom: 20px;
        }
        
        .images-section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 15px;
        }
        
        .images-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .image-item {
            text-align: center;
            flex: 1;
            min-width: 150px;
        }
        
        .image-title {
            background-color: #f0f0f0;
            padding: 8px;
            border: 1px solid #ccc;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .image-placeholder {
            width: 120px;
            height: 150px;
            border: 1px solid #ccc;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f9f9f9;
            margin: 0 auto;
        }
        
        .employee-image {
            width: 120px;
            height: 150px;
            object-fit: cover;
            border: 1px solid #ccc;
        }
        
        .section-header {
            background-color: #4a90b8;
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
            margin: 20px 0 0 0;
        }
        
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .info-table td {
            border: 1px solid #333;
            padding: 8px;
            text-align: right;
        }
        
        .info-table td:first-child {
            background-color: #f0f0f0;
            font-weight: bold;
            width: 40%;
        }
        
        .info-table tr:nth-child(even) td:last-child {
            background-color: #f9f9f9;
        }
        
        .performance-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .performance-table th,
        .performance-table td {
            border: 1px solid #333;
            padding: 6px;
            text-align: center;
        }
        
        .performance-table th {
            background-color: #4a90b8;
            color: white;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 10px;
            color: #666;
        }
        
        @page {
            size: A4;
            margin: 1cm;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="main-title">تقرير المعلومات الأساسية للموظف</div>
    </div>
    
    <!-- قسم الصور -->
    <div class="images-section">
        <div class="images-container">
            <div class="image-item">
                <div class="image-title">الصورة الشخصية</div>
                {% if profile_image_url %}
                    <img src="{{ profile_image_url }}" alt="الصورة الشخصية" class="employee-image">
                {% else %}
                    <div class="image-placeholder">لا توجد صورة</div>
                {% endif %}
            </div>
            
            <div class="image-item">
                <div class="image-title">صورة الهوية الوطنية</div>
                {% if national_id_image_url %}
                    <img src="{{ national_id_image_url }}" alt="صورة الهوية" class="employee-image">
                {% else %}
                    <div class="image-placeholder">لا توجد صورة</div>
                {% endif %}
            </div>
            
            <div class="image-item">
                <div class="image-title">صورة رخصة القيادة</div>
                {% if license_image_url %}
                    <img src="{{ license_image_url }}" alt="صورة الرخصة" class="employee-image">
                {% else %}
                    <div class="image-placeholder">لا توجد صورة</div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- المعلومات الأساسية -->
    <div class="section-header">المعلومات الأساسية</div>
    <table class="info-table">
        <tr>
            <td>اسم الموظف</td>
            <td>{{ employee.name or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>رقم الهوية الوطنية</td>
            <td>{{ employee.national_id or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>رقم الهاتف</td>
            <td>{{ employee.mobile or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>الجوال</td>
            <td>{{ employee.mobile or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>البريد الإلكتروني</td>
            <td>{{ employee.email or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>الجنسية</td>
            <td>{{ employee.nationality or 'غير محدد' }}</td>
        </tr>
    </table>
    
    <!-- معلومات العمل -->
    <div class="section-header">معلومات العمل</div>
    <table class="info-table">
        <tr>
            <td>الوظيفة الحالية</td>
            <td>{{ employee.job_title or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>القسم</td>
            <td>{{ employee.department_name or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>رقم الموظف</td>
            <td>{{ employee.employee_id or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>التخصص</td>
            <td>{{ employee.job_title or 'غير محدد' }}</td>
        </tr>
        <tr>
            <td>تاريخ التعيين</td>
            <td>{{ join_date_str }}</td>
        </tr>
        <tr>
            <td>الراتب</td>
            <td>{{ salary_str }}</td>
        </tr>
        <tr>
            <td>أيام الإجازة المتبقية</td>
            <td>غير محدد</td>
        </tr>
    </table>
    
    <!-- سجلات أداء الموظف -->
    <div class="section-header">سجلات أداء الموظف (آخر 10 سجلات)</div>
    <table class="performance-table">
        <thead>
            <tr>
                <th>ملاحظات</th>
                <th>نوع السجل</th>
                <th>التاريخ</th>
                <th>رقم السجل</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td colspan="4">لا توجد سجلات</td>
            </tr>
        </tbody>
    </table>
    
    <!-- الراتب الحالي -->
    <div class="section-header">الراتب الحالي</div>
    <table class="info-table">
        <tr>
            <td>إجمالي الراتب</td>
            <td>{{ salary_str }}</td>
        </tr>
    </table>
    
    <div class="footer">
        تم إنتاج هذا التقرير في: {{ generation_date }}
    </div>
</body>
</html>
            """
            
            # رندر HTML مع البيانات
            html_content = render_template_string(html_template,
                employee=employee,
                profile_image_url=profile_image_url,
                national_id_image_url=national_id_image_url,
                license_image_url=license_image_url,
                contract_display=contract_display,
                status_display=status_display,
                join_date_str=join_date_str,
                salary_str=salary_str,
                generation_date=generation_date
            )
            
            # إنشاء PDF من HTML
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            
            print("تم إنتاج التقرير بـ WeasyPrint بنجاح")
            return pdf_bytes, None
            
    except Exception as e:
        import traceback
        error_msg = f"خطأ في إنتاج التقرير بـ WeasyPrint: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return None, error_msg