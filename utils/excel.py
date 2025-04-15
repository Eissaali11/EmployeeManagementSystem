import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from utils.date_converter import parse_date

def parse_employee_excel(file):
    """
    Parse Excel file containing employee data
    
    Args:
        file: The uploaded Excel file
        
    Returns:
        List of dictionaries containing employee data
    """
    try:
        # Read the Excel file explicitly using openpyxl engine
        df = pd.read_excel(file, engine='openpyxl')
        
        # Print column names for debugging
        print(f"Excel columns: {df.columns.tolist()}")
        
        # Convert all columns to string to handle datetime objects
        for col in df.columns:
            if isinstance(col, datetime):
                continue  # Skip date columns completely
        
        # Manual detection of common column patterns - for Gulf/Saudi style Excel sheets
        name_col = None
        emp_id_col = None
        national_id_col = None
        mobile_col = None
        job_title_col = None
        status_col = None
        location_col = None
        project_col = None
        
        # Search for column names in Arabic and English with patterns
        for col in df.columns:
            if isinstance(col, datetime):
                continue
                
            col_str = str(col).lower()
            
            # Name
            if col_str in ['name', 'اسم', 'الاسم', 'اسم الموظف']:
                name_col = col
            
            # Employee ID
            elif ('emp' in col_str and ('.n' in col_str or 'id' in col_str or 'no' in col_str)) or col_str in ['رقم الموظف', 'الرقم الوظيفي']:
                emp_id_col = col
            
            # National ID
            elif ('id' in col_str and ('.n' in col_str or 'no' in col_str)) or 'national' in col_str or col_str in ['هوية', 'رقم الهوية', 'الرقم الوطني']:
                national_id_col = col
            
            # Mobile
            elif col_str in ['mobile', 'mobil', 'phone', 'جوال', 'رقم الجوال', 'هاتف']:
                mobile_col = col
            
            # Job Title
            elif ('job' in col_str and 'title' in col_str) or col_str in ['title', 'المسمى', 'المسمى الوظيفي', 'الوظيفة']:
                job_title_col = col
            
            # Status
            elif col_str in ['status', 'الحالة', 'حالة', 'حالة الموظف']:
                status_col = col
                
            # Location
            elif col_str in ['location', 'موقع', 'الموقع']:
                location_col = col
                
            # Project
            elif col_str in ['project', 'مشروع', 'المشروع']:
                project_col = col
        
        # Print detected columns
        print(f"Detected columns: Name={name_col}, ID={emp_id_col}, NationalID={national_id_col}, Mobile={mobile_col}, Job={job_title_col}, Status={status_col}")
        
        # Force these columns if specific patterns are found 
        # (This is for the specific file format you're using)
        if 'Name' in df.columns:
            name_col = 'Name'
            
        if 'Emp .N' in df.columns:
            emp_id_col = 'Emp .N'
            
        if 'ID .N' in df.columns:
            national_id_col = 'ID .N'
            
        if 'Mobil' in df.columns:
            mobile_col = 'Mobil'
            
        if 'Job Title' in df.columns:
            job_title_col = 'Job Title'
            
        if 'Status' in df.columns:
            status_col = 'Status'
            
        if 'Location' in df.columns:
            location_col = 'Location'
            
        if 'Project' in df.columns:
            project_col = 'Project'
                
        # Verify we found all required columns
        if not all([name_col, emp_id_col, national_id_col, mobile_col, job_title_col, status_col]):
            missing = []
            if not name_col: missing.append("Name")
            if not emp_id_col: missing.append("Employee ID")
            if not national_id_col: missing.append("National ID")
            if not mobile_col: missing.append("Mobile")
            if not job_title_col: missing.append("Job Title")
            if not status_col: missing.append("Status")
            
            missing_str = ", ".join(missing)
            raise ValueError(f"Required columns missing: {missing_str}. Available columns: {[c for c in df.columns if not isinstance(c, datetime)]}")
        
        # Process each row
        employees = []
        for idx, row in df.iterrows():
            # Skip rows with empty values in important fields
            if any(pd.isna(row[col]) for col in [name_col, emp_id_col, national_id_col, mobile_col, job_title_col]):
                continue
                
            # Default to 'active' status if it's a datetime object or empty
            if isinstance(row[status_col], datetime) or pd.isna(row[status_col]):
                status_value = 'active'
            else:
                status_value = str(row[status_col]).lower()
                
            # Create employee dictionary with required fields
            employee = {
                'name': str(row[name_col]),
                'employee_id': str(row[emp_id_col]),
                'national_id': str(row[national_id_col]),
                'mobile': str(row[mobile_col]),
                'job_title': str(row[job_title_col]),
                'status': status_value
            }
            
            # Add optional fields if present
            if location_col is not None and not pd.isna(row[location_col]):
                employee['location'] = str(row[location_col])
                
            if project_col is not None and not pd.isna(row[project_col]):
                employee['project'] = str(row[project_col])
            
            # We don't have email in this Excel format, so skip it
            
            employees.append(employee)
            print(f"Added employee: {employee['name']}")
        
        return employees
    
    except Exception as e:
        import traceback
        print(f"Error parsing Excel: {str(e)}")
        print(traceback.format_exc())
        raise Exception(f"Error parsing Excel file: {str(e)}")

