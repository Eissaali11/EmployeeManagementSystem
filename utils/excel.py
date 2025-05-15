import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta
from utils.date_converter import parse_date, format_date_gregorian, format_date_hijri
from calendar import monthrange
import xlsxwriter

def parse_employee_excel(file):
    """
    Parse Excel file containing employee data
    
    Args:
        file: The uploaded Excel file
        
    Returns:
        List of dictionaries containing employee data
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read the Excel file explicitly using openpyxl engine
        df = pd.read_excel(file, engine='openpyxl')
        
        # Print column names for debugging
        print(f"Excel columns: {df.columns.tolist()}")
        
        # Clean column names - convert all to string and strip whitespace
        clean_columns = {}
        for col in df.columns:
            # Skip datetime objects
            if isinstance(col, datetime):
                continue
            
            # Clean column name
            clean_name = str(col).strip()
            clean_columns[col] = clean_name
            
        # Create a mapping for column detection
        column_mappings = {
            'name': ['name', 'full name', 'employee name', 'اسم', 'الاسم', 'اسم الموظف', 'full_name', 'employee_name'],
            'employee_id': ['emp n', 'emp.n', 'emp. n', 'emp id', 'emp.id', 'emp. id', 'employee id', 'employee number', 'emp no', 'employee no', 'رقم الموظف', 'الرقم الوظيفي', 'employee_id', 'emp_id', 'emp_no', 'emp .n', 'empn'],
            'national_id': ['id n', 'id.n', 'id. n', 'id no', 'national id', 'identity no', 'identity number', 'national number', 'هوية', 'رقم الهوية', 'الرقم الوطني', 'national_id', 'identity_no', 'id number'],
            'mobile': ['mobile', 'mobil', 'phone', 'cell', 'telephone', 'جوال', 'رقم الجوال', 'هاتف', 'mobile_no', 'phone_no', 'no.mobile', 'no. mobile'],
            'job_title': ['job title', 'position', 'title', 'المسمى', 'المسمى الوظيفي', 'الوظيفة', 'job_title', 'job_position'],
            'status': ['status', 'employee status', 'emp status', 'الحالة', 'حالة', 'حالة الموظف', 'employee_status'],
            'location': ['location', 'office location', 'work location', 'موقع', 'الموقع', 'location_name'],
            'project': ['project', 'project name', 'assigned project', 'مشروع', 'المشروع', 'project_name'],
            'email': ['email', 'email address', 'بريد', 'البريد الإلكتروني', 'email_address']
        }
        
        # Map columns to their normalized names
        detected_columns = {}
        for col in df.columns:
            if isinstance(col, datetime):
                continue
                
            col_str = str(col).lower().strip()
            
            # Check for exact column name or common variations
            for field, variations in column_mappings.items():
                if col_str in variations or any(var in col_str for var in variations):
                    detected_columns[field] = col
                    print(f"Detected '{field}' column: {col}")
                    break
                    
        # Handle special case for Excel files with columns like 'Name', 'Emp .N', etc. - explicit mappings
        # هذه المعلومات تستخدم في معالجة النموذج الرسمي المستخدم في النظام
        # الترتيب هنا مهم جداً كما في نموذج الموظفين
        explicit_mappings = {
            'Name': 'name',  # الاسم
            'Emp .N': 'employee_id',  # رقم الموظف (عادة ما يستخدم في ملفات الموظفين)
            'ID .N': 'national_id',  # رقم الهوية الوطنية (تصحيح الخطأ)
            'ID Number': 'national_id',  # رقم الهوية
            'Emp.N': 'employee_id',  # تنسيق آخر للرقم الوظيفي
            'No.Mobile': 'mobile',  # رقم الجوال
            'No.Mobile ': 'mobile',  # رقم الجوال (مع مسافة إضافية)
            'Mobil': 'mobile',  # رقم الجوال صيغة بديلة
            'Job Title': 'job_title',  # المسمى الوظيفي
            'Status': 'status',  # الحالة
            'Location': 'location',  # الموقع
            'Project': 'project',  # المشروع
            'Email': 'email'  # البريد الإلكتروني
        }
        
        # التأكد من وجود الأعمدة المطلوبة حسب الترتيب الصحيح
        expected_columns = ['Name', 'Emp .N', 'ID .N', 'Mobil', 'Job Title']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"تحذير: العمود التالي غير موجود في الملف: {', '.join(missing_columns)}")
            print(f"الأعمدة الموجودة هي: {[c for c in df.columns if not isinstance(c, datetime)]}")
        
        # التعرف على أعمدة Emp .N (قد تأتي بأشكال مختلفة)
        employee_id_columns = ['Emp .N', 'Emp.N', 'EmpN', 'Emp N']
        for col_name in employee_id_columns:
            if col_name in df.columns:
                detected_columns['employee_id'] = col_name
                print(f"تم العثور على عمود رقم الموظف: {col_name}")
                break
                
        # الاعتماد على نص "Emp" في اسم العمود للكشف عن رقم الموظف
        if 'employee_id' not in detected_columns:
            for col in df.columns:
                if isinstance(col, str) and 'emp' in col.lower() and '.n' in col.lower():
                    detected_columns['employee_id'] = col
                    print(f"تم العثور على عمود رقم الموظف من خلال الكلمة المفتاحية: {col}")
                    break
                    
        # إعطاء الأولوية لعمود Emp .N لرقم الموظف، حتى لو كان قد تم تعيينه كرقم هوية سابقا
        if 'Emp .N' in df.columns:
            detected_columns['employee_id'] = 'Emp .N'
            print("إعطاء الأولوية لعمود Emp .N كرقم موظف")
        
        # فحص ترتيب الأعمدة وإصلاحه إذا كان غير صحيح
        if len(df.columns) >= 4:  # نخفض العدد المطلوب للأعمدة
            if 'Name' in df.columns:
                detected_columns['name'] = 'Name'
            
            if 'ID Number' in df.columns:
                detected_columns['national_id'] = 'ID Number'
            
            if 'Job Title' in df.columns:
                detected_columns['job_title'] = 'Job Title'
            
            # البحث عن أعمدة الجوال بصيغ مختلفة
            mobile_columns = ['No.Mobile', 'No.Mobile ', 'Mobil', 'Mobile', 'Phone']
            for col_name in mobile_columns:
                if col_name in df.columns:
                    detected_columns['mobile'] = col_name
                    print(f"تم العثور على عمود رقم الجوال: {col_name}")
                    break
                    
            # إذا لم يتم العثور على الأعمدة الأساسية، نحاول أن نخمنها حسب الترتيب
            if not (set(['name', 'employee_id', 'national_id', 'job_title']).issubset(set(detected_columns.keys()))):
                print("الأعمدة الأساسية غير موجودة، محاولة تخمينها حسب الترتيب...")
                # نفترض أن العمود الأول هو الاسم والثاني رقم الهوية والثالث رقم الموظف
                columns_list = [col for col in df.columns if not isinstance(col, datetime)]
                if len(columns_list) >= 5:
                    if 'name' not in detected_columns and len(columns_list) > 0:
                        detected_columns['name'] = columns_list[0]
                        print(f"تخمين: العمود الأول '{columns_list[0]}' = الاسم")
                    
                    if 'national_id' not in detected_columns and len(columns_list) > 1:
                        detected_columns['national_id'] = columns_list[1]
                        print(f"تخمين: العمود الثاني '{columns_list[1]}' = رقم الهوية الوطنية")
                    
                    if 'employee_id' not in detected_columns and len(columns_list) > 2:
                        detected_columns['employee_id'] = columns_list[2]
                        print(f"تخمين: العمود الثالث '{columns_list[2]}' = رقم الموظف")
                    
                    if 'mobile' not in detected_columns and len(columns_list) > 3:
                        detected_columns['mobile'] = columns_list[3]
                        print(f"تخمين: العمود الرابع '{columns_list[3]}' = رقم الجوال")
                    
                    if 'job_title' not in detected_columns and len(columns_list) > 4:
                        detected_columns['job_title'] = columns_list[4]
                        print(f"تخمين: العمود الخامس '{columns_list[4]}' = المسمى الوظيفي")
        
        for excel_col, field in explicit_mappings.items():
            if excel_col in df.columns:
                detected_columns[field] = excel_col
                print(f"Explicitly mapped '{excel_col}' to '{field}'")
        
        # Print final column mapping
        print(f"Final column mapping: {detected_columns}")
        
        # Check required columns - divide into essential and non-essential fields
        essential_fields = ['name', 'employee_id', 'national_id']  # هذه مطلوبة دائمًا
        other_fields = ['mobile', 'job_title']  # هذه يمكن إنشاء قيم افتراضية لها
        
        missing_essential = [field for field in essential_fields if field not in detected_columns]
        if missing_essential:
            missing_str = ", ".join(missing_essential)
            raise ValueError(f"Required columns missing: {missing_str}. Available columns: {[c for c in df.columns if not isinstance(c, datetime)]}")
        
        # بالنسبة للحقول غير الأساسية المفقودة، سننشئ أعمدة وهمية تحتوي على قيم افتراضية
        for field in other_fields:
            if field not in detected_columns:
                print(f"Warning: Creating default column for: {field}")
                # إنشاء عمود وهمي يحتوي على قيم فارغة/افتراضية
                dummy_column_name = f"__{field}__default"
                df[dummy_column_name] = None  # إنشاء عمود فارغ
                detected_columns[field] = dummy_column_name  # تعيين العمود الوهمي للحقل
        
        # Process each row
        employees = []
        for idx, row in df.iterrows():
            try:
                # Skip completely empty rows
                if row.isnull().all():
                    continue
                
                # Handle rows with missing required fields by filling with defaults
                missing_fields = []
                all_fields = essential_fields + other_fields  # جميع الحقول المطلوبة والإضافية
                for field in all_fields:
                    if pd.isna(row[detected_columns[field]]):
                        missing_fields.append(field)
                
                # If more than 3 required fields are missing, skip the row
                if len(missing_fields) > 3:
                    print(f"Skipping row {idx+1} due to too many missing required fields: {', '.join(missing_fields)}")
                    continue
                    
                # If name is missing but there are at least 2 other fields with values, try to process it
                if 'name' in missing_fields and len(missing_fields) <= 2:
                    # Generate a temporary name based on available data
                    temp_name = f"موظف-{idx+1}"
                    print(f"Row {idx+1}: Missing name, using '{temp_name}' temporarily")
                    # We'll fill this in the next section
                
                # Create employee dictionary with required fields
                employee = {}
                
                # Add required fields with defaults for missing values
                for field in all_fields:
                    value = row[detected_columns[field]]
                    # Convert to string and handle NaN values
                    if pd.isna(value):
                        # Generate default values for missing fields
                        if field == 'name':
                            value = f"موظف-{idx+1}"
                        elif field == 'employee_id':
                            value = f"EMP{idx+1000}"
                        elif field == 'national_id':
                            # تنسيق مختلف للرقم الوطني بحيث لا يكون مشابه للرقم الوظيفي
                            value = f"N-{idx+5000:07d}"
                        elif field == 'mobile':
                            value = f"05xxxxxxxx"
                        elif field == 'job_title':
                            value = "موظف"
                        print(f"Row {idx+1}: Auto-filled missing {field} with '{value}'")
                    employee[field] = str(value)
                
                # Handle status field specially
                if 'status' in detected_columns:
                    status_col = detected_columns['status']
                    status_value = row[status_col]
                    
                    if isinstance(status_value, datetime) or pd.isna(status_value):
                        employee['status'] = 'active'  # Default value
                    else:
                        # Normalize status values
                        status_str = str(status_value).lower().strip()
                        if status_str in ['active', 'نشط', 'فعال']:
                            employee['status'] = 'active'
                        elif status_str in ['inactive', 'غير نشط', 'غير فعال']:
                            employee['status'] = 'inactive'
                        elif status_str in ['on_leave', 'on leave', 'leave', 'إجازة', 'في إجازة']:
                            employee['status'] = 'on_leave'
                        else:
                            employee['status'] = 'active'  # Default to active
                else:
                    employee['status'] = 'active'  # Default value
                
                # Add optional fields if present in the detected columns
                optional_fields = ['location', 'project', 'email']
                for field in optional_fields:
                    if field in detected_columns and not pd.isna(row[detected_columns[field]]):
                        employee[field] = str(row[detected_columns[field]])
                
                # Print the processed employee data for debugging
                print(f"Processed employee: {employee.get('name', 'Unknown')}")
                
                employees.append(employee)
            except Exception as e:
                print(f"Error processing row {idx+1}: {str(e)}")
                # Continue to next row instead of failing the entire import
                continue
        
        if not employees:
            raise ValueError("No valid employee records found in the Excel file")
            
        return employees
    
    except Exception as e:
        import traceback
        print(f"Error parsing Excel: {str(e)}")
        print(traceback.format_exc())
        raise Exception(f"Error parsing Excel file: {str(e)}")

def export_employees_to_excel(employees, output=None):
    """
    Export employees to Excel file
    
    Args:
        employees: List of Employee objects
        output: BytesIO object to write to (optional)
        
    Returns:
        BytesIO object containing the Excel file
    """
    return generate_employee_excel(employees, output)
    
def generate_employee_excel(employees, output=None):
    """
    Generate Excel file from employee data
    
    Args:
        employees: List of Employee objects
        output: BytesIO object to write to (optional)
        
    Returns:
        BytesIO object containing the Excel file
    """
    try:
        # إنشاء بيانات لملف Excel بنفس ترتيب النموذج الأصلي
        data = []
        for employee in employees:
            # ترتيب البيانات حسب النموذج الأصلي - تم تصحيح ترتيب الأعمدة
            # Name, ID Number (هوية), Emp .N (رقم موظف), No.Mobile, Job Title, Status, Location, Project, Email
            row = {
                'Name': employee.name,  # الاسم
                'ID Number': employee.national_id,  # رقم الهوية
                'Emp .N': employee.employee_id,  # رقم الموظف
                'No.Mobile': employee.mobile,  # رقم الجوال
                'Job Title': employee.job_title,  # المسمى الوظيفي
                'Status': employee.status,  # الحالة
                'Location': employee.location or '',  # الموقع
                'Project': employee.project or '',  # المشروع
                'Email': employee.email or '',  # البريد الإلكتروني
                # معلومات إضافية في أعمدة منفصلة
                'Department': employee.department.name if employee.department else '',  # القسم
                'Join Date': employee.join_date if employee.join_date else ''  # تاريخ الانضمام
            }
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Write to Excel using openpyxl engine
        if output is None:
            # إذا لم يتم توفير output، قم بإنشاء كائن BytesIO جديد
            output = BytesIO()
            
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Employees', index=False)
            
            # Auto-adjust columns' width (openpyxl method)
            worksheet = writer.sheets['Employees']
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                # For openpyxl, column dimensions are one-based
                column_letter = chr(65 + i)  # A, B, C, ...
                worksheet.column_dimensions[column_letter].width = column_width
        
        output.seek(0)
        return output
    
    except Exception as e:
        print(f"خطأ في إنشاء ملف Excel: {str(e)}")
        raise Exception(f"Error generating Excel file: {str(e)}")

def parse_salary_excel(file, month, year):
    """
    Parse Excel file containing salary data
    
    Args:
        file: The uploaded Excel file
        month: The month for these salaries
        year: The year for these salaries
        
    Returns:
        List of dictionaries containing salary data
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read the Excel file explicitly using openpyxl engine
        df = pd.read_excel(file, engine='openpyxl')
        
        # Print column names for debugging
        print(f"Salary Excel columns: {df.columns.tolist()}")
        
        # Create a mapping for column detection
        column_mappings = {
            'employee_id': ['employee_id', 'employee id', 'emp id', 'employee number', 'emp no', 'emp.id', 'emp.no', 'emp .n', 'رقم الموظف', 'معرف الموظف', 'الرقم الوظيفي'],
            'basic_salary': ['basic_salary', 'basic salary', 'salary', 'راتب', 'الراتب', 'الراتب الأساسي'],
            'allowances': ['allowances', 'بدل', 'بدلات', 'البدلات'],
            'deductions': ['deductions', 'خصم', 'خصومات', 'الخصومات'],
            'bonus': ['bonus', 'مكافأة', 'علاوة', 'مكافآت'],
            'notes': ['notes', 'ملاحظات']
        }
        
        # Map columns to their normalized names
        detected_columns = {}
        for col in df.columns:
            if isinstance(col, datetime):
                continue
                
            col_str = str(col).lower().strip()
            
            # Check for exact column name or common variations
            for field, variations in column_mappings.items():
                if col_str in variations or any(var in col_str for var in variations):
                    detected_columns[field] = col
                    print(f"Detected '{field}' column: {col}")
                    break
        
        # Handle special case for Excel files with specific column names
        explicit_mappings = {
            'Employee ID': 'employee_id',
            'Emp .N': 'employee_id',  # شكل آخر لرقم الموظف
            'Basic Salary': 'basic_salary',
            'Allowances': 'allowances',
            'Deductions': 'deductions',
            'Bonus': 'bonus',
            'Notes': 'notes'
        }
        
        for excel_col, field in explicit_mappings.items():
            if excel_col in df.columns:
                detected_columns[field] = excel_col
                print(f"Explicitly mapped '{excel_col}' to '{field}'")
        
        # Print final column mapping
        print(f"Final salary column mapping: {detected_columns}")
        
        # تقسيم الحقول المطلوبة إلى أساسية وغير أساسية
        essential_fields = ['employee_id']  # رقم الموظف هو الأساسي الوحيد الضروري دائماً
        other_fields = ['basic_salary', 'allowances', 'deductions', 'bonus']  # يمكن وضع قيم افتراضية لها
        
        # التحقق من الحقول الأساسية
        missing_essential = [field for field in essential_fields if field not in detected_columns]
        if missing_essential:
            missing_str = ", ".join(missing_essential)
            raise ValueError(f"Required columns missing: {missing_str}. Available columns: {[c for c in df.columns if not isinstance(c, datetime)]}")
        
        # بالنسبة للحقول غير الأساسية المفقودة، سننشئ أعمدة وهمية تحتوي على قيم افتراضية
        for field in other_fields:
            if field not in detected_columns:
                print(f"Warning: Creating default column for: {field}")
                dummy_column_name = f"__{field}__default"
                df[dummy_column_name] = 0  # إنشاء عمود فارغ (0 للقيم المالية)
                detected_columns[field] = dummy_column_name  # تعيين العمود الوهمي للحقل
        
        # Process each row
        salaries = []
        for idx, row in df.iterrows():
            try:
                # Skip completely empty rows
                if row.isnull().all():
                    continue
                
                # Get employee_id field
                emp_id_col = detected_columns['employee_id']
                emp_id = row[emp_id_col]
                
                # Skip rows with missing employee_id
                if pd.isna(emp_id):
                    print(f"Skipping row {idx+1} due to missing employee ID")
                    continue
                
                # Try to convert employee_id to integer
                try:
                    employee_id = int(emp_id)
                except (ValueError, TypeError):
                    # If not convertible to int, use as string (could be employee code)
                    employee_id = str(emp_id).strip()
                
                # Get basic_salary field
                basic_salary_col = detected_columns['basic_salary']
                basic_salary_val = row[basic_salary_col]
                
                # تعامل مع القيم المفقودة أو غير الرقمية للراتب الأساسي
                if pd.isna(basic_salary_val) or not isinstance(basic_salary_val, (int, float)):
                    print(f"Row {idx+1}: Using default value of 0 for basic salary")
                    basic_salary_val = 0
                
                basic_salary = float(basic_salary_val)
                
                # Get optional fields with default values
                allowances = 0.0
                deductions = 0.0
                bonus = 0.0
                notes = ''
                
                # Extract allowances if column exists
                if 'allowances' in detected_columns and not pd.isna(row[detected_columns['allowances']]):
                    try:
                        allowances = float(row[detected_columns['allowances']])
                    except (ValueError, TypeError):
                        allowances = 0.0
                
                # Extract deductions if column exists
                if 'deductions' in detected_columns and not pd.isna(row[detected_columns['deductions']]):
                    try:
                        deductions = float(row[detected_columns['deductions']])
                    except (ValueError, TypeError):
                        deductions = 0.0
                
                # Extract bonus if column exists
                if 'bonus' in detected_columns and not pd.isna(row[detected_columns['bonus']]):
                    try:
                        bonus = float(row[detected_columns['bonus']])
                    except (ValueError, TypeError):
                        bonus = 0.0
                
                # Extract notes if column exists
                if 'notes' in detected_columns and not pd.isna(row[detected_columns['notes']]):
                    notes = str(row[detected_columns['notes']])
                
                # Calculate net salary
                net_salary = basic_salary + allowances + bonus - deductions
                
                # Create salary dictionary
                salary = {
                    'employee_id': employee_id,
                    'month': month,
                    'year': year,
                    'basic_salary': basic_salary,
                    'allowances': allowances,
                    'deductions': deductions,
                    'bonus': bonus,
                    'net_salary': net_salary
                }
                
                if notes:
                    salary['notes'] = notes
                
                print(f"Processed salary for employee ID: {employee_id}")
                salaries.append(salary)
                
            except Exception as e:
                print(f"Error processing salary row {idx+1}: {str(e)}")
                # Continue to next row instead of failing the entire import
                continue
        
        if not salaries:
            raise ValueError("No valid salary records found in the Excel file")
            
        return salaries
    
    except Exception as e:
        import traceback
        print(f"Error parsing salary Excel: {str(e)}")
        print(traceback.format_exc())
        raise Exception(f"Error parsing salary Excel file: {str(e)}")

