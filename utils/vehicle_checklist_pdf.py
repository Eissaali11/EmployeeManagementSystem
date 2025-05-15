"""   
مكتبة لإنشاء تقارير PDF لفحص المركبات مع دعم للنصوص العربية وعرض صورة المركبة مع علامات التلف
"""
import os
import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# تسجيل الخطوط العربية
def register_arabic_fonts():
    """تسجيل الخطوط العربية لمكتبة ReportLab"""
    # استخدام خط Tajawal العربي المتوفر بالفعل في النظام
    font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts', 'Tajawal-Regular.ttf')
    pdfmetrics.registerFont(TTFont('Amiri', font_path))
    
    # استخدام خط Tajawal Bold العربي المتوفر بالفعل في النظام
    font_path_bold = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts', 'Tajawal-Bold.ttf')
    pdfmetrics.registerFont(TTFont('Amiri-Bold', font_path_bold))

# معالجة النص العربي ليعرض بشكل صحيح
def arabic_text(text):
    """معالجة النصوص العربية للعرض الصحيح في PDF"""
    if text is None:
        return ""
    
    # تحويل النص إلى سلسلة إذا لم يكن كذلك
    if not isinstance(text, str):
        text = str(text)
    
    # إعادة تشكيل النص العربي وضبط الاتجاه
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        # في حالة فشل معالجة النص، إرجاع النص الأصلي
        return text

# مكون مخصص لعرض المركبة مع علامات التلف
class VehicleDiagramWithMarkers(Flowable):
    """عنصر مخصص لعرض مخطط المركبة مع علامات الضرر"""
    
    def __init__(self, vehicle_diagram_path, damage_markers=None, width=500, height=300):
        """
        تهيئة مكون مخطط المركبة
        
        Args:
            vehicle_diagram_path: مسار صورة مخطط المركبة (لم يعد يستخدم - نرسم بدلاً منها)
            damage_markers: قائمة بعلامات التلف، كل علامة تتكون من (x, y, notes)
            width: عرض المخطط
            height: ارتفاع المخطط
        """
        Flowable.__init__(self)
        self.vehicle_diagram_path = vehicle_diagram_path
        self.damage_markers = damage_markers or []
        self.width = width
        self.height = height
    
    def draw(self):
        """رسم المركبة مع علامات الضرر"""
        # استدعاء canvas لرسم المكونات
        canvas = self.canv
        
        # حفظ الحالة الحالية للـ canvas
        canvas.saveState()
        
        # رسم مخطط السيارة بدلاً من تحميل صورة
        # رسم هيكل السيارة
        canvas.setStrokeColor(colors.black)
        canvas.setFillColor(colors.white)
        canvas.setLineWidth(2)
        
        # مستطيل الهيكل الرئيسي
        canvas.roundRect(50, 50, self.width - 100, self.height - 100, 20, stroke=1, fill=1)
        
        # الزجاج الأمامي
        canvas.setFillColor(colors.lightblue)
        canvas.setStrokeColor(colors.black)
        points = [
            100, self.height - 100,  # أعلى يسار
            self.width - 100, self.height - 100,  # أعلى يمين
            self.width - 120, self.height - 140,  # أسفل يمين
            120, self.height - 140   # أسفل يسار
        ]
        canvas.drawPolygon(points, stroke=1, fill=1)
        
        # الزجاج الخلفي
        points = [
            120, 140,  # أعلى يسار
            self.width - 120, 140,  # أعلى يمين
            self.width - 100, 100,  # أسفل يمين
            100, 100   # أسفل يسار
        ]
        canvas.drawPolygon(points, stroke=1, fill=1)
        
        # العجلات
        canvas.setFillColor(colors.black)
        canvas.circle(120, 80, 30, stroke=1, fill=1)
        canvas.circle(self.width - 120, 80, 30, stroke=1, fill=1)
        
        # داخل العجلات (الجنوط)
        canvas.setFillColor(colors.grey)
        canvas.circle(120, 80, 15, stroke=1, fill=1)
        canvas.circle(self.width - 120, 80, 15, stroke=1, fill=1)
        
        # المصابيح الأمامية
        canvas.setFillColor(colors.yellow)
        canvas.circle(80, self.height - 120, 12, stroke=1, fill=1)
        canvas.circle(self.width - 80, self.height - 120, 12, stroke=1, fill=1)
        
        # المصابيح الخلفية
        canvas.setFillColor(colors.red)
        canvas.circle(80, 120, 12, stroke=1, fill=1)
        canvas.circle(self.width - 80, 120, 12, stroke=1, fill=1)
        
        # رسم علامات التلف
        for marker in self.damage_markers:
            # تحويل الإحداثيات من النسبة المئوية إلى إحداثيات فعلية
            x = float(marker.x_position) * self.width / 100
            y = float(marker.y_position) * self.height / 100
            note = marker.description
            
            # رسم دائرة حمراء عند نقطة التلف
            canvas.setStrokeColor(colors.red)
            canvas.setFillColor(colors.red)
            canvas.circle(x, y, 10, fill=1)
            
            # إضافة رقم داخل الدائرة
            canvas.setFillColor(colors.white)
            canvas.setFont('Amiri-Bold', 10)
            marker_index = self.damage_markers.index(marker) + 1
            # تعديل موضع النص حسب عدد الأرقام
            if marker_index < 10:
                canvas.drawCentredString(x, y - 3, str(marker_index))
            else:
                canvas.drawCentredString(x, y - 3, str(marker_index))
        
        # استعادة حالة الـ canvas
        canvas.restoreState()

