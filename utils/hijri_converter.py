"""
دوال تحويل التواريخ بين التقويم الميلادي والهجري
"""

from datetime import date
from hijri_converter import convert

def convert_gregorian_to_hijri(gregorian_date):
    """
    تحويل تاريخ من التقويم الميلادي إلى التقويم الهجري
    
    Args:
        gregorian_date: تاريخ ميلادي (datetime.date أو datetime.datetime)
        
    Returns:
        كائن تاريخ هجري
    """
    if not gregorian_date:
        return None
    
    # إذا كان التاريخ من نوع datetime، استخرج الجزء date منه
    if hasattr(gregorian_date, 'date'):
        gregorian_date = gregorian_date.date()
    
    try:
        hijri_date = convert.Gregorian(
            gregorian_date.year, 
            gregorian_date.month, 
            gregorian_date.day
        ).to_hijri()
        return hijri_date
    except Exception as e:
        print(f"خطأ في تحويل التاريخ الميلادي إلى هجري: {str(e)}")
        return None

def convert_hijri_to_gregorian(hijri_year, hijri_month, hijri_day):
    """
    تحويل تاريخ من التقويم الهجري إلى التقويم الميلادي
    
    Args:
        hijri_year: السنة الهجرية
        hijri_month: الشهر الهجري
        hijri_day: اليوم الهجري
        
    Returns:
        كائن datetime.date يمثل التاريخ الميلادي
    """
    try:
        gregorian_date = convert.Hijri(
            hijri_year, 
            hijri_month, 
            hijri_day
        ).to_gregorian()
        return date(gregorian_date.year, gregorian_date.month, gregorian_date.day)
    except Exception as e:
        print(f"خطأ في تحويل التاريخ الهجري إلى ميلادي: {str(e)}")
        return None

def format_hijri_date(hijri_date, format_type='full'):
    """
    تنسيق تاريخ هجري كنص
    
    Args:
        hijri_date: كائن التاريخ الهجري
        format_type: نوع التنسيق ('full' للتنسيق الكامل، 'short' للتنسيق المختصر)
        
    Returns:
        نص يمثل التاريخ الهجري بالتنسيق المطلوب
    """
    if not hijri_date:
        return ""
    
    # أسماء الأشهر العربية
    arabic_months = [
        "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
        "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
    ]
    
    # أيام الأسبوع بالعربية
    arabic_days = [
        "الاثنين", "الثلاثاء", "الأربعاء", "الخميس",
        "الجمعة", "السبت", "الأحد"
    ]
    
    if format_type == 'full':
        # التنسيق الكامل: اليوم، اليوم الشهر السنة هـ
        return f"{hijri_date.day} {arabic_months[hijri_date.month - 1]} {hijri_date.year} هـ"
    elif format_type == 'short':
        # التنسيق المختصر: اليوم/الشهر/السنة هـ
        return f"{hijri_date.day}/{hijri_date.month}/{hijri_date.year} هـ"
    else:
        # التنسيق الافتراضي
        return f"{hijri_date.day} {arabic_months[hijri_date.month - 1]} {hijri_date.year} هـ"