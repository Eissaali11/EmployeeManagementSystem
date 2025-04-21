import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta
from utils.date_converter import parse_date
from calendar import monthrange

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
            'ID .N': 'employee_id',  # رقم الموظف بديل
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
                        print(f"تخمين: العمود الثاني '{columns_list[1]}' = رقم الهوية")
                    
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

def generate_salary_excel(salaries):
    """
    Generate Excel file from salary data
    
    Args:
        salaries: List of Salary objects
        
    Returns:
        BytesIO object containing the Excel file
    """
    try:
        # Create data for Excel file
        data = []
        for salary in salaries:
            row = {
                'معرف': salary.id,
                'اسم الموظف': salary.employee.name,
                'رقم الموظف': salary.employee.employee_id,
                'الشهر': salary.month,
                'السنة': salary.year,
                'الراتب الأساسي': salary.basic_salary,
                'البدلات': salary.allowances,
                'الخصومات': salary.deductions,
                'المكافآت': salary.bonus,
                'صافي الراتب': salary.net_salary,
                'ملاحظات': salary.notes or ''
            }
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Write to Excel using openpyxl engine
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Salaries', index=False)
            
            # Auto-adjust columns' width (openpyxl method)
            worksheet = writer.sheets['Salaries']
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                # For openpyxl, column dimensions are one-based
                column_letter = chr(65 + i)  # A, B, C, ...
                worksheet.column_dimensions[column_letter].width = column_width
        
        output.seek(0)
        return output
    
    except Exception as e:
        raise Exception(f"Error generating Excel file: {str(e)}")

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
        # تحديد الشهر والسنة إذا لم يتم توفيرهما
        current_date = datetime.now()
        if not year:
            year = current_date.year
        if not month:
            month = current_date.month
            
        # الحصول على عدد أيام الشهر
        _, days_in_month = monthrange(year, month)
        
        # إنشاء اسم الشهر بالعربية
        month_names_ar = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'إبريل', 5: 'مايو', 6: 'يونيو',
            7: 'يوليو', 8: 'أغسطس', 9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name_ar = month_names_ar.get(month, str(month))
        
        # إنشاء عنوان الملف
        title = f"سجل حضور {employee.name} - {month_name_ar} {year}"
        
        # إنشاء قاموس لسجلات الحضور مفهرسة بالتاريخ
        attendance_dict = {}
        
        # تحديد نطاق التواريخ للشهر المحدد
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, days_in_month).date()
        
        # فلترة سجلات الحضور للشهر المحدد
        attendances = []
        if employee.attendances:
            for attendance in employee.attendances:
                if start_date <= attendance.date <= end_date:
                    attendances.append(attendance)
                    attendance_dict[attendance.date.day] = attendance
        
        # تحضير البيانات للإكسل
        data = []
        status_map = {
            'present': 'حاضر',
            'absent': 'غائب',
            'leave': 'إجازة',
            'sick': 'مرضي'
        }
        
        # إضافة صف لكل يوم في الشهر
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day).date()
            
            # تخطي أيام العطلة الأسبوعية (الجمعة والسبت)
            is_weekend = date_obj.weekday() >= 5  # 5 = السبت، 6 = الأحد
            
            # إنشاء بيانات الصف
            attendance = attendance_dict.get(day)
            row = {
                'اليوم': day,
                'التاريخ': date_obj.strftime('%Y-%m-%d'),
                'اليوم من الأسبوع': date_obj.strftime('%A'),
                'الحالة': status_map.get(attendance.status, '') if attendance else ('عطلة أسبوعية' if is_weekend else ''),
                'وقت الحضور': attendance.check_in.strftime('%H:%M') if attendance and attendance.check_in else '',
                'وقت الانصراف': attendance.check_out.strftime('%H:%M') if attendance and attendance.check_out else '',
                'الملاحظات': attendance.notes if attendance and attendance.notes else ''
            }
            data.append(row)
        
        # إنشاء DataFrame
        df = pd.DataFrame(data)
        
        # معلومات الموظف
        employee_info = pd.DataFrame([{
            'البيان': 'معلومات الموظف',
            '': '',
            'الاسم': employee.name,
            'الرقم الوظيفي': employee.employee_id,
            'المسمى الوظيفي': employee.job_title,
            'القسم': employee.department.name if employee.department else '',
            'الشهر': f"{month_name_ar} {year}"
        }])
        
        # إحصائيات الحضور
        present_count = len([a for a in attendances if a.status == 'present'])
        absent_count = len([a for a in attendances if a.status == 'absent'])
        leave_count = len([a for a in attendances if a.status == 'leave'])
        sick_count = len([a for a in attendances if a.status == 'sick'])
        
        stats_info = pd.DataFrame([{
            'البيان': 'إحصائيات الحضور',
            '': '',
            'أيام الحضور': present_count,
            'أيام الغياب': absent_count,
            'أيام الإجازة': leave_count,
            'أيام المرضي': sick_count,
            'المجموع': present_count + absent_count + leave_count + sick_count
        }])
        
        # إنشاء ملف إكسل في الذاكرة
        output = BytesIO()
        
        # الكاتب
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # كتابة بيانات الموظف
            employee_info.to_excel(writer, sheet_name='تقرير الحضور', startrow=0, index=False)
            
            # كتابة إحصائيات الحضور
            stats_info.to_excel(writer, sheet_name='تقرير الحضور', startrow=3, index=False)
            
            # كتابة بيانات الحضور
            df.to_excel(writer, sheet_name='تقرير الحضور', startrow=7, index=False)
            
            # الحصول على ورقة العمل
            worksheet = writer.sheets['تقرير الحضور']
            
            # تنسيق ورقة العمل
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#D8E4BC',
                'border': 1
            })
            
            # تطبيق التنسيق على رؤوس الأعمدة
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(7, col_num, value, header_format)
            
            # ضبط عرض الأعمدة
            worksheet.set_column('A:G', 15)
            
            # إضافة عنوان للتقرير
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter'
            })
            worksheet.merge_range('A1:G1', title, title_format)
        
        # إعادة مؤشر الذاكرة إلى البداية
        output.seek(0)
        
        return output
    except Exception as e:
        import traceback
        print(f"Error generating attendance Excel file: {str(e)}")
        print(traceback.format_exc())
        raise