# دالة إنشاء ملف PDF لتقرير فحص المركبة
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
    # طباعة قيم للتصحيح
    print(f"Vehicle: {vars(vehicle)}")
    print(f"Checklist: {vars(checklist)}")
    # تسجيل الخطوط العربية
    register_arabic_fonts()
    
    # تحضير ملف PDF
    buffer = BytesIO()
    
    # تعيين أنماط الخطوط
    styles = getSampleStyleSheet()
    
    # إضافة نمط للنصوص العربية
    styles.add(ParagraphStyle(name='Arabic',
                              fontName='Amiri',
                              fontSize=12,
                              leading=14,
                              alignment=1))  # وسط النص
    
    # إضافة نمط للعناوين العربية
    styles.add(ParagraphStyle(name='ArabicHeading',
                              fontName='Amiri-Bold',
                              fontSize=16,
                              leading=20,
                              alignment=1))  # وسط النص
    
    # إضافة نمط للعناوين الفرعية
    styles.add(ParagraphStyle(name='ArabicSubHeading',
                              fontName='Amiri-Bold',
                              fontSize=14,
                              leading=16,
                              alignment=1))  # وسط النص
    
    # إضافة نمط للجداول
    styles.add(ParagraphStyle(name='ArabicTable',
                              fontName='Amiri',
                              fontSize=10,
                              leading=12,
                              alignment=1))  # وسط النص
    
    # إنشاء مستند PDF
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=2*cm,
                            leftMargin=2*cm,
                            topMargin=2*cm,
                            bottomMargin=2*cm)
    
    # إنشاء قائمة العناصر للمستند
    elements = []
    
    # دالة لإضافة الشعار وعنوان الصفحة
    def add_logo_to_page(canvas, doc):
        # حفظ حالة الـ canvas
        canvas.saveState()
        
        # إضافة الشعار في أعلى الصفحة
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 2*cm, A4[1] - 4*cm, width=4*cm, height=2*cm)
        
        # إضافة عنوان التقرير
        canvas.setFont('Amiri-Bold', 20)
        canvas.drawCentredString(A4[0]/2, A4[1] - 3*cm, arabic_text("تقرير فحص المركبة"))
        
        # إضافة تاريخ الفحص والوقت
        canvas.setFont('Amiri', 10)
        date_str = ""
        if hasattr(checklist, 'check_date') and checklist.check_date:
            date_str = checklist.check_date.strftime("%Y-%m-%d")
        elif hasattr(checklist, 'inspection_date') and checklist.inspection_date:
            date_str = checklist.inspection_date.strftime("%Y-%m-%d")
        canvas.drawString(A4[0] - 5*cm, A4[1] - 3.5*cm, arabic_text(f"تاريخ الفحص: {date_str}"))
        
        # إضافة رقم الصفحة في أسفل الصفحة
        canvas.setFont('Amiri', 9)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(A4[0]/2, 1*cm, arabic_text(f"صفحة {page_num}"))
        
        # استعادة حالة الـ canvas
        canvas.restoreState()
    
    # إضافة معلومات المركبة
    elements.append(Paragraph(arabic_text("معلومات المركبة"), styles['ArabicHeading']))
    elements.append(Spacer(1, 10 * mm))
    
    # جدول معلومات المركبة
    vehicle_data = [
        [Paragraph(arabic_text("رقم اللوحة"), styles['ArabicTable']), 
         Paragraph(arabic_text(vehicle.plate_number or ""), styles['ArabicTable'])],
        [Paragraph(arabic_text("نوع المركبة"), styles['ArabicTable']), 
         Paragraph(arabic_text(getattr(vehicle, 'vehicle_type', '') or ""), styles['ArabicTable'])],
        [Paragraph(arabic_text("الماركة"), styles['ArabicTable']), 
         Paragraph(arabic_text(vehicle.make or ""), styles['ArabicTable'])],
        [Paragraph(arabic_text("الموديل"), styles['ArabicTable']), 
         Paragraph(arabic_text(vehicle.model or ""), styles['ArabicTable'])],
        [Paragraph(arabic_text("سنة الصنع"), styles['ArabicTable']), 
         Paragraph(arabic_text(str(vehicle.year) if vehicle.year else ""), styles['ArabicTable'])],
        [Paragraph(arabic_text("عداد المسافة (كم)"), styles['ArabicTable']), 
         Paragraph(arabic_text(str(getattr(checklist, 'odometer_reading', '')) if getattr(checklist, 'odometer_reading', None) else ""), styles['ArabicTable'])]
    ]
    
    # تنسيق جدول معلومات المركبة
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    vehicle_table = Table(vehicle_data, colWidths=[5*cm, 10*cm])
    vehicle_table.setStyle(table_style)
    elements.append(vehicle_table)
    elements.append(Spacer(1, 10 * mm))
    
    # إضافة مخطط المركبة مع علامات التلف
    elements.append(Paragraph(arabic_text("مخطط المركبة مع علامات التلف"), styles['ArabicHeading']))
    elements.append(Spacer(1, 10 * mm))
    
    # رسم مخطط المركبة مباشرة بدلاً من تحميل صورة
    # نستخدم القماش مباشرة
    diagram_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'vehicles', 'vehicle_diagram.svg')
    
    # إضافة مخطط المركبة مع علامات التلف
    diagram = VehicleDiagramWithMarkers(diagram_path, damage_markers, width=450, height=250)
    elements.append(diagram)
    elements.append(Spacer(1, 10 * mm))
    
    # إضافة شرح علامات التلف إذا كانت موجودة
    if damage_markers and len(damage_markers) > 0:
        elements.append(Paragraph(arabic_text("ملاحظات التلف"), styles['ArabicSubHeading']))
        elements.append(Spacer(1, 5 * mm))
        
        # إنشاء جدول ملاحظات التلف
        damage_data = []
        for i, marker in enumerate(damage_markers):
            damage_data.append([
                Paragraph(arabic_text(str(i+1)), styles['ArabicTable']),
                Paragraph(arabic_text(marker.description or ""), styles['ArabicTable'])
            ])
        
        # تنسيق جدول ملاحظات التلف
        damage_table = Table(damage_data, colWidths=[2*cm, 13*cm])
        damage_table.setStyle(table_style)
        elements.append(damage_table)
        elements.append(Spacer(1, 10 * mm))
    
    # إضافة عناصر الفحص
    elements.append(Paragraph(arabic_text("عناصر الفحص"), styles['ArabicHeading']))
    elements.append(Spacer(1, 10 * mm))
    
    # جدول عناصر الفحص مصنفة حسب الفئة
    for category, items in checklist_items.items():
        elements.append(Paragraph(arabic_text(category), styles['ArabicSubHeading']))
        elements.append(Spacer(1, 5 * mm))
        
        # إنشاء جدول عناصر الفحص للفئة الحالية
        items_data = []
        items_data.append([
            Paragraph(arabic_text("العنصر"), styles['ArabicTable']),
            Paragraph(arabic_text("الحالة"), styles['ArabicTable']),
            Paragraph(arabic_text("الملاحظات"), styles['ArabicTable'])
        ])
        
        for item in items:
            # تحديد حالة العنصر (جيد/سيء)
            status = ""
            status_color = colors.black
            
            if hasattr(item, 'status'):
                if item.status == 'good':
                    status = "جيد"
                    status_color = colors.green
                elif item.status == 'fair':
                    status = "متوسط"
                    status_color = colors.orange
                elif item.status == 'poor':
                    status = "سيء"
                    status_color = colors.red
                else:
                    status = "غير محدد"
                    status_color = colors.black
            
            # التعامل مع الملاحظات المفقودة
            item_name = getattr(item, 'item_name', '') or ""
            item_notes = getattr(item, 'notes', '') or ""
            
            # إضافة الصف إلى جدول البيانات
            items_data.append([
                Paragraph(arabic_text(item_name), styles['ArabicTable']),
                Paragraph(f'<font color="{status_color}">{arabic_text(status)}</font>', styles['ArabicTable']),
                Paragraph(arabic_text(item_notes), styles['ArabicTable'])
            ])
        
        # تنسيق جدول عناصر الفحص
        items_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        items_table = Table(items_data, colWidths=[5*cm, 3*cm, 7*cm])
        items_table.setStyle(items_table_style)
        elements.append(items_table)
        elements.append(Spacer(1, 10 * mm))
    
    # إضافة الصور المرفقة إذا كانت موجودة
    if checklist_images and len(checklist_images) > 0:
        elements.append(Paragraph(arabic_text("الصور المرفقة"), styles['ArabicHeading']))
        elements.append(Spacer(1, 10 * mm))
        
        # تعريف دالة مساعدة لمعالجة الصور
        def process_image(image_obj):
            # القيمة الافتراضية إذا كانت الصورة غير متوفرة
            default_cell = [Paragraph(arabic_text("(الصورة غير متوفرة)"), styles['ArabicTable'])]
            
            # التحقق من وجود سمة image_path
            image_path = getattr(image_obj, 'image_path', '')
            if not image_path:
                return default_cell
                
            img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', image_path)
            if not os.path.exists(img_path):
                return default_cell
                
            cell_content = []
            try:
                img = Image(img_path, width=7*cm, height=7*cm)
                cell_content.append(img)
            except Exception as e:
                print(f"خطأ في تحميل الصورة: {str(e)}")
                return default_cell
                
            description = getattr(image_obj, 'description', '') or ""
            cell_content.append(Paragraph(arabic_text(description), styles['ArabicTable']))
            return cell_content
        
        # عرض الصور في صفوف من صورتين
        images_data = []
        for i in range(0, len(checklist_images), 2):
            row = []
            
            # الصورة الأولى
            row.append(process_image(checklist_images[i]))
            
            # الصورة الثانية (إن وجدت)
            if i + 1 < len(checklist_images):
                row.append(process_image(checklist_images[i + 1]))
            else:
                # إضافة خلية فارغة
                row.append([])
                
            images_data.append(row)
            
            # تنسيق جدول الصور
            images_table_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            images_table = Table(images_data, colWidths=[8*cm, 8*cm])
            images_table.setStyle(images_table_style)
            elements.append(images_table)
            elements.append(Spacer(1, 10 * mm))
    
    # إضافة معلومات المفتش
    elements.append(Paragraph(arabic_text("معلومات المفتش"), styles['ArabicHeading']))
    elements.append(Spacer(1, 10 * mm))
    
    # جدول توقيع المفتش
    inspector_data = [
        [Paragraph(arabic_text("اسم المفتش"), styles['ArabicTable']), 
         Paragraph(arabic_text(checklist.inspector_name or ""), styles['ArabicTable'])],
        [Paragraph(arabic_text("التوقيع"), styles['ArabicTable']), 
         Paragraph(arabic_text("________________________"), styles['ArabicTable'])]
    ]
    
    # تنسيق جدول توقيع المفتش
    inspector_table = Table(inspector_data, colWidths=[5*cm, 10*cm])
    inspector_table.setStyle(table_style)
    elements.append(inspector_table)
    
    # إنشاء المستند النهائي
    doc.build(elements, onFirstPage=add_logo_to_page, onLaterPages=add_logo_to_page)
    
    # إعادة مؤشر القراءة إلى بداية الملف
    buffer.seek(0)
    return buffer