"""   
مكتبة لإنشاء تقارير PDF لفحص المركبات مع دعم للنصوص العربية وعرض صورة المركبة مع علامات التلف
"""

import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.units import mm, cm
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from flask import current_app

# محاولة استيراد مكتبات النصوص العربية
try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("تحذير: مكتبات دعم النصوص العربية غير متوفرة")

# تسجيل خط Amiri العربي
def register_arabic_fonts():
    """تسجيل الخطوط العربية لمكتبة ReportLab"""
    try:
        # البحث عن مسار الخطوط
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_path = os.path.join(base_path, 'static', 'fonts')
        
        amiri_regular = os.path.join(font_path, 'Amiri-Regular.ttf')
        amiri_bold = os.path.join(font_path, 'Amiri-Bold.ttf')
        
        if os.path.exists(amiri_regular) and os.path.exists(amiri_bold):
            pdfmetrics.registerFont(TTFont('Amiri', amiri_regular))
            pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_bold))
            return True
    except Exception as e:
        print(f"خطأ في تسجيل الخطوط العربية: {e}")
    
    return False

# دالة مساعدة لمعالجة النصوص العربية
def arabic_text(text):
    """معالجة النصوص العربية للعرض الصحيح في PDF"""
    if not text:
        return ''
    
    # تحويل النص إلى سلسلة نصية إذا لم يكن كذلك بالفعل
    text = str(text)
    
    # إذا كان هناك دعم للنصوص العربية
    if ARABIC_SUPPORT:
        try:
            reshaped_text = reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"خطأ في معالجة النص العربي: {e}")
    
    # إرجاع النص كما هو إذا لم يكن هناك دعم للعربية أو حدث خطأ
    return text

class VehicleDiagramWithMarkers(Flowable):
    """عنصر مخصص لعرض مخطط المركبة مع علامات الضرر"""
    
    def __init__(self, vehicle_diagram_path, damage_markers=None, width=500, height=300):
        Flowable.__init__(self)
        self.vehicle_diagram_path = vehicle_diagram_path
        self.damage_markers = damage_markers or []
        self.width = width
        self.height = height
        
    def draw(self):
        """رسم المركبة مع علامات الضرر"""
        try:
            # تحميل صورة المركبة
            if os.path.exists(self.vehicle_diagram_path):
                # احتساب نسبة الحجم
                img = PILImage.open(self.vehicle_diagram_path)
                aspect_ratio = img.width / img.height
                
                # تعديل الحجم الفعلي مع المحافظة على النسبة
                if aspect_ratio > 1:  # عرض أكبر من الارتفاع
                    actual_width = min(self.width, img.width)
                    actual_height = actual_width / aspect_ratio
                else:  # ارتفاع أكبر من العرض
                    actual_height = min(self.height, img.height)
                    actual_width = actual_height * aspect_ratio
                
                # رسم صورة المركبة
                self.canv.drawImage(
                    self.vehicle_diagram_path,
                    0, 0,
                    width=actual_width,
                    height=actual_height,
                    mask='auto'
                )
                
                # رسم علامات الضرر
                for marker in self.damage_markers:
                    # تحويل النسب المئوية إلى إحداثيات فعلية
                    x = marker.position_x * actual_width / 100
                    y = marker.position_y * actual_height / 100
                    
                    # اختيار لون العلامة بناءً على نوعها
                    if marker.marker_type == 'damage':
                        marker_color = colors.red
                    else:  # scratch
                        marker_color = colors.orange
                    
                    # رسم دائرة في موقع العلامة
                    self.canv.setFillColor(marker_color)
                    self.canv.setStrokeColor(colors.black)
                    self.canv.circle(x, actual_height - y, 5, fill=1)
                    
                    # إضافة رمز داخل الدائرة
                    self.canv.setFillColor(colors.white)
                    self.canv.setFont('Helvetica-Bold', 8)
                    if marker.marker_type == 'damage':
                        self.canv.drawCentredString(x, actual_height - y - 2, 'X')
                    else:
                        self.canv.drawCentredString(x, actual_height - y - 2, '-')
                    
                return (actual_width, actual_height)
            else:
                print(f"خطأ: لم يتم العثور على صورة المركبة: {self.vehicle_diagram_path}")
                return (0, 0)
                
        except Exception as e:
            print(f"خطأ في رسم مخطط المركبة: {e}")
            return (0, 0)