def generate_employee_excel(employees):
    """
    Generate Excel file from employee data
    
    Args:
        employees: List of Employee objects
        
    Returns:
        BytesIO object containing the Excel file
    """
    try:
        # Create data for Excel file
        data = []
        for employee in employees:
            row = {
                'معرف الموظف': employee.id,
                'رقم الموظف': employee.employee_id,
                'الاسم': employee.name,
                'رقم الهوية': employee.national_id,
                'رقم الجوال': employee.mobile,
                'البريد الإلكتروني': employee.email or '',
                'المسمى الوظيفي': employee.job_title,
                'الحالة': employee.status,
                'الموقع': employee.location or '',
                'المشروع': employee.project or '',
                'القسم': employee.department.name if employee.department else '',
                'تاريخ الانضمام': employee.join_date if employee.join_date else ''
            }
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Write to Excel using openpyxl engine
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
        # Read the Excel file explicitly using openpyxl engine
        df = pd.read_excel(file, engine='openpyxl')
        
        # Print column names for debugging
        print(f"Salary Excel columns: {df.columns.tolist()}")
        
        # Basic validation
        required_columns = ['employee_id', 'basic_salary']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' is missing from the Excel file")
        
        # Process each row
        salaries = []
        for _, row in df.iterrows():
            # Skip rows where required fields are missing or invalid
            if (pd.isna(row['employee_id']) or pd.isna(row['basic_salary']) or
                not isinstance(row['basic_salary'], (int, float))):
                continue
            
            # Get optional fields
            allowances = row['allowances'] if 'allowances' in df.columns and not pd.isna(row['allowances']) else 0
            deductions = row['deductions'] if 'deductions' in df.columns and not pd.isna(row['deductions']) else 0
            bonus = row['bonus'] if 'bonus' in df.columns and not pd.isna(row['bonus']) else 0
            
            # Calculate net salary
            basic_salary = float(row['basic_salary'])
            net_salary = basic_salary + allowances + bonus - deductions
            
            # Create salary dictionary
            salary = {
                'employee_id': int(row['employee_id']),
                'month': month,
                'year': year,
                'basic_salary': basic_salary,
                'allowances': float(allowances),
                'deductions': float(deductions),
                'bonus': float(bonus),
                'net_salary': float(net_salary)
            }
            
            # Add notes if present
            if 'notes' in df.columns and not pd.isna(row['notes']):
                salary['notes'] = str(row['notes'])
            
            salaries.append(salary)
        
        return salaries
    
    except Exception as e:
        raise Exception(f"Error parsing Excel file: {str(e)}")

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
        # Read the Excel file explicitly using openpyxl engine
        df = pd.read_excel(file, engine='openpyxl')
        
        # Print column names for debugging
        print(f"Document Excel columns: {df.columns.tolist()}")
        
        # Basic validation
        required_columns = ['employee_id', 'document_type', 'document_number', 
                           'issue_date', 'expiry_date']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' is missing from the Excel file")
        
        # Process each row
        documents = []
        for _, row in df.iterrows():
            # Skip rows where required fields are missing
            if (pd.isna(row['employee_id']) or pd.isna(row['document_type']) or 
                pd.isna(row['document_number']) or pd.isna(row['issue_date']) or
                pd.isna(row['expiry_date'])):
                continue
            
            # Parse dates
            try:
                issue_date = parse_date(str(row['issue_date']))
                expiry_date = parse_date(str(row['expiry_date']))
            except ValueError:
                continue
            
            # Create document dictionary
            document = {
                'employee_id': int(row['employee_id']),
                'document_type': str(row['document_type']),
                'document_number': str(row['document_number']),
                'issue_date': issue_date,
                'expiry_date': expiry_date
            }
            
            # Add notes if present
            if 'notes' in df.columns and not pd.isna(row['notes']):
                document['notes'] = str(row['notes'])
            
            documents.append(document)
        
        return documents
    
    except Exception as e:
        raise Exception(f"Error parsing Excel file: {str(e)}")
