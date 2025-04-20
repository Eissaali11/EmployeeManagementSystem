"""
وحدة إنشاء تقارير PDF باستخدام ReportLab
"""
from datetime import datetime

def generate_salary_report_pdf(salaries, month, year, department_name, totals):
    """
    إنشاء تقرير PDF للرواتب باستخدام ReportLab مع دعم للغة العربية
    
    Args:
        salaries: قائمة بكائنات الرواتب
        month: رقم الشهر
        year: السنة
        department_name: اسم القسم
        totals: قاموس يحتوي على مجاميع الرواتب
        
    Returns:
        BytesIO يحتوي على ملف PDF
    """
    try:
        from io import BytesIO
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import arabic_reshaper
        from bidi.algorithm import get_display
        from utils.date_converter import get_month_name_ar
        
        # التأكد من تحويل الشهر والسنة إلى قيم عددية
        month = int(month) if not isinstance(month, int) else month
        year = int(year) if not isinstance(year, int) else year
        
        # إنشاء ملف PDF
        buffer = BytesIO()
        
        # تسجيل الخط العربي (Tajawal بدلاً من Cairo لأن Cairo غير متوفر)
        try:
            # محاولة تسجيل خط Tajawal الذي يدعم اللغة العربية
            pdfmetrics.registerFont(TTFont('Arabic', 'static/fonts/Tajawal-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('ArabicBold', 'static/fonts/Tajawal-Bold.ttf'))
            arabic_font = 'Arabic'
            arabic_font_bold = 'ArabicBold'
            print("تم تسجيل خط Tajawal بنجاح")
        except Exception as e:
            print(f"خطأ في تسجيل الخط العربي: {str(e)}")
            arabic_font = 'Helvetica'
            arabic_font_bold = 'Helvetica-Bold'
            
        # تعيين أبعاد الصفحة واتجاهها
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # إعداد الأنماط
        styles = getSampleStyleSheet()
        # إنشاء نمط للنص العربي
        arabic_style = ParagraphStyle(
            name='ArabicStyle',
            parent=styles['Normal'],
            fontName=arabic_font,
            fontSize=12,
            alignment=1, # وسط
            textColor=colors.black
        )
        
        # إنشاء نمط للعناوين
        title_style = ParagraphStyle(
            name='TitleArabic',
            parent=styles['Title'],
            fontName=arabic_font,
            fontSize=16,
            alignment=1, # وسط
            textColor=colors.black
        )
        
        # إعداد المحتوى
        elements = []
        
        # إضافة اسم الشركة
        company_name = "نُظم - نظام إدارة متكامل"
        company_name = get_display(arabic_reshaper.reshape(company_name))
        company_style = ParagraphStyle(
            name='CompanyTitle',
            parent=styles['Title'],
            fontName=arabic_font_bold,
            fontSize=18,
            alignment=1, # وسط
            textColor=colors.black
        )
        elements.append(Paragraph(company_name, company_style))
        elements.append(Spacer(1, 10))
        
        # إضافة العنوان
        title = f"كشف رواتب شهر {get_month_name_ar(month)} {year} - {department_name}"
        # تهيئة النص العربي للعرض في PDF
        title = get_display(arabic_reshaper.reshape(title))
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))
        
        # إضافة تاريخ التقرير
        date_text = f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}"
        date_text = get_display(arabic_reshaper.reshape(date_text))
        elements.append(Paragraph(date_text, arabic_style))
        elements.append(Spacer(1, 20))
        
        # إعداد جدول البيانات
        headers = ["الاسم", "الرقم الوظيفي", "الراتب الأساسي", "البدلات", "الخصومات", "المكافآت", "صافي الراتب"]
        data = []
        
        # إضافة الرؤوس
        headers_display = [get_display(arabic_reshaper.reshape(h)) for h in headers]
        data.append(headers_display)
        
        # إضافة بيانات الرواتب
        for salary_item in salaries:
            if salary_item['has_salary']:
                employee = salary_item['employee']
                row = [
                    get_display(arabic_reshaper.reshape(employee.name)),
                    employee.employee_id,
                    f"{salary_item['basic_salary']:.2f}",
                    f"{salary_item['allowances']:.2f}",
                    f"{salary_item['deductions']:.2f}",
                    f"{salary_item['bonus']:.2f}",
                    f"{salary_item['net_salary']:.2f}"
                ]
                data.append(row)
        
        # إنشاء الجدول
        if len(data) > 1:  # لدينا بيانات بخلاف الرؤوس
            # حساب العرض المناسب للجدول بناءً على حجم الصفحة
            table_width = landscape(A4)[0] - 4*cm  # العرض الإجمالي ناقص الهوامش
            col_widths = [table_width/len(headers)] * len(headers)  # توزيع متساوي
            table = Table(data, colWidths=col_widths)
            
            # إعداد أنماط الجدول
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),  # لون خلفية العناوين
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # لون نص العناوين
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # محاذاة النص
                ('FONTNAME', (0, 0), (-1, 0), arabic_font),  # خط العناوين
                ('FONTSIZE', (0, 0), (-1, 0), 12),  # حجم خط العناوين
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # تباعد أسفل العناوين
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # لون خلفية البيانات
                ('FONTNAME', (0, 1), (-1, -1), arabic_font),  # خط البيانات
                ('FONTSIZE', (0, 1), (-1, -1), 10),  # حجم خط البيانات
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # حدود الجدول
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # محاذاة النص عموديا
            ])
            
            # تطبيق التناوب في ألوان الصفوف لتحسين القراءة
            for i in range(1, len(data)):
                if i % 2 == 0:
                    table_style.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)
            
            table.setStyle(table_style)
            elements.append(table)
            
            # إضافة صف الإجماليات
            elements.append(Spacer(1, 20))
            totals_text = f"الإجماليات: الراتب الأساسي: {totals['basic']:.2f} - البدلات: {totals['allowances']:.2f} - الخصومات: {totals['deductions']:.2f} - المكافآت: {totals['bonus']:.2f} - صافي الرواتب: {totals['net']:.2f}"
            totals_text = get_display(arabic_reshaper.reshape(totals_text))
            elements.append(Paragraph(totals_text, arabic_style))
        else:
            no_data_text = "لا توجد بيانات رواتب لهذه الفترة"
            no_data_text = get_display(arabic_reshaper.reshape(no_data_text))
            elements.append(Paragraph(no_data_text, arabic_style))
        
        # إضافة معلومات التقرير في أسفل الصفحة
        elements.append(Spacer(1, 20))
        footer_text = f"تاريخ إنشاء التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        footer_text = get_display(arabic_reshaper.reshape(footer_text))
        elements.append(Paragraph(footer_text, arabic_style))
        
        # بناء المستند
        doc.build(elements)
        
        # إعادة المؤشر إلى بداية البايت والإرجاع
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        print(f"خطأ في إنشاء تقرير PDF: {str(e)}")
        raise Exception(f"خطأ في إنشاء تقرير PDF: {str(e)}")