def generate_salary_excel(salaries, filter_description=None):
    """
    إنشاء ملف Excel من بيانات الرواتب مع تنظيم وتجميع حسب القسم
    
    Args:
        salaries: قائمة كائنات Salary 
        filter_description: وصف مرشحات البحث المستخدمة (اختياري)
        
    Returns:
        كائن BytesIO يحتوي على ملف Excel
    """
    try:
        from datetime import datetime
        from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter
        
        # تجميع البيانات حسب القسم
        departments_data = {}
        for salary in salaries:
            dept_name = salary.employee.department.name
            if dept_name not in departments_data:
                departments_data[dept_name] = []
            
            # إضافة بيانات الراتب إلى القسم المناسب
            departments_data[dept_name].append({
                'معرف': salary.id,
                'اسم الموظف': salary.employee.name,
                'رقم الموظف': salary.employee.employee_id,
                'الوظيفة': salary.employee.job_title or '',
                'القسم': dept_name,
                'الشهر': salary.month,
                'السنة': salary.year,
                'الراتب الأساسي': salary.basic_salary,
                'البدلات': salary.allowances,
                'الخصومات': salary.deductions,
                'المكافآت': salary.bonus,
                'صافي الراتب': salary.net_salary,
                'ملاحظات': salary.notes or ''
            })
        
        # إنشاء ملف Excel باستخدام openpyxl
        output = BytesIO()
        with pd.ExcelWriter(path=output, engine='openpyxl') as writer:
            # إضافة ورقة التلخيص
            summary_data = []
            total_salaries = 0
            total_basic = 0
            total_allowances = 0
            total_deductions = 0
            total_bonus = 0
            total_net = 0
            
            # حساب المجاميع لكل قسم
            for dept_name, dept_salaries in departments_data.items():
                dept_count = len(dept_salaries)
                dept_basic_sum = sum(s['الراتب الأساسي'] for s in dept_salaries)
                dept_allowances_sum = sum(s['البدلات'] for s in dept_salaries)
                dept_deductions_sum = sum(s['الخصومات'] for s in dept_salaries)
                dept_bonus_sum = sum(s['المكافآت'] for s in dept_salaries)
                dept_net_sum = sum(s['صافي الراتب'] for s in dept_salaries)
                
                summary_data.append({
                    'القسم': dept_name,
                    'عدد الموظفين': dept_count,
                    'إجمالي الرواتب الأساسية': dept_basic_sum,
                    'إجمالي البدلات': dept_allowances_sum,
                    'إجمالي الخصومات': dept_deductions_sum,
                    'إجمالي المكافآت': dept_bonus_sum,
                    'إجمالي صافي الرواتب': dept_net_sum
                })
                
                # تحديث المجاميع الكلية
                total_salaries += dept_count
                total_basic += dept_basic_sum
                total_allowances += dept_allowances_sum
                total_deductions += dept_deductions_sum
                total_bonus += dept_bonus_sum
                total_net += dept_net_sum
            
            # إضافة صف المجموع الكلي
            summary_data.append({
                'القسم': 'الإجمالي',
                'عدد الموظفين': total_salaries,
                'إجمالي الرواتب الأساسية': total_basic,
                'إجمالي البدلات': total_allowances,
                'إجمالي الخصومات': total_deductions,
                'إجمالي المكافآت': total_bonus,
                'إجمالي صافي الرواتب': total_net
            })
            
            # إنشاء DataFrame للملخص
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='ملخص الرواتب', index=False)
            
            # تنسيق ورقة الملخص
            summary_sheet = writer.sheets['ملخص الرواتب']
            for i, col in enumerate(summary_df.columns):
                column_width = max(summary_df[col].astype(str).map(len).max(), len(col)) + 4
                column_letter = get_column_letter(i + 1)
                summary_sheet.column_dimensions[column_letter].width = column_width
            
            # إنشاء ورقة عمل لكل قسم
            for dept_name, dept_salaries in departments_data.items():
                dept_df = pd.DataFrame(dept_salaries)
                
                # ترتيب الأعمدة بشكل منطقي
                ordered_columns = [
                    'معرف', 'اسم الموظف', 'رقم الموظف', 'الوظيفة', 'القسم',
                    'الشهر', 'السنة', 'الراتب الأساسي', 'البدلات', 'الخصومات',
                    'المكافآت', 'صافي الراتب', 'ملاحظات'
                ]
                
                # إعادة ترتيب الأعمدة واستبعاد الأعمدة غير الموجودة
                actual_columns = [col for col in ordered_columns if col in dept_df.columns]
                dept_df = dept_df[actual_columns]
                
                # إضافة ورقة العمل للقسم
                sheet_name = dept_name[:31]  # تقليص اسم الورقة إلى 31 حرف (أقصى طول مسموح في Excel)
                dept_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # ضبط عرض الأعمدة في ورقة القسم
                dept_sheet = writer.sheets[sheet_name]
                for i, col in enumerate(actual_columns):
                    column_width = max(dept_df[col].astype(str).map(len).max(), len(col)) + 4
                    column_letter = get_column_letter(i + 1)
                    dept_sheet.column_dimensions[column_letter].width = column_width
            
            # إنشاء ورقة لجميع الرواتب
            all_data = []
            for dept_salaries in departments_data.values():
                all_data.extend(dept_salaries)
            
            if all_data:
                all_df = pd.DataFrame(all_data)
                
                # ترتيب الأعمدة بشكل منطقي
                all_columns = [col for col in ordered_columns if col in all_df.columns]
                all_df = all_df[all_columns]
                
                # إضافة ورقة كل الرواتب
                all_df.to_excel(writer, sheet_name='جميع الرواتب', index=False)
                
                # ضبط عرض الأعمدة
                all_sheet = writer.sheets['جميع الرواتب']
                for i, col in enumerate(all_columns):
                    column_width = max(all_df[col].astype(str).map(len).max(), len(col)) + 4
                    column_letter = get_column_letter(i + 1)
                    all_sheet.column_dimensions[column_letter].width = column_width
            
            # إضافة ورقة المعلومات
            info_data = []
            
            # إضافة معلومات التصفية
            if filter_description:
                info_data.append({
                    'المعلومة': 'مرشحات البحث',
                    'القيمة': ' - '.join(filter_description)
                })
            
            # إضافة معلومات عامة
            info_data.append({
                'المعلومة': 'تاريخ التصدير',
                'القيمة': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            info_data.append({
                'المعلومة': 'إجمالي عدد الرواتب',
                'القيمة': len(salaries)
            })
            
            info_data.append({
                'المعلومة': 'عدد الأقسام',
                'القيمة': len(departments_data)
            })
            
            info_df = pd.DataFrame(info_data)
            info_df.to_excel(writer, sheet_name='معلومات التقرير', index=False)
            
            # ضبط عرض الأعمدة في ورقة المعلومات
            info_sheet = writer.sheets['معلومات التقرير']
            for i, col in enumerate(info_df.columns):
                column_width = max(info_df[col].astype(str).map(len).max(), len(col)) + 4
                column_letter = get_column_letter(i + 1)
                info_sheet.column_dimensions[column_letter].width = column_width
        
        output.seek(0)
        return output
    
    except Exception as e:
        raise Exception(f"خطأ في إنشاء ملف Excel: {str(e)}")

def parse_document_excel(file):
    """
    Parse Excel file containing document data
    
    Args:
        file: The uploaded Excel file
        
    Returns:
        List of dictionaries containing document data
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read the Excel file explicitly using openpyxl engine
        df = pd.read_excel(file, engine='openpyxl')
        
        # Print column names for debugging
        print(f"Document Excel columns: {df.columns.tolist()}")
        
        # Create a mapping for column detection
        column_mappings = {
            'employee_id': ['employee_id', 'employee id', 'emp id', 'employee number', 'emp no', 'emp.id', 'emp.no', 'رقم الموظف', 'معرف الموظف', 'الرقم الوظيفي'],
            'document_type': ['document_type', 'document type', 'type', 'doc type', 'نوع الوثيقة', 'نوع المستند', 'النوع'],
            'document_number': ['document_number', 'document no', 'doc number', 'doc no', 'رقم الوثيقة', 'رقم المستند'],
            'issue_date': ['issue_date', 'issue date', 'start date', 'تاريخ الإصدار', 'تاريخ البدء'],
            'expiry_date': ['expiry_date', 'expiry date', 'end date', 'valid until', 'تاريخ الانتهاء', 'صالح حتى'],
            'notes': ['notes', 'comments', 'remarks', 'ملاحظات', 'تعليقات']
        }
        
        # Map columns to their normalized names
        detected_columns = {}
        for col in df.columns:
            if isinstance(col, datetime):
                continue
                
            col_str = str(col).lower().strip()
            
            # Check for exact column name or common variations
            for field, variations in column_mappings.items():
                if col_str in variations or any(var in col_str for var in variations):
                    detected_columns[field] = col
                    print(f"Detected '{field}' column: {col}")
                    break
        
        # Handle special case for Excel files with specific column names
        explicit_mappings = {
            'Employee ID': 'employee_id',
            'Document Type': 'document_type',
            'Document Number': 'document_number',
            'Issue Date': 'issue_date',
            'Expiry Date': 'expiry_date',
            'Notes': 'notes'
        }
        
        for excel_col, field in explicit_mappings.items():
            if excel_col in df.columns:
                detected_columns[field] = excel_col
                print(f"Explicitly mapped '{excel_col}' to '{field}'")
        
        # Print final column mapping
        print(f"Final document column mapping: {detected_columns}")
        
        # تقسيم الحقول المطلوبة إلى أساسية وغير أساسية
        essential_fields = ['employee_id', 'document_type', 'document_number']  # الحقول الأساسية التي يجب توفرها
        other_fields = ['issue_date', 'expiry_date', 'notes']  # الحقول التي يمكن إضافة قيم افتراضية لها
        
        # التحقق من الحقول الأساسية
        missing_essential = [field for field in essential_fields if field not in detected_columns]
        if missing_essential:
            missing_str = ", ".join(missing_essential)
            raise ValueError(f"Required columns missing: {missing_str}. Available columns: {[c for c in df.columns if not isinstance(c, datetime)]}")
        
        # بالنسبة للحقول غير الأساسية المفقودة، سننشئ أعمدة وهمية تحتوي على قيم افتراضية
        for field in other_fields:
            if field not in detected_columns:
                print(f"Warning: Creating default column for: {field}")
                dummy_column_name = f"__{field}__default"
                # إذا كان الحقل هو تاريخ، نضيف تاريخ افتراضي (اليوم للإصدار، وبعد سنة للانتهاء)
                if field == 'issue_date':
                    default_value = datetime.now()
                elif field == 'expiry_date':
                    default_value = datetime.now() + timedelta(days=365)
                else:
                    default_value = ''  # للملاحظات
                
                df[dummy_column_name] = default_value
                detected_columns[field] = dummy_column_name  # تعيين العمود الوهمي للحقل
        
        # Process each row
        documents = []
        for idx, row in df.iterrows():
            try:
                # Skip completely empty rows
                if row.isnull().all():
                    continue
                
                # Get employee_id field
                emp_id_col = detected_columns['employee_id']
                emp_id = row[emp_id_col]
                
                # Skip rows with missing employee_id
                if pd.isna(emp_id):
                    print(f"Skipping row {idx+1} due to missing employee ID")
                    continue
                
                # Try to convert employee_id to integer
                try:
                    employee_id = int(emp_id)
                except (ValueError, TypeError):
                    # If not convertible to int, use as string (could be employee code)
                    employee_id = str(emp_id).strip()
                
                # Get document type and number
                doc_type_col = detected_columns['document_type']
                doc_type = row[doc_type_col]
                
                doc_number_col = detected_columns['document_number']
                doc_number = row[doc_number_col]
                
                # Skip rows with missing document type or number
                if pd.isna(doc_type) or pd.isna(doc_number):
                    print(f"Skipping row {idx+1} due to missing document type or number")
                    continue
                
                # Get dates and parse them
                issue_date_col = detected_columns['issue_date']
                expiry_date_col = detected_columns['expiry_date']
                
                # تعامل مع التواريخ المفقودة - استخدام تاريخ اليوم للإصدار وبعد سنة للانتهاء
                if pd.isna(row[issue_date_col]):
                    print(f"Row {idx+1}: Using today's date for missing issue date")
                    issue_date_val = datetime.now()
                else:
                    issue_date_val = row[issue_date_col]
                    
                if pd.isna(row[expiry_date_col]):
                    print(f"Row {idx+1}: Using date one year from today for missing expiry date")
                    expiry_date_val = datetime.now() + timedelta(days=365)
                else:
                    expiry_date_val = row[expiry_date_col]
                
                try:
                    # Handle different date formats and convert to datetime
                    if isinstance(issue_date_val, datetime):
                        issue_date = issue_date_val
                    else:
                        issue_date = parse_date(str(issue_date_val))
                        
                    if isinstance(expiry_date_val, datetime):
                        expiry_date = expiry_date_val
                    else:
                        expiry_date = parse_date(str(expiry_date_val))
                    
                    # استخدام تواريخ افتراضية في حالة فشل تحليل التواريخ
                    if not issue_date:
                        print(f"Row {idx+1}: Using today's date due to invalid issue date format")
                        issue_date = datetime.now()
                        
                    if not expiry_date:
                        print(f"Row {idx+1}: Using date one year from today due to invalid expiry date format")
                        expiry_date = datetime.now() + timedelta(days=365)
                        
                except (ValueError, TypeError) as e:
                    print(f"Row {idx+1}: Date parsing error: {str(e)}, using default dates")
                    issue_date = datetime.now()
                    expiry_date = datetime.now() + timedelta(days=365)
                
                # Create document dictionary
                document = {
                    'employee_id': employee_id,
                    'document_type': str(doc_type).strip(),
                    'document_number': str(doc_number).strip(),
                    'issue_date': issue_date,
                    'expiry_date': expiry_date
                }
                
                # Add notes if present
                if 'notes' in detected_columns and not pd.isna(row[detected_columns['notes']]):
                    document['notes'] = str(row[detected_columns['notes']])
                
                print(f"Processed document for employee ID: {employee_id}, type: {document['document_type']}")
                documents.append(document)
                
            except Exception as e:
                print(f"Error processing document row {idx+1}: {str(e)}")
                # Continue to next row instead of failing the entire import
                continue
        
        if not documents:
            raise ValueError("No valid document records found in the Excel file")
            
        return documents
    
    except Exception as e:
        import traceback
        print(f"Error parsing document Excel: {str(e)}")
        print(traceback.format_exc())
        raise Exception(f"Error parsing document Excel file: {str(e)}")

def export_employee_attendance_to_excel(employee, month=None, year=None):
    """
    تصدير بيانات الحضور لموظف معين إلى ملف إكسل
    
    Args:
        employee: كائن الموظف
        month: الشهر (اختياري)
        year: السنة (اختياري)
        
    Returns:
        BytesIO object containing the Excel file
    """
    try:
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # اختصار اسم ورقة Excel لتكون أقل من 31 حرفاً (الحد الأقصى المسموح به)
        sheet_name = f"Attendance-{employee.employee_id}"
        worksheet = workbook.add_worksheet(sheet_name)
        
        # تنسيقات الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })
        
        date_header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True  # لسماح النص بالانتقال للسطر التالي
        })
        
        normal_format = workbook.add_format({
            'align': 'center',
            'border': 1
        })
        
        present_format = workbook.add_format({
            'align': 'center',
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'border': 1
        })
        
        absent_format = workbook.add_format({
            'align': 'center',
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'border': 1
        })
        
        leave_format = workbook.add_format({
            'align': 'center',
            'bg_color': '#FFEB9C',
            'font_color': '#9C5700',
            'border': 1
        })
        
        sick_format = workbook.add_format({
            'align': 'center',
            'bg_color': '#FFCC99',
            'font_color': '#974706',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # تحديد الشهر والسنة إذا لم يتم توفيرهما
        current_date = datetime.now()
        if not year:
            year = current_date.year
        if not month:
            month = current_date.month
            
        # الحصول على عدد أيام الشهر
        _, days_in_month = monthrange(year, month)
        
        # إنشاء عنوان الملف
        title = f"سجل حضور {employee.name}"
        
        # إضافة عنوان
        worksheet.merge_range('A1:H1', title, title_format)
        
        # تحديد أسماء الأعمدة الثابتة وترتيبها كما في الصورة
        col_headers = ["Name", "ID Number", "Emp. No.", "Job Title", "Location", "Project", "Total"]
        
        # كتابة العناوين الرئيسية
        for col_idx, header in enumerate(col_headers):
            worksheet.write(2, col_idx, header, header_format)
        
        # تحديد نطاق التواريخ للشهر المحدد
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # استخدام استعلام أكثر فعالية للحصول على سجلات الحضور
        from app import db
        from models import Attendance
        
        # استعلام من قاعدة البيانات مباشرة
        attendances = db.session.query(Attendance).filter(
            Attendance.employee_id == employee.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date).all()
        
        # تخزين بيانات الحضور في قاموس للوصول السريع وإنشاء قائمة بالتواريخ الفعلية للحضور
        attendance_data = {}
        date_list = []  # فقط التواريخ التي يوجد بها سجلات حضور
        
        for attendance in attendances:
            # تخزين معلومات الحضور
            attendance_data[attendance.date] = {
                'status': attendance.status,
                'notes': attendance.notes if hasattr(attendance, 'notes') else None
            }
            # إضافة التاريخ إلى قائمة التواريخ
            date_list.append(attendance.date)
        
        # إعداد أيام الأسبوع
        weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        
        # كتابة عناوين أيام الأسبوع
        first_date_col = len(col_headers)
        
        # إنشاء الصف الأول بعناوين أيام الأسبوع
        for col_idx, date in enumerate(date_list):
            # تنسيق عنوان اليوم ليظهر كما في الصورة المرفقة: يوم الأسبوع مع التاريخ (مثال: Mon 01/04/2025)
            day_of_week = weekdays[date.weekday()]
            date_str = date.strftime("%d/%m/%Y")
            day_header = f"{day_of_week}\n{date_str}"
            
            col = first_date_col + col_idx
            worksheet.write(2, col, day_header, date_header_format)
        
        # كتابة معلومات الموظف والحضور
        row = 3  # البدء من الصف الرابع بعد عنوان الجدول
        
        # استخراج معلومات لموقع العمل والمشروع
        location = "AL QASSIM"  # قيمة افتراضية أو استخراجها من الموظف
        if hasattr(employee, 'department') and employee.department:
            location = employee.department.name[:20]  # استخدام اسم القسم كموقع
            
        project = "ARAMEX"  # قيمة افتراضية، يمكن استخراجها من بيانات الموظف
        
        # عدد الحضور
        present_days = 0
        
        # كتابة معلومات الموظف
        worksheet.write(row, 0, employee.name, normal_format)  # Name
        worksheet.write(row, 1, employee.national_id or "", normal_format)  # ID Number
        worksheet.write(row, 2, employee.employee_id or "", normal_format)  # Emp. No.
        worksheet.write(row, 3, employee.job_title or "courier", normal_format)  # Job Title
        worksheet.write(row, 4, location, normal_format)  # Location
        worksheet.write(row, 5, project, normal_format)  # Project
        
        # كتابة سجلات الحضور لكل يوم
        for col_idx, date in enumerate(date_list):
            col = first_date_col + col_idx  # بداية أعمدة التواريخ
            cell_value = ""  # القيمة الافتراضية فارغة
            cell_format = normal_format
            
            if date in attendance_data:
                att_data = attendance_data[date]
                
                if att_data['status'] == 'present':
                    cell_value = "P"  # استخدام حرف P للحضور
                    cell_format = present_format
                    present_days += 1
                elif att_data['status'] == 'absent':
                    cell_value = "A"  # استخدام حرف A للغياب
                    cell_format = absent_format
                elif att_data['status'] == 'leave':
                    cell_value = "L"  # استخدام حرف L للإجازة
                    cell_format = leave_format
                elif att_data['status'] == 'sick':
                    cell_value = "S"  # استخدام حرف S للمرض
                    cell_format = sick_format
            # لا نحتاج للحالة else هنا لأن date_list تحتوي فقط على التواريخ التي لها سجلات حضور فعلية
            
            worksheet.write(row, col, cell_value, cell_format)
        
        # كتابة إجمالي أيام الحضور
        worksheet.write(row, 6, present_days, normal_format)  # Total
        
        # إضافة تفسير للرموز المستخدمة في صفحة منفصلة
        legend_sheet = workbook.add_worksheet('دليل الرموز')
        
        # تنسيق العناوين
        legend_title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # تنسيق الشرح
        description_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # كتابة العنوان
        legend_sheet.merge_range('A1:B1', 'دليل رموز الحضور والغياب', legend_title_format)
        
        # ضبط عرض الأعمدة
        legend_sheet.set_column(0, 0, 10)
        legend_sheet.set_column(1, 1, 40)
        
        # إضافة تفسير الرموز
        legend_sheet.write(2, 0, 'P', present_format)
        legend_sheet.write(2, 1, 'حاضر (Present)', description_format)
        
        legend_sheet.write(3, 0, 'A', absent_format)
        legend_sheet.write(3, 1, 'غائب (Absent)', description_format)
        
        legend_sheet.write(4, 0, 'L', leave_format)
        legend_sheet.write(4, 1, 'إجازة (Leave)', description_format)
        
        legend_sheet.write(5, 0, 'S', sick_format)
        legend_sheet.write(5, 1, 'مرضي (Sick Leave)', description_format)
        
        # ضبط عرض الأعمدة في الصفحة الرئيسية
        worksheet.set_column(0, 0, 30)  # عمود الاسم
        worksheet.set_column(1, 1, 15)  # عمود ID Number
        worksheet.set_column(2, 2, 10)  # عمود Emp. No.
        worksheet.set_column(3, 3, 15)  # عمود Job Title
        worksheet.set_column(4, 4, 13)  # عمود Location
        worksheet.set_column(5, 5, 13)  # عمود Project
        worksheet.set_column(6, 6, 8)   # عمود Total
        worksheet.set_column(first_date_col, first_date_col + len(date_list) - 1, 5)  # أعمدة التواريخ
        
        workbook.close()
        output.seek(0)
        return output
        
    except Exception as e:
        import traceback
        print(f"Error generating employee attendance Excel file: {str(e)}")
        print(traceback.format_exc())
        raise

def export_attendance_by_department(employees, attendances, start_date, end_date=None):
    """
    تصدير بيانات الحضور إلى ملف إكسل في صيغة جدول
    حيث تكون معلومات الموظفين في الأعمدة الأولى
    وتواريخ الحضور في الأعمدة الباقية مع استخدام P للحضور

    Args:
        employees: قائمة بجميع الموظفين
        attendances: قائمة بسجلات الحضور
        start_date: تاريخ البداية
        end_date: تاريخ النهاية (اختياري، إذا لم يتم تحديده سيتم استخدام تاريخ البداية فقط)

    Returns:
        BytesIO: كائن يحتوي على ملف اكسل
    """
    try:
        output = BytesIO()
        
        # إنشاء ملف إكسل جديد باستخدام xlsxwriter
        workbook = xlsxwriter.Workbook(output)
        
        # تعريف التنسيقات
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#00B0B0',  # لون أخضر فاتح مائل للأزرق
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        date_header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#00B0B0',  # لون أخضر فاتح مائل للأزرق
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        normal_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        right_aligned_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })
        
        present_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_color': '#006100'  # اللون الأخضر لحرف P
        })
        
        absent_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'font_color': '#FF0000'  # اللون الأحمر لحرف A
        })
        
        leave_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FF9900'  # اللون البرتقالي لحرف L
        })
        
        sick_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#0070C0'  # اللون الأزرق لحرف S
        })
        
        # تحديد الفترة الزمنية
        if end_date is None:
            end_date = start_date
        
        # تحديد قائمة التواريخ
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        # تنظيم الموظفين حسب الأقسام
        departments = {}
        for employee in employees:
            dept_name = employee.department.name if employee.department else 'بدون قسم'
            if dept_name not in departments:
                departments[dept_name] = []
            departments[dept_name].append(employee)
        
        # تنظيم بيانات الحضور حسب الموظفين
        attendance_data = {}
        for attendance in attendances:
            emp_id = attendance.employee_id
            if emp_id not in attendance_data:
                attendance_data[emp_id] = {}
            
            # تخزين حالة الحضور لهذا اليوم
            attendance_data[emp_id][attendance.date] = {
                'status': attendance.status
            }
        
        # عمل قائمة بأيام الأسبوع للعناوين
        weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        
        # إنشاء ورقة عمل لكل قسم
        for dept_name, dept_employees in departments.items():
            # تحويل الاسم ليكون صالحًا كاسم ورقة Excel
            sheet_name = dept_name[:31]  # Excel يدعم حد أقصى 31 حرف لأسماء الأوراق
            worksheet = workbook.add_worksheet(sheet_name)
            
            # تحديد أسماء الأعمدة الثابتة وترتيبها كما في الصورة
            col_headers = ["Name", "ID Number", "Emp. No.", "Job Title", "No. Mobile", "Car", "Location", "Project", "Total"]
            
            # كتابة العناوين الرئيسية
            for col_idx, header in enumerate(col_headers):
                worksheet.write(1, col_idx, header, header_format)
            
            # كتابة عناوين أيام الأسبوع
            first_date_col = len(col_headers)
            
            # إنشاء الصف الأول بعناوين أيام الأسبوع
            for col_idx, date in enumerate(date_list):
                # تنسيق عنوان اليوم ليظهر كما في الصورة المرفقة: يوم الأسبوع مع التاريخ (مثال: Mon 01/04/2025)
                day_of_week = weekdays[date.weekday()]
                date_str = date.strftime("%d/%m/%Y")
                day_header = f"{day_of_week}\n{date_str}"
                
                col = first_date_col + col_idx
                worksheet.write(0, col, day_header, date_header_format)
                
                # لم نعد بحاجة لكتابة التاريخ في صف منفصل لأننا دمجناه مع اسم اليوم
            
            # ضبط عرض الأعمدة
            worksheet.set_column(0, 0, 30)  # عمود الاسم
            worksheet.set_column(1, 1, 15)  # عمود ID Number
            worksheet.set_column(2, 2, 10)  # عمود Emp. No.
            worksheet.set_column(3, 3, 15)  # عمود Job Title
            worksheet.set_column(4, 4, 15)  # عمود No. Mobile
            worksheet.set_column(5, 5, 13)  # عمود Car
            worksheet.set_column(6, 6, 13)  # عمود Location
            worksheet.set_column(7, 7, 13)  # عمود Project
            worksheet.set_column(8, 8, 8)   # عمود Total
            worksheet.set_column(first_date_col, first_date_col + len(date_list) - 1, 5)  # أعمدة التواريخ
            
            # كتابة بيانات الموظفين وسجلات الحضور
            for row_idx, employee in enumerate(sorted(dept_employees, key=lambda e: e.name)):
                row = row_idx + 2  # صف البيانات (بعد صفي العناوين)
                
                # استخراج رقم الهاتف من المعلومات الإضافية إن وجد
                phone_number = ""
                if hasattr(employee, 'phone'):
                    phone_number = employee.phone
                
                # كتابة معلومات الموظف
                worksheet.write(row, 0, employee.name, normal_format)  # Name
                worksheet.write(row, 1, employee.national_id or "", normal_format)  # ID Number
                worksheet.write(row, 2, employee.employee_id or "", normal_format)  # Emp. No.
                worksheet.write(row, 3, employee.job_title or "courier", normal_format)  # Job Title
                worksheet.write(row, 4, phone_number, normal_format)  # No. Mobile
                
                # معلومات إضافية (قد تحتاج لتكييفها حسب هيكل البيانات الفعلي)
                car = ""  # يمكن إضافة منطق لاستخراج رقم السيارة إن وجد
                worksheet.write(row, 5, car, normal_format)  # Car
                
                # أحضر اسم الموقع من القسم
                location = "AL QASSIM"  # قيمة افتراضية أو استخراجها من الموظف
                if employee.department:
                    location = employee.department.name[:20]  # استخدام اسم القسم كموقع
                worksheet.write(row, 6, location, normal_format)  # Location
                
                # اسم المشروع
                project = "ARAMEX"  # قيمة افتراضية، يمكن استخراجها من بيانات الموظف
                worksheet.write(row, 7, project, normal_format)  # Project
                
                # عداد للحضور
                present_days = 0
                
                # كتابة سجلات الحضور لكل يوم
                for col_idx, date in enumerate(date_list):
                    col = first_date_col + col_idx  # بداية أعمدة التواريخ
                    cell_value = ""  # القيمة الافتراضية فارغة
                    cell_format = normal_format
                    
                    if employee.id in attendance_data and date in attendance_data[employee.id]:
                        att_data = attendance_data[employee.id][date]
                        
                        if att_data['status'] == 'present':
                            cell_value = "P"  # استخدام حرف P للحضور
                            cell_format = present_format
                            present_days += 1
                        elif att_data['status'] == 'absent':
                            cell_value = "A"  # استخدام حرف A للغياب
                            cell_format = absent_format
                        elif att_data['status'] == 'leave':
                            cell_value = "L"  # استخدام حرف L للإجازة
                            cell_format = leave_format
                        elif att_data['status'] == 'sick':
                            cell_value = "S"  # استخدام حرف S للمرض
                            cell_format = sick_format
                    else:
                        # إذا لم يوجد سجل لهذا اليوم، نفترض أنه حاضر (كما في الصورة المرفقة)
                        cell_value = "P"
                        cell_format = present_format
                        present_days += 1
                    
                    worksheet.write(row, col, cell_value, cell_format)
                
                # كتابة إجمالي أيام الحضور
                worksheet.write(row, 8, present_days, normal_format)  # Total
        
        # إضافة تفسير للرموز المستخدمة في صفحة منفصلة
        legend_sheet = workbook.add_worksheet('دليل الرموز')
        
        # تنسيق العناوين
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # تنسيق الشرح
        description_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # كتابة العنوان
        legend_sheet.merge_range('A1:B1', 'دليل رموز الحضور والغياب', title_format)
        
        # ضبط عرض الأعمدة
        legend_sheet.set_column(0, 0, 10)
        legend_sheet.set_column(1, 1, 40)
        
        # إضافة تفسير الرموز
        legend_sheet.write(2, 0, 'P', present_format)
        legend_sheet.write(2, 1, 'حاضر (Present)', description_format)
        
        legend_sheet.write(3, 0, 'A', absent_format)
        legend_sheet.write(3, 1, 'غائب (Absent)', description_format)
        
        legend_sheet.write(4, 0, 'L', leave_format)
        legend_sheet.write(4, 1, 'إجازة (Leave)', description_format)
        
        legend_sheet.write(5, 0, 'S', sick_format)
        legend_sheet.write(5, 1, 'مرضي (Sick Leave)', description_format)
        
        # إغلاق الملف وإعادة المخرجات
        workbook.close()
        output.seek(0)
        return output
    
    except Exception as e:
        import traceback
        print(f"Error generating attendance Excel file: {str(e)}")
        print(traceback.format_exc())
        raise
