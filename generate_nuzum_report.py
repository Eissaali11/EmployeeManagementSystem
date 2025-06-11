#!/usr/bin/env python3
"""
إنشاء تقرير شامل عن نظام نُظم بصيغة PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

def setup_arabic_font():
    """إعداد الخط العربي"""
    font_paths = [
        'Cairo.ttf',
        'fonts/Cairo.ttf', 
        'static/fonts/Cairo.ttf',
        '/System/Library/Fonts/Arial Unicode.ttf'  # macOS fallback
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
                return True
            except Exception as e:
                print(f"فشل في تحميل الخط {font_path}: {e}")
                continue
    
    # محاولة استخدام خطوط النظام الأساسية
    try:
        # تسجيل خط Helvetica للنصوص الإنجليزية
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        registerFontFamily('Arabic', normal='Helvetica', bold='Helvetica-Bold')
        print("تم استخدام خط Helvetica كبديل")
        return False
    except:
        print("فشل في تسجيل الخط البديل")
        return False

def create_arabic_style(font_size=12, alignment=TA_RIGHT):
    """إنشاء نمط للنص العربي"""
    if setup_arabic_font():
        return ParagraphStyle(
            'Arabic',
            fontName='Arabic',
            fontSize=font_size,
            alignment=alignment,
            rightIndent=20,
            leftIndent=20,
            spaceAfter=12,
            leading=font_size * 1.2
        )
    else:
        return ParagraphStyle(
            'Arabic',
            fontName='Helvetica',
            fontSize=font_size,
            alignment=alignment,
            rightIndent=20,
            leftIndent=20,
            spaceAfter=12,
            leading=font_size * 1.2
        )

def generate_nuzum_report():
    """إنشاء التقرير الشامل لنظام نُظم"""
    
    # إعداد المستند
    filename = f"nuzum_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # إعداد الأنماط
    styles = getSampleStyleSheet()
    title_style = create_arabic_style(20, TA_CENTER)
    heading_style = create_arabic_style(16, TA_RIGHT)
    normal_style = create_arabic_style(12, TA_RIGHT)
    bullet_style = create_arabic_style(10, TA_RIGHT)
    
    # محتوى التقرير
    story = []
    
    # العنوان الرئيسي
    story.append(Paragraph("تقرير شامل عن نظام نُظم", title_style))
    story.append(Paragraph("نظام إدارة الموارد البشرية والمركبات المتكامل", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # معلومات التقرير
    story.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y/%m/%d')}", normal_style))
    story.append(Paragraph("النسخة: 2.0.0", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # نظرة عامة
    story.append(Paragraph("نظرة عامة", heading_style))
    overview_text = """
    نظام نُظم هو نظام إدارة متكامل للموارد البشرية والمركبات مصمم خصيصاً للشركات والمؤسسات العربية. 
    يوفر النظام حلولاً شاملة لإدارة الموظفين، تتبع الحضور والانصراف، إدارة المركبات، 
    نظام الرواتب، والتقارير التفصيلية. النظام مبني بتقنيات حديثة ويدعم اللغة العربية بالكامل.
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الميزات الرئيسية
    story.append(Paragraph("الميزات الرئيسية", heading_style))
    
    # إدارة الموظفين
    story.append(Paragraph("1. إدارة الموظفين", create_arabic_style(14, TA_RIGHT)))
    employee_features = [
        "إضافة وتعديل وحذف بيانات الموظفين",
        "تخزين المعلومات الشخصية والوظيفية الكاملة",
        "رفع وإدارة صور الموظفين والوثائق",
        "تصنيف الموظفين حسب الأقسام والوظائف",
        "تتبع تواريخ الالتحاق والعقود",
        "إدارة بيانات الاتصال والعناوين",
        "نظام البحث المتقدم في بيانات الموظفين"
    ]
    
    for feature in employee_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # نظام الحضور والانصراف
    story.append(Paragraph("2. نظام الحضور والانصراف", create_arabic_style(14, TA_RIGHT)))
    attendance_features = [
        "تسجيل الحضور والانصراف اليومي",
        "تتبع أوقات الدخول والخروج",
        "حساب ساعات العمل والإضافي",
        "تسجيل الغياب والإجازات",
        "التقارير اليومية والشهرية للحضور",
        "إنذارات التأخير والغياب",
        "نظام الموافقات للإجازات الطارئة"
    ]
    
    for feature in attendance_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # إدارة المركبات
    story.append(Paragraph("3. إدارة المركبات", create_arabic_style(14, TA_RIGHT)))
    vehicle_features = [
        "قاعدة بيانات شاملة للمركبات",
        "تتبع معلومات المركبات (الطراز، السنة، اللون)",
        "إدارة تأمين المركبات وتواريخ الانتهاء",
        "نظام تسليم واستلام المركبات",
        "ربط المركبات بالسائقين",
        "تتبع حالة المركبات (متاح، قيد الاستخدام، صيانة)",
        "تقارير استخدام المركبات"
    ]
    
    for feature in vehicle_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # نظام الرواتب
    story.append(Paragraph("4. نظام الرواتب", create_arabic_style(14, TA_RIGHT)))
    salary_features = [
        "إدارة الراتب الأساسي والبدلات",
        "حساب الاستقطاعات والمكافآت",
        "كشوفات الرواتب الشهرية",
        "تقارير مالية تفصيلية",
        "ربط الرواتب بساعات العمل",
        "نظام الحوافز والعمولات",
        "تصدير كشوفات الرواتب بصيغة PDF و Excel"
    ]
    
    for feature in salary_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    
    story.append(PageBreak())
    
    # الوحدات المتقدمة
    story.append(Paragraph("الوحدات المتقدمة", heading_style))
    
    # التقارير والتحليلات
    story.append(Paragraph("1. التقارير والتحليلات", create_arabic_style(14, TA_RIGHT)))
    reports_features = [
        "تقارير ملخص الموظفين حسب الأقسام",
        "تحليلات الحضور والغياب الشهرية",
        "تقارير أداء الموظفين",
        "إحصائيات استخدام المركبات",
        "التقارير المالية وكشوفات الرواتب",
        "تحليلات الإنتاجية والكفاءة",
        "رسوم بيانية تفاعلية"
    ]
    
    for feature in reports_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # إدارة المستخدمين والصلاحيات
    story.append(Paragraph("2. إدارة المستخدمين والصلاحيات", create_arabic_style(14, TA_RIGHT)))
    users_features = [
        "نظام مستخدمين متعدد المستويات",
        "صلاحيات مخصصة حسب الأدوار",
        "ربط المستخدمين بأقسام محددة",
        "تحكم في الوصول للوحدات المختلفة",
        "سجل العمليات والتدقيق",
        "نظام كلمات المرور الآمنة",
        "جلسات المستخدمين الآمنة"
    ]
    
    for feature in users_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # بوابة الموظفين
    story.append(Paragraph("3. بوابة الموظفين", create_arabic_style(14, TA_RIGHT)))
    portal_features = [
        "واجهة منفصلة للموظفين",
        "تسجيل دخول بالرقم الوظيفي ورقم الهوية",
        "عرض البيانات الشخصية والوظيفية",
        "استعراض سجلات الحضور والغياب",
        "عرض كشوفات الرواتب",
        "متابعة المركبات المخصصة",
        "تحديث البيانات الشخصية"
    ]
    
    for feature in portal_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الميزات التقنية
    story.append(Paragraph("الميزات التقنية", heading_style))
    
    # التقنيات المستخدمة
    story.append(Paragraph("1. التقنيات المستخدمة", create_arabic_style(14, TA_RIGHT)))
    tech_features = [
        "Python Flask - إطار عمل الويب الخلفي",
        "SQLAlchemy ORM - إدارة قاعدة البيانات",
        "PostgreSQL - قاعدة بيانات قوية ومتقدمة",
        "Bootstrap - واجهة مستخدم متجاوبة",
        "Chart.js - الرسوم البيانية التفاعلية",
        "JWT Authentication - نظام مصادقة آمن",
        "RESTful API - واجهة برمجية متكاملة"
    ]
    
    for feature in tech_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الأمان والحماية
    story.append(Paragraph("2. الأمان والحماية", create_arabic_style(14, TA_RIGHT)))
    security_features = [
        "تشفير كلمات المرور باستخدام Bcrypt",
        "نظام JWT للمصادقة الآمنة",
        "حماية من هجمات CSRF",
        "تشفير الاتصالات HTTPS",
        "سجلات النشاط والتدقيق",
        "صلاحيات محددة للمستخدمين",
        "نسخ احتياطية دورية للبيانات"
    ]
    
    for feature in security_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # API للتطبيقات الجوالة
    story.append(Paragraph("3. API للتطبيقات الجوالة", create_arabic_style(14, TA_RIGHT)))
    api_features = [
        "API شامل يحتوي على 30+ endpoint",
        "دعم كامل لجميع وظائف النظام",
        "مصادقة JWT للتطبيقات الجوالة",
        "استجابات JSON منظمة ومتسقة",
        "معالجة الأخطاء المتقدمة",
        "توثيق شامل للمطورين",
        "أمثلة عملية للتطبيق والاختبار"
    ]
    
    for feature in api_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    
    story.append(PageBreak())
    
    # الإحصائيات والأرقام
    story.append(Paragraph("الإحصائيات والأرقام", heading_style))
    
    stats_data = [
        ["المقياس", "العدد", "الوصف"],
        ["عدد الموظفين المدعومين", "غير محدود", "لا توجد قيود على عدد الموظفين"],
        ["عدد الأقسام", "غير محدود", "إمكانية إنشاء أقسام متعددة"],
        ["عدد المركبات", "غير محدود", "قاعدة بيانات شاملة للمركبات"],
        ["عدد المستخدمين", "غير محدود", "نظام مستخدمين متعدد المستويات"],
        ["تقارير النظام", "15+ تقرير", "تقارير متنوعة وتحليلات متقدمة"],
        ["API Endpoints", "30+ endpoint", "واجهة برمجية شاملة"],
        ["أنواع الملفات المدعومة", "PDF, Excel, صور", "تصدير وتحميل متعدد الصيغ"]
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # فوائد النظام
    story.append(Paragraph("فوائد النظام", heading_style))
    benefits = [
        "تحسين كفاءة إدارة الموارد البشرية",
        "توفير الوقت في العمليات الإدارية",
        "دقة في تتبع الحضور والغياب",
        "شفافية في نظام الرواتب",
        "تحكم أفضل في المركبات والأصول",
        "تقارير دقيقة لاتخاذ القرارات",
        "أمان عالي لحماية البيانات",
        "واجهة سهلة الاستخدام باللغة العربية"
    ]
    
    for benefit in benefits:
        story.append(Paragraph(f"• {benefit}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # متطلبات النظام
    story.append(Paragraph("متطلبات النظام", heading_style))
    
    # متطلبات الخادم
    story.append(Paragraph("متطلبات الخادم:", create_arabic_style(12, TA_RIGHT)))
    server_requirements = [
        "نظام التشغيل: Linux/Windows/macOS",
        "Python 3.8 أو أحدث",
        "قاعدة بيانات PostgreSQL",
        "ذاكرة: 2GB RAM كحد أدنى",
        "مساحة التخزين: 10GB متاحة",
        "اتصال إنترنت مستقر"
    ]
    
    for req in server_requirements:
        story.append(Paragraph(f"• {req}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # متطلبات العميل
    story.append(Paragraph("متطلبات العميل:", create_arabic_style(12, TA_RIGHT)))
    client_requirements = [
        "متصفح ويب حديث (Chrome, Firefox, Safari, Edge)",
        "دعم JavaScript مفعل",
        "اتصال إنترنت مستقر",
        "دقة شاشة: 1024x768 كحد أدنى",
        "دعم اللغة العربية في المتصفح"
    ]
    
    for req in client_requirements:
        story.append(Paragraph(f"• {req}", bullet_style))
    
    story.append(PageBreak())
    
    # خطة التطوير المستقبلية
    story.append(Paragraph("خطة التطوير المستقبلية", heading_style))
    
    future_features = [
        "تطبيق جوال أصلي لنظامي iOS و Android",
        "نظام إشعارات متقدم عبر البريد الإلكتروني والـ SMS",
        "تكامل مع أنظمة الحضور البيومترية",
        "ذكاء اصطناعي لتحليل الأداء والتنبؤ",
        "نظام إدارة المشاريع والمهام",
        "تكامل مع أنظمة المحاسبة الخارجية",
        "نظام إدارة الوثائق المتقدم",
        "دعم لغات إضافية",
        "نظام التوقيعات الإلكترونية",
        "تحليلات متقدمة بالذكاء الاصطناعي"
    ]
    
    for feature in future_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الخلاصة
    story.append(Paragraph("الخلاصة", heading_style))
    conclusion_text = """
    نظام نُظم هو حل متكامل وشامل لإدارة الموارد البشرية والمركبات، يجمع بين السهولة في الاستخدام والقوة التقنية.
    يوفر النظام جميع الأدوات اللازمة للشركات والمؤسسات لإدارة عملياتها بكفاءة عالية وأمان متقدم.
    
    مع دعم كامل للغة العربية وواجهة برمجية متطورة للتطبيقات الجوالة، يعد نظام نُظم الخيار الأمثل
    للمؤسسات التي تسعى لتحسين كفاءة العمل وتبسيط العمليات الإدارية.
    
    النظام قابل للتطوير والتوسع، ويمكن تخصيصه ليناسب احتياجات كل مؤسسة على حدة.
    """
    story.append(Paragraph(conclusion_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # معلومات الاتصال
    story.append(Paragraph("معلومات التقرير", heading_style))
    story.append(Paragraph(f"تاريخ الإنتاج: {datetime.now().strftime('%Y/%m/%d %H:%M')}", normal_style))
    story.append(Paragraph("نظام نُظم - الإصدار 2.0.0", normal_style))
    story.append(Paragraph("تقرير تم إنتاجه تلقائياً من النظام", normal_style))
    
    # إنشاء المستند
    doc.build(story)
    
    return filename

if __name__ == "__main__":
    filename = generate_nuzum_report()
    print(f"تم إنشاء التقرير بنجاح: {filename}")