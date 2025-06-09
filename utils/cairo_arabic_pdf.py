"""
مولد PDF بالعربية باستخدام خط Cairo المحمل مباشرة
"""

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import io
import os

def register_cairo_font():
    """تسجيل خط Cairo العربي"""
    try:
        font_path = 'Cairo.ttf'
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Cairo', font_path))
            return True
        
        # محاولة المسار البديل
        alt_font_path = 'static/fonts/Cairo-Regular.ttf'
        if os.path.exists(alt_font_path):
            pdfmetrics.registerFont(TTFont('Cairo', alt_font_path))
            return True
            
        return False
    except Exception as e:
        print(f"خطأ في تسجيل خط Cairo: {e}")
        return False

def format_arabic_text(text):
    """تنسيق النص العربي للعرض الصحيح"""
    if not text:
        return ""
    
    try:
        text_str = str(text)
        # إعادة تشكيل النص العربي
        reshaped_text = arabic_reshaper.reshape(text_str)
        # تطبيق خوارزمية الاتجاه الثنائي
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"خطأ في تنسيق النص العربي: {e}")
        return str(text)

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء PDF للورشة بخط Cairo العربي"""
    
    try:
        print("بدء إنشاء PDF بخط Cairo...")
        
        # تسجيل خط Cairo
        if not register_cairo_font():
            print("فشل في تسجيل خط Cairo، استخدام البديل...")
            from utils.simple_html_pdf import generate_workshop_pdf as fallback
            return fallback(vehicle, workshop_records)
        
        # إنشاء buffer للـ PDF
        buffer = io.BytesIO()
        
        # إنشاء canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # إعداد الخط
        c.setFont("Cairo", 16)
        
        # عنوان التقرير
        title = format_arabic_text(f"تقرير سجلات الورشة للمركبة: {vehicle.plate_number}")
        c.drawRightString(width - 50, height - 60, title)
        
        # معلومات المركبة
        c.setFont("Cairo", 14)
        vehicle_info = format_arabic_text(f"{vehicle.make} {vehicle.model} - سنة {vehicle.year}")
        c.drawRightString(width - 50, height - 90, vehicle_info)
        
        color_status = format_arabic_text(f"اللون: {vehicle.color} | الحالة: {get_status_arabic(vehicle.status)}")
        c.drawRightString(width - 50, height - 110, color_status)
        
        # خط فاصل
        c.setStrokeColor(colors.blue)
        c.setLineWidth(2)
        c.line(50, height - 130, width - 50, height - 130)
        
        # قسم معلومات المركبة
        y_position = height - 160
        c.setFont("Cairo", 12)
        
        vehicle_details = [
            (f"رقم اللوحة: {vehicle.plate_number}"),
            (f"الصنع والموديل: {vehicle.make} {vehicle.model}"),
            (f"سنة الصنع: {vehicle.year}"),
            (f"اللون: {vehicle.color}"),
            (f"الحالة الحالية: {get_status_arabic(vehicle.status)}")
        ]
        
        for detail in vehicle_details:
            formatted_detail = format_arabic_text(detail)
            c.drawRightString(width - 70, y_position, formatted_detail)
            y_position -= 25
        
        # سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            y_position -= 30
            c.setFont("Cairo", 14)
            records_title = format_arabic_text(f"سجلات الورشة ({len(workshop_records)} سجل)")
            c.drawRightString(width - 50, y_position, records_title)
            
            y_position -= 40
            c.setFont("Cairo", 10)
            
            # عرض السجلات
            total_cost = 0
            total_days = 0
            
            for i, record in enumerate(workshop_records):
                if y_position < 100:  # إنشاء صفحة جديدة
                    c.showPage()
                    c.setFont("Cairo", 10)
                    y_position = height - 80
                
                # تاريخ الدخول
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else "غير محدد"
                
                # تاريخ الخروج
                if record.exit_date:
                    exit_date = record.exit_date.strftime('%Y-%m-%d')
                else:
                    exit_date = "ما زالت في الورشة"
                
                # سبب الدخول وحالة الإصلاح
                reason = get_reason_arabic(record.reason)
                status = get_repair_status_arabic(record.repair_status)
                
                # التكلفة
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                
                # اسم الورشة والفني
                workshop_name = record.workshop_name if record.workshop_name else "غير محدد"
                technician = record.technician_name if record.technician_name else "غير محدد"
                
                # حساب الأيام
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                
                # عرض بيانات السجل
                record_line1 = format_arabic_text(f"السجل {i+1}: تاريخ الدخول: {entry_date} | تاريخ الخروج: {exit_date}")
                c.drawRightString(width - 70, y_position, record_line1)
                y_position -= 20
                
                record_line2 = format_arabic_text(f"سبب الدخول: {reason} | حالة الإصلاح: {status}")
                c.drawRightString(width - 70, y_position, record_line2)
                y_position -= 20
                
                record_line3 = format_arabic_text(f"التكلفة: {cost:,.0f} ريال | الورشة: {workshop_name}")
                c.drawRightString(width - 70, y_position, record_line3)
                y_position -= 20
                
                if technician != "غير محدد":
                    record_line4 = format_arabic_text(f"الفني المسؤول: {technician}")
                    c.drawRightString(width - 70, y_position, record_line4)
                    y_position -= 20
                
                # خط فاصل بين السجلات
                c.setStrokeColor(colors.lightgrey)
                c.setLineWidth(0.5)
                c.line(70, y_position - 5, width - 70, y_position - 5)
                y_position -= 25
            
            # الإحصائيات
            if y_position < 200:  # إنشاء صفحة جديدة للإحصائيات
                c.showPage()
                c.setFont("Cairo", 12)
                y_position = height - 80
            else:
                y_position -= 30
            
            c.setFont("Cairo", 14)
            stats_title = format_arabic_text("ملخص الإحصائيات")
            c.drawRightString(width - 50, y_position, stats_title)
            
            y_position -= 40
            c.setFont("Cairo", 12)
            
            # حساب المتوسطات
            avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
            avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
            
            stats = [
                f"عدد السجلات: {len(workshop_records)}",
                f"إجمالي التكلفة: {total_cost:,.0f} ريال",
                f"إجمالي أيام الإصلاح: {total_days} يوم",
                f"متوسط التكلفة لكل سجل: {avg_cost:,.0f} ريال",
                f"متوسط مدة الإصلاح: {avg_days:.1f} يوم"
            ]
            
            for stat in stats:
                formatted_stat = format_arabic_text(stat)
                c.drawRightString(width - 70, y_position, formatted_stat)
                y_position -= 25
        
        else:
            y_position -= 30
            no_records = format_arabic_text("لا توجد سجلات ورشة متاحة لهذه المركبة")
            c.drawRightString(width - 70, y_position, no_records)
        
        # التذييل
        c.setFont("Cairo", 10)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        footer = format_arabic_text(f"تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات - {current_time}")
        c.drawRightString(width - 50, 50, footer)
        
        # حفظ PDF
        c.save()
        buffer.seek(0)
        
        print("تم إنشاء PDF بخط Cairo بنجاح!")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF بخط Cairo: {str(e)}")
        # العودة للبديل
        from utils.simple_html_pdf import generate_workshop_pdf as fallback
        return fallback(vehicle, workshop_records)

def get_status_arabic(status):
    """ترجمة حالة المركبة للعربية"""
    status_map = {
        'available': 'متاح',
        'rented': 'مؤجر',
        'in_workshop': 'في الورشة',
        'accident': 'حادث'
    }
    return status_map.get(status, status)

def get_reason_arabic(reason):
    """ترجمة سبب دخول الورشة للعربية"""
    reason_map = {
        'maintenance': 'صيانة دورية',
        'breakdown': 'عطل',
        'accident': 'حادث'
    }
    return reason_map.get(reason, reason if reason else "غير محدد")

def get_repair_status_arabic(status):
    """ترجمة حالة الإصلاح للعربية"""
    status_map = {
        'in_progress': 'قيد التنفيذ',
        'completed': 'تم الإصلاح',
        'pending_approval': 'بانتظار الموافقة'
    }
    return status_map.get(status, status if status else "غير محدد")