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
        
        # Standardize column names (convert to lowercase and replace spaces)
        # Create a copy of the dataframe with standardized column names
        df_standardized = df.copy()
        
        # Define column mapping for common variations
        column_mapping = {
            'name': ['name', 'Name', 'الاسم', 'اسم الموظف', 'employee name'],
            'employee_id': ['employee_id', 'emp id', 'emp.id', 'empid', 'employee id', 'رقم الموظف', 'الرقم الوظيفي', 'emp .n', 'emp. n', 'emp n'],
            'national_id': ['national_id', 'national id', 'natid', 'id number', 'رقم الهوية', 'الهوية', 'الرقم الوطني', 'id .n', 'id. n', 'id n'],
            'mobile': ['mobile', 'phone', 'cell', 'رقم الجوال', 'الجوال', 'phone number', 'mobil'],
            'job_title': ['job_title', 'job title', 'title', 'position', 'المسمى الوظيفي', 'الوظيفة'],
            'status': ['status', 'state', 'emp status', 'employee status', 'الحالة', 'حالة الموظف']
        }
        
        # Create a mapping from actual columns to standard columns
        actual_to_standard = {}
        
        # For each standard column, find if any of its variations exist in the dataframe
        for standard_col, variations in column_mapping.items():
            for var in variations:
                if var in df.columns:
                    actual_to_standard[var] = standard_col
                    break
        
        # If we couldn't find a standard column, check case-insensitive and strip spaces
        for standard_col, variations in column_mapping.items():
            if standard_col not in actual_to_standard.values():
                for col in df.columns:
                    col_clean = col.lower().strip().replace(' ', '_')
                    if col_clean in variations or col_clean == standard_col:
                        actual_to_standard[col] = standard_col
                        break
        
        print(f"Column mapping: {actual_to_standard}")
        
        # Apply the mapping to rename columns
        df_standardized = df.rename(columns=actual_to_standard)
        
        # Check required columns
        required_columns = ['name', 'employee_id', 'national_id', 'mobile', 
                           'job_title', 'status']
        
        for col in required_columns:
            if col not in df_standardized.columns:
                raise ValueError(f"Column '{col}' is missing from the Excel file. Available columns: {df.columns.tolist()}")
        
        # Process each row
        employees = []
        for _, row in df_standardized.iterrows():
            # Skip rows where required fields are missing
            if (pd.isna(row['name']) or pd.isna(row['employee_id']) or 
                pd.isna(row['national_id']) or pd.isna(row['mobile']) or
                pd.isna(row['job_title']) or pd.isna(row['status'])):
                continue
            
            # Create employee dictionary
            employee = {
                'name': str(row['name']),
                'employee_id': str(row['employee_id']),
                'national_id': str(row['national_id']),
                'mobile': str(row['mobile']),
                'job_title': str(row['job_title']),
                'status': str(row['status']).lower()
            }
            
            # Add optional fields if present
            if 'email' in df_standardized.columns and not pd.isna(row['email']):
                employee['email'] = str(row['email'])
            
            if 'location' in df_standardized.columns and not pd.isna(row['location']):
                employee['location'] = str(row['location'])
            
            if 'project' in df_standardized.columns and not pd.isna(row['project']):
                employee['project'] = str(row['project'])
            
            if 'department_id' in df_standardized.columns and not pd.isna(row['department_id']):
                employee['department_id'] = int(row['department_id'])
            
            if 'join_date' in df_standardized.columns and not pd.isna(row['join_date']):
                employee['join_date'] = parse_date(str(row['join_date']))
            
            employees.append(employee)
        
        return employees
    
    except Exception as e:
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
