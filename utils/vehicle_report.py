"""
وحدة إنشاء تقارير المركبات الشاملة
توفر هذه الوحدة وظائف لإنشاء تقارير PDF شاملة للمركبات
"""

import os
import io
from datetime import datetime
from flask import current_app
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

def arabic_text(pdf, x, y, text, align='R'):
    """
    طباعة نص عربي في الموضع المحدد
    
    Args:
        pdf: كائن FPDF
        x: الموضع السيني
        y: الموضع الصادي
        text: النص المراد طباعته
        align: محاذاة النص (R = يمين، L = يسار، C = وسط)
    """
    # معالجة النص العربي
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    
    # تعيين موضع الطباعة
    pdf.set_xy(x, y)
    
    # طباعة النص مع المحاذاة المناسبة
    if align == 'R':  # محاذاة لليمين (للنص العربي تكون يسار)
        pdf.cell(0, 0, bidi_text, ln=0, align='L')
    elif align == 'C':  # توسيط
        pdf.cell(0, 0, bidi_text, ln=0, align='C')
    else:  # محاذاة لليسار (للنص العربي تكون يمين)
        pdf.cell(0, 0, bidi_text, ln=0, align='R')

def generate_complete_vehicle_report(vehicle, rental=None, workshop_records=None, documents=None, maintenance_records=None):
    """
    إنشاء تقرير شامل للسيارة بصيغة PDF
    
    Args:
        vehicle: كائن المركبة
        rental: معلومات الإيجار (اختياري)
        workshop_records: سجلات الورشة (اختياري)
        documents: مستندات المركبة (اختياري)
        maintenance_records: سجلات الصيانة الدورية (اختياري)
        
    Returns:
        bytes: محتوى ملف PDF
    """
    try:
        # إنشاء PDF جديد
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # إضافة الخط العربي
        font_path = os.path.join(current_app.root_path, 'static', 'fonts', 'Amiri-Regular.ttf')
        if os.path.exists(font_path):
            pdf.add_font('Arabic', '', font_path, uni=True)
            pdf.set_font('Arabic', '', 14)
        else:
            pdf.set_font('Arial', '', 14)
        
        # إعداد الألوان الرئيسية
        primary_color = (29, 161, 142)  # لون أخضر أساسي
        secondary_color = (66, 66, 66)  # لون رمادي ثانوي
        accent_color = (13, 71, 161)  # لون أزرق فاتح
        
        # إضافة ترويسة التقرير
        pdf.set_font('Arabic', 'B', 18)
        pdf.set_text_color(*primary_color)
        arabic_text(pdf, 105, 15, 'تقرير شامل للسيارة', 'C')
        
        # إضافة رقم اللوحة
        pdf.set_font('Arabic', 'B', 16)
        arabic_text(pdf, 105, 25, f'رقم اللوحة: {vehicle.plate_number}', 'C')
        
        # إضافة التاريخ
        pdf.set_font('Arabic', '', 10)
        pdf.set_text_color(*secondary_color)
        arabic_text(pdf, 105, 35, f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d")}', 'C')
        
        # إضافة خط تحت العنوان
        pdf.set_draw_color(*primary_color)
        pdf.set_line_width(0.5)
        pdf.line(10, 40, 200, 40)
        
        # قسم معلومات السيارة الأساسية
        y_pos = 50
        pdf.set_font('Arabic', 'B', 14)
        pdf.set_text_color(*primary_color)
        arabic_text(pdf, 190, y_pos, 'معلومات السيارة الأساسية', 'R')
        
        y_pos += 10
        
        # جدول المعلومات الأساسية
        pdf.set_font('Arabic', '', 11)
        pdf.set_text_color(*secondary_color)
        
        # رسم مستطيل خلفية
        pdf.set_fill_color(245, 245, 245)
        pdf.rect(10, y_pos, 190, 56, 'F')
        
        # بيانات السيارة
        arabic_text(pdf, 190, y_pos + 8, 'رقم اللوحة:', 'R')
        arabic_text(pdf, 100, y_pos + 8, vehicle.plate_number, 'R')
        
        arabic_text(pdf, 190, y_pos + 16, 'النوع:', 'R')
        arabic_text(pdf, 100, y_pos + 16, f'{vehicle.make} {vehicle.model}', 'R')
        
        arabic_text(pdf, 190, y_pos + 24, 'سنة الصنع:', 'R')
        arabic_text(pdf, 100, y_pos + 24, str(vehicle.year), 'R')
        
        arabic_text(pdf, 190, y_pos + 32, 'اللون:', 'R')
        arabic_text(pdf, 100, y_pos + 32, vehicle.color, 'R')
        
        arabic_text(pdf, 190, y_pos + 40, 'الحالة:', 'R')
        status_map = {
            'available': 'متاحة',
            'rented': 'مؤجرة',
            'in_project': 'في المشروع',
            'in_workshop': 'في الورشة',
            'accident': 'حادث'
        }
        arabic_text(pdf, 100, y_pos + 40, status_map.get(vehicle.status, vehicle.status), 'R')
        
        arabic_text(pdf, 190, y_pos + 48, 'تاريخ الإضافة:', 'R')
        arabic_text(pdf, 100, y_pos + 48, vehicle.created_at.strftime('%Y-%m-%d'), 'R')
        
        # معلومات الإيجار
        y_pos += 66
        pdf.set_font('Arabic', 'B', 14)
        pdf.set_text_color(*primary_color)
        arabic_text(pdf, 190, y_pos, 'معلومات الإيجار', 'R')
        
        y_pos += 10
        pdf.set_font('Arabic', '', 11)
        pdf.set_text_color(*secondary_color)
        
        if rental:
            # رسم مستطيل خلفية
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, y_pos, 190, 48, 'F')
            
            arabic_text(pdf, 190, y_pos + 8, 'المؤجر:', 'R')
            arabic_text(pdf, 100, y_pos + 8, rental.lessor_name or 'غير محدد', 'R')
            
            arabic_text(pdf, 190, y_pos + 16, 'تاريخ البداية:', 'R')
            arabic_text(pdf, 100, y_pos + 16, rental.start_date.strftime('%Y-%m-%d'), 'R')
            
            arabic_text(pdf, 190, y_pos + 24, 'تاريخ النهاية:', 'R')
            if rental.end_date:
                arabic_text(pdf, 100, y_pos + 24, rental.end_date.strftime('%Y-%m-%d'), 'R')
            else:
                arabic_text(pdf, 100, y_pos + 24, 'مستمر', 'R')
            
            arabic_text(pdf, 190, y_pos + 32, 'التكلفة الشهرية:', 'R')
            arabic_text(pdf, 100, y_pos + 32, f"{rental.monthly_cost:,.2f} ريال", 'R')
            
            arabic_text(pdf, 190, y_pos + 40, 'رقم العقد:', 'R')
            arabic_text(pdf, 100, y_pos + 40, rental.contract_number or 'غير محدد', 'R')
            
            y_pos += 50
        else:
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, y_pos, 190, 15, 'F')
            arabic_text(pdf, 100, y_pos + 8, 'لا يوجد إيجار نشط حاليًا', 'C')
            y_pos += 20
        
        # ملخص سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            pdf.set_font('Arabic', 'B', 14)
            pdf.set_text_color(*primary_color)
            arabic_text(pdf, 190, y_pos, 'ملخص سجلات الورشة', 'R')
            
            y_pos += 10
            
            # حساب التكلفة الإجمالية
            total_cost = sum(record.cost for record in workshop_records)
            
            # رسم مستطيل خلفية
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, y_pos, 190, 15, 'F')
            
            pdf.set_font('Arabic', '', 11)
            pdf.set_text_color(*secondary_color)
            arabic_text(pdf, 190, y_pos + 8, f'عدد مرات دخول الورشة:', 'R')
            arabic_text(pdf, 110, y_pos + 8, str(len(workshop_records)), 'R')
            
            arabic_text(pdf, 100, y_pos + 8, f'إجمالي التكاليف:', 'R')
            arabic_text(pdf, 20, y_pos + 8, f"{total_cost:,.2f} ريال", 'R')
            
            # جدول آخر 3 سجلات للورشة
            if len(workshop_records) > 0:
                y_pos += 20
                pdf.set_font('Arabic', 'B', 11)
                pdf.set_text_color(*accent_color)
                arabic_text(pdf, 180, y_pos, 'آخر سجلات الورشة:', 'R')
                
                y_pos += 8
                
                # عناوين الجدول
                pdf.set_font('Arabic', 'B', 9)
                pdf.set_text_color(*secondary_color)
                
                # خلفية عناوين الجدول
                pdf.set_fill_color(230, 230, 230)
                pdf.rect(10, y_pos, 190, 8, 'F')
                
                arabic_text(pdf, 180, y_pos + 4, 'التاريخ', 'R')
                arabic_text(pdf, 140, y_pos + 4, 'اسم الورشة', 'R')
                arabic_text(pdf, 90, y_pos + 4, 'سبب الدخول', 'R')
                arabic_text(pdf, 40, y_pos + 4, 'التكلفة', 'R')
                
                # بيانات الجدول
                y_pos += 8
                pdf.set_font('Arabic', '', 9)
                
                reason_map = {
                    'maintenance': 'صيانة دورية',
                    'breakdown': 'عطل',
                    'accident': 'حادث'
                }
                
                # عرض آخر 3 سجلات فقط
                for i, record in enumerate(workshop_records[:3]):
                    # تناوب لون الخلفية
                    if i % 2 == 0:
                        pdf.set_fill_color(245, 245, 245)
                    else:
                        pdf.set_fill_color(255, 255, 255)
                    pdf.rect(10, y_pos, 190, 8, 'F')
                    
                    arabic_text(pdf, 180, y_pos + 4, record.entry_date.strftime('%Y-%m-%d'), 'R')
                    arabic_text(pdf, 140, y_pos + 4, record.workshop_name or 'غير محدد', 'R')
                    arabic_text(pdf, 90, y_pos + 4, reason_map.get(record.reason, record.reason), 'R')
                    arabic_text(pdf, 40, y_pos + 4, f"{record.cost:,.2f} ريال", 'R')
                    
                    y_pos += 8
        
        # الملاحظات
        if vehicle.notes:
            # نقل لصفحة جديدة إذا لزم الأمر
            if y_pos > 240:
                pdf.add_page()
                y_pos = 20
            
            pdf.set_font('Arabic', 'B', 12)
            pdf.set_text_color(*primary_color)
            arabic_text(pdf, 190, y_pos + 8, 'ملاحظات:', 'R')
            
            # رسم مستطيل خلفية
            y_pos += 12
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(10, y_pos, 190, 20, 'F')
            
            pdf.set_font('Arabic', '', 10)
            pdf.set_text_color(*secondary_color)
            
            # طباعة الملاحظات مع مراعاة طول النص
            notes = vehicle.notes
            if len(notes) > 150:
                notes = notes[:150] + '...'
            
            arabic_text(pdf, 180, y_pos + 8, notes, 'R')
        
        # تذييل التقرير
        pdf.set_y(-15)
        pdf.set_font('Arabic', '', 8)
        pdf.set_text_color(*secondary_color)
        arabic_text(pdf, 105, pdf.get_y(), f'تم إنشاء هذا التقرير بواسطة نظام إدارة المركبات - {datetime.now().strftime("%Y-%m-%d %H:%M")}', 'C')
        
        # إرجاع بيانات PDF كـ bytes
        return pdf.output(dest='S').encode('latin1')
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير الشامل للسيارة: {str(e)}")
        raise e