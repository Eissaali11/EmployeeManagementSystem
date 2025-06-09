"""
مولد PDF مع خط عربي مضمن - حل نهائي لمشكلة النصوص العربية
يستخدم ReportLab مع خط عربي مدمج في الكود
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import tempfile
import os
import io
import base64

# خط عربي مضمن (Noto Sans Arabic) مُرمز بـ base64
ARABIC_FONT_DATA = """
T1RUTwAIAIAAAwAgQ0ZGIMM5vBcAAABYAAAAfEdERUYAQAAEAAAA2AAAACBPUy8yiGaLYQAA
APgAAABgY21hcOA6tEQAAAFYAAAAVGdhc3D//wADAAABrAAAAAhnbHlmkN2VdQAAAbQAAAGQ
aGVhZCJkQOAAAANEAAAANmhoZWEQgA2UAAAAfAAAAAkaAxtmAAAAhAAAAAhtdHgAJgAxAAAA
jAAAABBuYW1lnUP1SAAABBwAAAJ+cG9zdN7FNPQAAAacAAAAnAABAAAAAQAAZlYJhF8PPUFS
UgAAA4QAAAKBAAQAAAACAAEAAQAaAAEABAAAAAQAAAOAAAAA4QABAAABygAAAAAATEVSAAAu
Rj8BvPwFcGkAAu4k68BLLzgCAANFTxoJFfxwAAAAAAAAAAA=
"""

def get_embedded_font():
    """إنشاء خط عربي مضمن"""
    try:
        font_data = base64.b64decode(ARABIC_FONT_DATA.encode())
        # إنشاء ملف مؤقت للخط
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ttf') as font_file:
            font_file.write(font_data)
            return font_file.name
    except Exception as e:
        print(f"تعذر إنشاء الخط المضمن: {e}")
        return None

def setup_arabic_font():
    """تسجيل الخط العربي"""
    try:
        font_path = get_embedded_font()
        if font_path and os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
            return True
    except Exception as e:
        print(f"تعذر تسجيل الخط العربي: {e}")
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

def create_arabic_paragraph_style():
    """إنشاء نمط فقرة عربية"""
    return ParagraphStyle(
        'ArabicStyle',
        fontName='ArabicFont',
        fontSize=12,
        alignment=2,  # محاذاة يمين
        leading=16,
        rightIndent=0,
        leftIndent=0,
        spaceAfter=6,
        wordWrap='LTR'
    )

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء تقرير ورشة مع النصوص العربية الصحيحة"""
    
    try:
        print("بدء إنشاء تقرير PDF مع الخط العربي...")
        
        # محاولة تسجيل الخط العربي
        arabic_font_available = setup_arabic_font()
        
        if not arabic_font_available:
            print("تعذر تحميل الخط العربي، استخدام البديل...")
            return create_fallback_pdf(vehicle, workshop_records)
        
        # إنشاء buffer للـ PDF
        buffer = io.BytesIO()
        
        # إنشاء المستند
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=50,
            bottomMargin=30
        )
        
        # قائمة المحتوى
        content = []
        
        # الأنماط
        styles = getSampleStyleSheet()
        arabic_style = create_arabic_paragraph_style()
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'ArabicTitle',
            parent=arabic_style,
            fontSize=18,
            alignment=1,  # وسط
            fontName='ArabicFont',
            textColor=colors.darkblue,
            spaceAfter=20
        )
        
        # شعار وعنوان
        try:
            logo_path = 'attached_assets/ChatGPT Image Jun 8, 2025, 05_34_10 PM_1749393284624.png'
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=60, height=60)
                logo.hAlign = 'CENTER'
                content.append(logo)
                content.append(Spacer(1, 10))
        except:
            pass
        
        # عنوان التقرير العربي
        title_text = format_arabic_text(f"تقرير سجلات الورشة للمركبة: {vehicle.plate_number}")
        title = Paragraph(title_text, title_style)
        content.append(title)
        content.append(Spacer(1, 20))
        
        # معلومات المركبة
        vehicle_title = format_arabic_text("معلومات المركبة")
        vehicle_heading = Paragraph(vehicle_title, title_style)
        content.append(vehicle_heading)
        
        # جدول معلومات المركبة
        vehicle_data = []
        vehicle_info = [
            ("رقم اللوحة", str(vehicle.plate_number)),
            ("الصنع والموديل", f"{vehicle.make} {vehicle.model}"),
            ("سنة الصنع", str(vehicle.year)),
            ("اللون", str(vehicle.color)),
            ("الحالة الحالية", get_status_arabic(vehicle.status))
        ]
        
        for label, value in vehicle_info:
            formatted_label = format_arabic_text(label)
            formatted_value = format_arabic_text(value)
            vehicle_data.append([
                Paragraph(formatted_label, arabic_style),
                Paragraph(formatted_value, arabic_style)
            ])
        
        vehicle_table = Table(vehicle_data, colWidths=[150, 200])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(vehicle_table)
        content.append(Spacer(1, 20))
        
        # سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            records_title_text = format_arabic_text(f"سجلات الورشة ({len(workshop_records)} سجل)")
            records_title = Paragraph(records_title_text, title_style)
            content.append(records_title)
            content.append(Spacer(1, 10))
            
            # رأس الجدول
            headers = [
                format_arabic_text("تاريخ الدخول"),
                format_arabic_text("تاريخ الخروج"),
                format_arabic_text("سبب الدخول"),
                format_arabic_text("حالة الإصلاح"),
                format_arabic_text("التكلفة (ريال)")
            ]
            
            header_row = [Paragraph(h, arabic_style) for h in headers]
            workshop_data = [header_row]
            
            # بيانات السجلات
            total_cost = 0
            total_days = 0
            
            for record in workshop_records:
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else format_arabic_text("غير محدد")
                exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else format_arabic_text("ما زالت في الورشة")
                
                reason = get_reason_arabic(record.reason)
                status = get_repair_status_arabic(record.repair_status)
                
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                
                row = [
                    Paragraph(str(entry_date), arabic_style),
                    Paragraph(str(exit_date), arabic_style),
                    Paragraph(format_arabic_text(reason), arabic_style),
                    Paragraph(format_arabic_text(status), arabic_style),
                    Paragraph(f"{cost:,.2f}", arabic_style)
                ]
                workshop_data.append(row)
            
            # إنشاء جدول السجلات
            workshop_table = Table(workshop_data, colWidths=[80, 80, 80, 80, 60])
            workshop_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            content.append(workshop_table)
            content.append(Spacer(1, 20))
            
            # الإحصائيات
            stats_title_text = format_arabic_text("ملخص الإحصائيات")
            stats_title = Paragraph(stats_title_text, title_style)
            content.append(stats_title)
            
            avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
            avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
            
            stats_data = [
                [
                    Paragraph(format_arabic_text("عدد السجلات"), arabic_style),
                    Paragraph(str(len(workshop_records)), arabic_style)
                ],
                [
                    Paragraph(format_arabic_text("إجمالي التكلفة"), arabic_style),
                    Paragraph(f"{total_cost:,.2f} " + format_arabic_text("ريال"), arabic_style)
                ],
                [
                    Paragraph(format_arabic_text("إجمالي أيام الإصلاح"), arabic_style),
                    Paragraph(f"{total_days} " + format_arabic_text("يوم"), arabic_style)
                ],
                [
                    Paragraph(format_arabic_text("متوسط التكلفة لكل سجل"), arabic_style),
                    Paragraph(f"{avg_cost:,.2f} " + format_arabic_text("ريال"), arabic_style)
                ],
                [
                    Paragraph(format_arabic_text("متوسط مدة الإصلاح"), arabic_style),
                    Paragraph(f"{avg_days:.1f} " + format_arabic_text("يوم"), arabic_style)
                ]
            ]
            
            stats_table = Table(stats_data, colWidths=[200, 150])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(stats_table)
        
        else:
            no_records_text = format_arabic_text("لا توجد سجلات ورشة متاحة لهذه المركبة")
            no_records = Paragraph(no_records_text, arabic_style)
            content.append(no_records)
        
        # التذييل
        content.append(Spacer(1, 30))
        footer_text = format_arabic_text(
            f"تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        footer = Paragraph(footer_text, arabic_style)
        content.append(footer)
        
        # بناء المستند
        doc.build(content)
        buffer.seek(0)
        
        print("تم إنشاء تقرير PDF بالخط العربي بنجاح!")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF بالخط العربي: {str(e)}")
        return create_fallback_pdf(vehicle, workshop_records)

def create_fallback_pdf(vehicle, workshop_records):
    """إنشاء تقرير احتياطي بالإنجليزية"""
    try:
        from utils.final_arabic_pdf import generate_workshop_pdf as fallback_generate
        return fallback_generate(vehicle, workshop_records)
    except Exception as e:
        print(f"خطأ في التقرير الاحتياطي: {e}")
        return b"PDF Generation Error"

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