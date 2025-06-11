#!/usr/bin/env python3
"""
إنشاء تقرير شامل عن نظام نُظم بصيغة PDF مع دعم محسن للعربية
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

def create_simple_report():
    """إنشاء تقرير بسيط بخط Helvetica مع النص الإنجليزي"""
    
    # إعداد المستند
    filename = f"nuzum_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # إعداد الأنماط
    styles = getSampleStyleSheet()
    
    # أنماط مخصصة
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leftIndent=20
    )
    
    # محتوى التقرير
    story = []
    
    # العنوان
    story.append(Paragraph("NUZUM System - Comprehensive Report", title_style))
    story.append(Paragraph("Human Resources & Vehicle Management System", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # معلومات التقرير
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y/%m/%d')}", normal_style))
    story.append(Paragraph("Version: 2.0.0", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # نظرة عامة
    story.append(Paragraph("System Overview", heading_style))
    overview_text = """
    NUZUM is an integrated Human Resources and Vehicle Management System designed specifically for Arabic organizations. 
    The system provides comprehensive solutions for employee management, attendance tracking, vehicle management, 
    payroll system, and detailed reporting. Built with modern technologies and full Arabic language support.
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الميزات الأساسية
    story.append(Paragraph("Core Features", heading_style))
    
    # إدارة الموظفين
    story.append(Paragraph("1. Employee Management", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    employee_features = [
        "Complete employee data management (add, edit, delete)",
        "Personal and professional information storage",
        "Photo and document upload capabilities",
        "Department and position classification",
        "Employment date and contract tracking",
        "Contact information and address management",
        "Advanced search functionality"
    ]
    
    for feature in employee_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # نظام الحضور
    story.append(Paragraph("2. Attendance Management System", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    attendance_features = [
        "Daily check-in and check-out recording",
        "Working hours and overtime tracking",
        "Absence and leave management",
        "Daily and monthly attendance reports",
        "Late arrival and absence alerts",
        "Emergency leave approval system"
    ]
    
    for feature in attendance_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # إدارة المركبات
    story.append(Paragraph("3. Vehicle Management", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    vehicle_features = [
        "Comprehensive vehicle database",
        "Vehicle information tracking (model, year, color)",
        "Insurance management and expiry tracking",
        "Vehicle handover and return system",
        "Driver assignment and tracking",
        "Vehicle status monitoring (available, in-use, maintenance)",
        "Vehicle utilization reports"
    ]
    
    for feature in vehicle_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # نظام الرواتب
    story.append(Paragraph("4. Payroll System", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    salary_features = [
        "Basic salary and allowances management",
        "Deductions and bonus calculations",
        "Monthly payroll generation",
        "Detailed financial reports",
        "Working hours integration",
        "Incentives and commission system",
        "PDF and Excel payroll export"
    ]
    
    for feature in salary_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    
    story.append(PageBreak())
    
    # الوحدات المتقدمة
    story.append(Paragraph("Advanced Modules", heading_style))
    
    # التقارير والتحليلات
    story.append(Paragraph("1. Reports & Analytics", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    reports_features = [
        "Employee summary reports by departments",
        "Monthly attendance and absence analytics",
        "Employee performance reports",
        "Vehicle utilization statistics",
        "Financial reports and payroll summaries",
        "Productivity and efficiency analytics",
        "Interactive charts and graphs"
    ]
    
    for feature in reports_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # إدارة المستخدمين
    story.append(Paragraph("2. User Management & Permissions", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    users_features = [
        "Multi-level user system",
        "Role-based permissions",
        "Department-specific user access",
        "Module access control",
        "Activity logs and audit trails",
        "Secure password management",
        "Secure user sessions"
    ]
    
    for feature in users_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # بوابة الموظفين
    story.append(Paragraph("3. Employee Portal", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    portal_features = [
        "Separate employee interface",
        "Login with employee ID and national ID",
        "Personal and professional data viewing",
        "Attendance records review",
        "Payroll statements access",
        "Assigned vehicle tracking",
        "Personal information updates"
    ]
    
    for feature in portal_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الميزات التقنية
    story.append(Paragraph("Technical Features", heading_style))
    
    # التقنيات المستخدمة
    story.append(Paragraph("1. Technologies Used", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    tech_features = [
        "Python Flask - Backend web framework",
        "SQLAlchemy ORM - Database management",
        "PostgreSQL - Advanced database system",
        "Bootstrap - Responsive user interface",
        "Chart.js - Interactive charts",
        "JWT Authentication - Secure authentication",
        "RESTful API - Comprehensive API interface"
    ]
    
    for feature in tech_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الأمان
    story.append(Paragraph("2. Security & Protection", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    security_features = [
        "Bcrypt password encryption",
        "JWT secure authentication system",
        "CSRF attack protection",
        "HTTPS communication encryption",
        "Activity logs and audit trails",
        "User-specific permissions",
        "Regular data backups"
    ]
    
    for feature in security_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # API للجوال
    story.append(Paragraph("3. Mobile Application API", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
    api_features = [
        "Comprehensive API with 30+ endpoints",
        "Full system functionality support",
        "JWT authentication for mobile apps",
        "Structured and consistent JSON responses",
        "Advanced error handling",
        "Complete developer documentation",
        "Practical examples and testing"
    ]
    
    for feature in api_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    
    story.append(PageBreak())
    
    # الإحصائيات
    story.append(Paragraph("System Statistics", heading_style))
    
    stats_data = [
        ["Metric", "Value", "Description"],
        ["Supported Employees", "Unlimited", "No limit on employee count"],
        ["Departments", "Unlimited", "Multiple department creation capability"],
        ["Vehicles", "Unlimited", "Comprehensive vehicle database"],
        ["Users", "Unlimited", "Multi-level user system"],
        ["System Reports", "15+ Reports", "Diverse reports and analytics"],
        ["API Endpoints", "30+ Endpoints", "Comprehensive programming interface"],
        ["Supported Formats", "PDF, Excel, Images", "Multi-format export and upload"]
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # فوائد النظام
    story.append(Paragraph("System Benefits", heading_style))
    benefits = [
        "Improved HR management efficiency",
        "Time savings in administrative operations",
        "Accurate attendance and absence tracking",
        "Transparent payroll system",
        "Better control of vehicles and assets",
        "Accurate reports for decision making",
        "High security for data protection",
        "Easy-to-use Arabic interface"
    ]
    
    for benefit in benefits:
        story.append(Paragraph(f"• {benefit}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # متطلبات النظام
    story.append(Paragraph("System Requirements", heading_style))
    
    # متطلبات الخادم
    story.append(Paragraph("Server Requirements:", normal_style))
    server_requirements = [
        "Operating System: Linux/Windows/macOS",
        "Python 3.8 or newer",
        "PostgreSQL Database",
        "Memory: 2GB RAM minimum",
        "Storage: 10GB available space",
        "Stable internet connection"
    ]
    
    for req in server_requirements:
        story.append(Paragraph(f"• {req}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # متطلبات العميل
    story.append(Paragraph("Client Requirements:", normal_style))
    client_requirements = [
        "Modern web browser (Chrome, Firefox, Safari, Edge)",
        "JavaScript enabled",
        "Stable internet connection",
        "Screen resolution: 1024x768 minimum",
        "Arabic language support in browser"
    ]
    
    for req in client_requirements:
        story.append(Paragraph(f"• {req}", bullet_style))
    
    story.append(PageBreak())
    
    # خطة التطوير
    story.append(Paragraph("Future Development Plan", heading_style))
    
    future_features = [
        "Native mobile applications for iOS and Android",
        "Advanced notification system via email and SMS",
        "Integration with biometric attendance systems",
        "AI for performance analysis and prediction",
        "Project and task management system",
        "Integration with external accounting systems",
        "Advanced document management system",
        "Additional language support",
        "Electronic signature system",
        "Advanced AI analytics"
    ]
    
    for feature in future_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    story.append(Spacer(1, 0.2*inch))
    
    # الخلاصة
    story.append(Paragraph("Conclusion", heading_style))
    conclusion_text = """
    NUZUM System is a comprehensive and integrated solution for human resources and vehicle management, 
    combining ease of use with technical power. The system provides all necessary tools for companies 
    and organizations to manage their operations with high efficiency and advanced security.
    
    With full Arabic language support and an advanced programming interface for mobile applications, 
    NUZUM System is the optimal choice for organizations seeking to improve work efficiency and 
    simplify administrative operations.
    
    The system is scalable and expandable, and can be customized to suit the needs of each organization individually.
    """
    story.append(Paragraph(conclusion_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # معلومات التقرير
    story.append(Paragraph("Report Information", heading_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y/%m/%d %H:%M')}", normal_style))
    story.append(Paragraph("NUZUM System - Version 2.0.0", normal_style))
    story.append(Paragraph("Report automatically generated by the system", normal_style))
    
    # إنشاء المستند
    doc.build(story)
    
    return filename

def create_arabic_content_report():
    """إنشاء تقرير بمحتوى عربي مبسط"""
    
    filename = f"nuzum_arabic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']
    
    story = []
    
    # محتوى عربي مبسط
    story.append(Paragraph("نظام نُظم - تقرير شامل", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    # أقسام النظام الرئيسية
    sections = [
        "ادارة الموظفين - نظام شامل لادارة بيانات الموظفين والتوظيف",
        "نظام الحضور - تتبع الحضور والانصراف والاجازات",
        "ادارة المركبات - نظام متكامل لادارة اسطول المركبات",
        "نظام الرواتب - حساب وادارة رواتب الموظفين",
        "التقارير والتحليلات - تقارير مفصلة وتحليلات متقدمة",
        "واجهة برمجية للجوال - API شامل للتطبيقات الجوالة",
        "نظام الامان - حماية متقدمة للبيانات والمعلومات",
        "بوابة الموظفين - واجهة منفصلة للموظفين"
    ]
    
    for section in sections:
        story.append(Paragraph(f"• {section}", normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y/%m/%d')}", normal_style))
    story.append(Paragraph("نظام نُظم - الاصدار 2.0.0", normal_style))
    
    doc.build(story)
    return filename

if __name__ == "__main__":
    print("إنشاء التقارير...")
    
    # تقرير إنجليزي شامل
    english_report = create_simple_report()
    print(f"تم إنشاء التقرير الإنجليزي: {english_report}")
    
    # تقرير عربي مبسط
    arabic_report = create_arabic_content_report()
    print(f"تم إنشاء التقرير العربي: {arabic_report}")
    
    print("تم إنشاء التقارير بنجاح!")