def create_vehicle_checklist_pdf(checklist, vehicle, checklist_items, damage_markers=None, checklist_images=None):
    """
    إنشاء ملف PDF لفحص المركبة
    
    Args:
        checklist: كائن فحص المركبة
        vehicle: كائن المركبة
        checklist_items: عناصر الفحص مصنفة حسب الفئة
        damage_markers: علامات التلف (اختياري)
        checklist_images: صور الفحص (اختياري)
        
    Returns:
        BytesIO: كائن BytesIO يحتوي على ملف PDF
    """
    # تسجيل الخطوط العربية
    fonts_registered = register_arabic_fonts()
    
    # إنشاء مستند PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=20*mm,
        bottomMargin=15*mm
    )
    
    # الأنماط المستخدمة في المستند
    styles = getSampleStyleSheet()
    
    # إضافة أنماط عربية مخصصة
    styles.add(
        ParagraphStyle(
            name='ArabicTitle',
            fontName='Amiri-Bold' if fonts_registered else 'Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArabicSubtitle',
            fontName='Amiri-Bold' if fonts_registered else 'Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_RIGHT,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='Arabic',
            fontName='Amiri' if fonts_registered else 'Helvetica',
            fontSize=12,
            leading=16,
            alignment=TA_RIGHT,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArabicSmall',
            fontName='Amiri' if fonts_registered else 'Helvetica',
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
        )
    )
    
    # قائمة لتخزين محتويات المستند
    content = []
    
    # إضافة دالة رأس الصفحة (مع الشعار مركزًا في الأعلى)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_path, 'static', 'images', 'logo', 'logo_new.png')
    
    # فحص وجود الشعار
    has_logo = os.path.exists(logo_path)
    add_logo_fn = None
    
    if has_logo:
        try:
            # إنشاء الدالة التي ستضيف الشعار إلى رأس الصفحة (مركزًا)
            def add_logo_to_page(canvas, doc):
                try:
                    # استخدام حجم مناسب للشعار في رأس الصفحة
                    logo_size = 40*mm  
                    # وضع الشعار في وسط رأس الصفحة
                    logo_x = doc.pagesize[0]/2  # الوسط الأفقي للصفحة
                    logo_y = doc.height + 30*mm  # أعلى الصفحة
                    
                    # رسم الشعار مع مراعاة مركز الشعار
                    canvas.drawImage(logo_path, logo_x - logo_size/2, logo_y - logo_size/2, width=logo_size, height=logo_size, mask='auto')
                except Exception as e:
                    print(f"خطأ في رسم الشعار في رأس الصفحة: {str(e)}")
            
            # تعيين الدالة لاستخدامها لاحقاً
            add_logo_fn = add_logo_to_page
                    
        except Exception as e:
            print(f"خطأ في تجهيز الشعار: {str(e)}")
            add_logo_fn = None
    
    # إضافة عنوان المستند
    inspection_type_map = {
        'daily': 'فحص يومي',
        'weekly': 'فحص أسبوعي',
        'monthly': 'فحص شهري',
        'quarterly': 'فحص ربع سنوي'
    }
    inspection_type = inspection_type_map.get(checklist.inspection_type, checklist.inspection_type)
    title = Paragraph(arabic_text(f"تقرير {inspection_type} للمركبة: {vehicle.plate_number}"), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 10))
    
    # معلومات المركبة والفحص
    vehicle_info_data = [
        [arabic_text("رقم اللوحة"), arabic_text(vehicle.plate_number), arabic_text("نوع السيارة"), arabic_text(f"{vehicle.make} {vehicle.model}")],
        [arabic_text("تاريخ الفحص"), arabic_text(checklist.inspection_date.strftime("%Y-%m-%d")), arabic_text("الفاحص"), arabic_text(checklist.inspector_name)],
        [arabic_text("نوع الفحص"), arabic_text(inspection_type), arabic_text("نسبة الاكتمال"), arabic_text(f"{checklist.completion_percentage}%")]
    ]
    
    # إنشاء جدول معلومات المركبة والفحص
    vehicle_info_table = Table(vehicle_info_data, colWidths=[doc.width/4] * 4)
    vehicle_info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Amiri' if fonts_registered else 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(vehicle_info_table)
    content.append(Spacer(1, 15))
    
    # ملخص الفحص
    content.append(Paragraph(arabic_text("ملخص الفحص"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 5))
    
    # إنشاء جدول ملخص الفحص
    summary_data = [
        [arabic_text("جيد"), arabic_text(str(checklist.summary.get('good', 0)))],
        [arabic_text("متوسط"), arabic_text(str(checklist.summary.get('fair', 0)))],
        [arabic_text("سيء"), arabic_text(str(checklist.summary.get('poor', 0)))],
    ]
    
    summary_table = Table(summary_data, colWidths=[doc.width/3, doc.width/3])
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Amiri' if fonts_registered else 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(summary_table)
    content.append(Spacer(1, 15))
    
    # مخطط المركبة مع علامات التلف
    if damage_markers and len(damage_markers) > 0:
        content.append(Paragraph(arabic_text("مخطط المركبة وعلامات التلف"), styles['ArabicSubtitle']))
        content.append(Spacer(1, 5))
        
        # مسار صورة المركبة
        vehicle_diagram_path = os.path.join(base_path, 'static', 'images', 'vehicles', 'vehicle_diagram.png')
        
        # إنشاء عنصر مخطط المركبة وإضافته إلى المحتوى
        if os.path.exists(vehicle_diagram_path):
            # إضافة الصورة مع العلامات
            diagram = VehicleDiagramWithMarkers(vehicle_diagram_path, damage_markers, width=doc.width, height=doc.width * 0.6)
            content.append(diagram)
            content.append(Spacer(1, 10))
            
            # إضافة جدول ملاحظات التلفيات
            content.append(Paragraph(arabic_text("ملاحظات التلفيات"), styles['Arabic']))
            content.append(Spacer(1, 5))
            
            marker_data = [
                [arabic_text("نوع العلامة"), arabic_text("الملاحظات")]
            ]
            
            for marker in damage_markers:
                if marker.notes:
                    marker_type = arabic_text("تلف") if marker.marker_type == 'damage' else arabic_text("خدش")
                    marker_data.append([marker_type, arabic_text(marker.notes)])
            
            if len(marker_data) > 1:
                marker_table = Table(marker_data, colWidths=[doc.width/4, 3*doc.width/4])
                marker_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Amiri' if fonts_registered else 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                content.append(marker_table)
                content.append(Spacer(1, 15))
            else:
                content.append(Paragraph(arabic_text("لا توجد ملاحظات للتلفيات"), styles['Arabic']))
                content.append(Spacer(1, 15))
        else:
            content.append(Paragraph(arabic_text("لم يتم العثور على مخطط المركبة"), styles['Arabic']))
            content.append(Spacer(1, 15))
    
    # صور الفحص المرفقة
    if checklist_images and len(checklist_images) > 0:
        content.append(Paragraph(arabic_text("صور الفحص المرفقة"), styles['ArabicSubtitle']))
        content.append(Spacer(1, 5))
        
        # تقسيم الصور إلى صفوف من 2 صورة لكل صف
        image_rows = []
        current_row = []
        
        for image in checklist_images:
            image_path = os.path.join(base_path, 'static', image.image_path)
            if os.path.exists(image_path):
                try:
                    # إضافة الصورة إلى الصف الحالي
                    current_row.append(image_path)
                    
                    # إذا اكتمل الصف، أضفه إلى قائمة الصفوف وابدأ صفًا جديدًا
                    if len(current_row) == 2:
                        image_rows.append(current_row)
                        current_row = []
                except Exception as e:
                    print(f"خطأ في معالجة الصورة: {str(e)}")
        
        # إذا كان هناك صور متبقية في الصف الأخير
        if current_row:
            # إضافة خانة فارغة إذا كان الصف غير مكتمل
            while len(current_row) < 2:
                current_row.append(None)
            image_rows.append(current_row)
        
        # إضافة صفوف الصور إلى المحتوى
        for row in image_rows:
            # إنشاء بيانات صف الصور
            img_data = []
            img_row = []
            
            for img_path in row:
                if img_path and os.path.exists(img_path):
                    # حساب الحجم المناسب للصورة
                    img_width = (doc.width - 15) / 2  # عرض الصورة
                    
                    # إنشاء كائن صورة
                    img = Image(img_path, width=img_width, height=img_width * 0.75)
                    img_row.append(img)
                else:
                    # إضافة خلية فارغة
                    img_row.append('')
            
            img_data.append(img_row)
            
            # إنشاء جدول الصور
            img_table = Table(img_data, colWidths=[doc.width/2] * 2)
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            content.append(img_table)
            content.append(Spacer(1, 10))
    
    # عناصر الفحص
    content.append(Paragraph(arabic_text("عناصر الفحص"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 5))
    
    # إضافة عناصر الفحص حسب الفئة
    for category, items in checklist_items.items():
        # تحويل اسم الفئة باللغة العربية
        category_name_map = {
            'engine': 'المحرك والسوائل',
            'tires': 'الإطارات والفرامل',
            'lights': 'الإضاءة والكهرباء',
            'components': 'مكونات داخلية وخارجية',
            'safety': 'أنظمة السلامة والطوارئ'
        }
        
        category_name = category_name_map.get(category, category)
        
        content.append(Paragraph(arabic_text(category_name), styles['Arabic']))
        
        # إنشاء جدول لعناصر الفئة
        items_data = [
            [arabic_text("العنصر"), arabic_text("الحالة"), arabic_text("ملاحظات")]
        ]
        
        for item in items:
            # تحويل حالة العنصر إلى العربية
            status_map = {
                'good': 'جيد',
                'fair': 'متوسط',
                'poor': 'سيء',
                'not_checked': 'لم يتم الفحص'
            }
            
            status = status_map.get(item.status, item.status)
            items_data.append([
                arabic_text(item.item_name),
                arabic_text(status),
                arabic_text(item.notes if item.notes else '')
            ])
        
        # إنشاء جدول عناصر الفئة
        items_table = Table(items_data, colWidths=[doc.width/3, doc.width/6, doc.width/2])
        items_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri' if fonts_registered else 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        content.append(items_table)
        content.append(Spacer(1, 15))
    
    # إضافة الملاحظات العامة
    if checklist.notes:
        content.append(Paragraph(arabic_text("ملاحظات عامة"), styles['ArabicSubtitle']))
        content.append(Spacer(1, 5))
        content.append(Paragraph(arabic_text(checklist.notes), styles['Arabic']))
        content.append(Spacer(1, 15))
    
    # إضافة تذييل للصفحة
    footer_text = f"تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة متكامل في {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    content.append(Paragraph(arabic_text(footer_text), styles['ArabicSmall']))
    
    # بناء المستند مع إضافة الشعار إذا كان موجوداً
    if add_logo_fn:
        # بناء المستند مع الشعار
        doc.build(content, onFirstPage=add_logo_fn, onLaterPages=add_logo_fn)
    else:
        # بناء المستند بدون الشعار
        doc.build(content)
    
    # إعادة ضبط مؤشر الكائن BytesIO للقراءة
    buffer.seek(0)
    
    # إرجاع مهاندل الملف ليتم استخدامه مع send_file
    return buffer