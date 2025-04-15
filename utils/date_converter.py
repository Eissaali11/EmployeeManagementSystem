import re
from datetime import datetime
from hijri_converter import convert

def parse_date(date_str):
    """
    Parse a date string in either Gregorian or Hijri format
    
    Args:
        date_str: Date string in format YYYY-MM-DD, DD/MM/YYYY, or Hijri format
        
    Returns:
        datetime.date object
    """
    # If empty string, return None
    if not date_str or date_str.strip() == '':
        return None
    
    # Try parsing as ISO format (YYYY-MM-DD)
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        pass
    
    # Try parsing as DD/MM/YYYY
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        pass
    
    # Check if it's a Hijri date (contains 'هـ')
    if 'هـ' in date_str:
        # Extract year, month, day from hijri date
        pattern = r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
        match = re.search(pattern, date_str)
        if match:
            day, month, year = map(int, match.groups())
            try:
                # Convert Hijri to Gregorian
                gregorian_date = convert.Hijri(year, month, day).to_gregorian()
                return gregorian_date.date()
            except ValueError:
                pass
    
    # If all parsing attempts fail, raise error
    raise ValueError(f"Could not parse date: {date_str}")

def format_date_hijri(date):
    """
    Format a date object to Hijri date string
    
    Args:
        date: datetime.date object
        
    Returns:
        String in format DD/MM/YYYY هـ
    """
    if not date:
        return ''
    
    try:
        hijri_date = convert.Gregorian(date.year, date.month, date.day).to_hijri()
        return f"{hijri_date.day}/{hijri_date.month}/{hijri_date.year} هـ"
    except ValueError:
        return ''

def format_date_gregorian(date):
    """
    Format a date object to Gregorian date string
    
    Args:
        date: datetime.date object
        
    Returns:
        String in format DD/MM/YYYY
    """
    if not date:
        return ''
    
    try:
        return date.strftime('%d/%m/%Y')
    except:
        return ''

def get_month_name_ar(month_number):
    """
    Get Arabic name for a month number
    
    Args:
        month_number: Integer (1-12)
        
    Returns:
        Arabic month name
    """
    months = {
        1: 'يناير',
        2: 'فبراير',
        3: 'مارس',
        4: 'أبريل',
        5: 'مايو',
        6: 'يونيو',
        7: 'يوليو',
        8: 'أغسطس',
        9: 'سبتمبر',
        10: 'أكتوبر',
        11: 'نوفمبر',
        12: 'ديسمبر'
    }
    
    return months.get(month_number, '')

def get_hijri_month_name(month_number):
    """
    Get Arabic Hijri name for a month number
    
    Args:
        month_number: Integer (1-12)
        
    Returns:
        Arabic Hijri month name
    """
    months = {
        1: 'محرم',
        2: 'صفر',
        3: 'ربيع الأول',
        4: 'ربيع الثاني',
        5: 'جمادى الأولى',
        6: 'جمادى الآخرة',
        7: 'رجب',
        8: 'شعبان',
        9: 'رمضان',
        10: 'شوال',
        11: 'ذو القعدة',
        12: 'ذو الحجة'
    }
    
    return months.get(month_number, '')
