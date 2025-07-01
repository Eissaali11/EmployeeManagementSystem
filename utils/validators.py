"""
مساعدات التحقق من صحة البيانات
"""

import re
from typing import Dict, List, Any

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """التحقق من وجود الحقول المطلوبة"""
    errors = []
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            errors.append(f"الحقل '{field}' مطلوب")
    return errors

def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف السعودي"""
    if not phone:
        return True  # اختياري
    # رقم سعودي يبدأ بـ 05 أو +966
    pattern = r'^(\+966|0)?5[0-9]{8}$'
    return bool(re.match(pattern, phone))

def validate_national_id(national_id: str) -> bool:
    """التحقق من صحة رقم الهوية الوطنية السعودية"""
    if not national_id:
        return False
    # رقم هوية سعودي 10 أرقام
    if len(national_id) != 10 or not national_id.isdigit():
        return False
    
    # خوارزمية التحقق من رقم الهوية السعودية
    checksum = 0
    for i in range(9):
        if i % 2 == 0:
            checksum += int(national_id[i])
        else:
            double = int(national_id[i]) * 2
            checksum += double // 10 + double % 10
    
    return (checksum % 10) == int(national_id[9])

def validate_employee_id(employee_id: str) -> bool:
    """التحقق من صحة رقم الموظف"""
    if not employee_id:
        return False
    return len(employee_id) >= 3 and employee_id.isdigit()