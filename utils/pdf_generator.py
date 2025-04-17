from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

def generate_salary_report_pdf(salaries, month, year):
    """
    Generate a PDF report for salary data using ReportLab
    
    Args:
        salaries: List of Salary objects
        month: Month number
        year: Year
        
    Returns:
        Bytes containing the PDF file
    """
    try:
        # Reshape Arabic text for PDF
        def arabic_text(text):
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        
        # Register default font
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        
        # Use the default Helvetica font which is built into ReportLab
        arabicFontName = 'Helvetica'
        
        # Register font family
        registerFontFamily(arabicFontName, normal=arabicFontName)
        
        # Get month name in Arabic
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(month, str(month))
        
        # Calculate totals
        total_basic = sum(s.basic_salary for s in salaries)
        total_allowances = sum(s.allowances for s in salaries)
        total_deductions = sum(s.deductions for s in salaries)
        total_bonus = sum(s.bonus for s in salaries)
        total_net = sum(s.net_salary for s in salaries)
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create PDF document with landscape orientation
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),  # Use landscape orientation
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Create title style
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            alignment=1,  # 1=center
            fontName='Helvetica',
            fontSize=16,
            spaceAfter=12
        )
        
        # Create heading style
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            alignment=1,  # 1=center
            fontName='Helvetica',
            fontSize=14,
            spaceAfter=12
        )
        
        # Create normal text style with RTL support
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            alignment=2,  # 2=right for RTL
            fontName='Helvetica',
            fontSize=10,
            leading=14
        )
        
        # Create elements list
        elements = []
        
        # Add title
        elements.append(Paragraph(arabic_text('تقرير الرواتب'), title_style))
        elements.append(Paragraph(arabic_text(f'شهر {month_name} {year}'), heading_style))
        elements.append(Spacer(1, 10))
        
        # Create table data
        data = [
            [
                arabic_text('م'),
                arabic_text('اسم الموظف'),
                arabic_text('الرقم الوظيفي'),
                arabic_text('الراتب الأساسي'),
                arabic_text('البدلات'),
                arabic_text('الخصومات'),
                arabic_text('المكافآت'),
                arabic_text('صافي الراتب')
            ]
        ]
        
        # Add rows for each salary
        for i, salary in enumerate(salaries):
            data.append([
                str(i+1),
                arabic_text(salary.employee.name),
                arabic_text(salary.employee.employee_id),
                f"{salary.basic_salary:.2f}",
                f"{salary.allowances:.2f}",
                f"{salary.deductions:.2f}",
                f"{salary.bonus:.2f}",
                f"{salary.net_salary:.2f}"
            ])
        
        # Add summary row
        data.append([
            '',
            arabic_text('المجموع'),
            '',
            f"{total_basic:.2f}",
            f"{total_allowances:.2f}",
            f"{total_deductions:.2f}",
            f"{total_bonus:.2f}",
            f"{total_net:.2f}"
        ])
        
        # Create table with specific column widths
        col_widths = [1*cm, 4*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm]
        table = Table(data, repeatRows=1, colWidths=col_widths)
        
        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (7, -1), 'CENTER'),  # Numbers are centered
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, -1), (2, -1)),  # Span cells for 'المجموع'
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),  # Thicker line below header
        ])
        
        # Add alternating row colors
        for i in range(1, len(data)-1):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightskyblue)
        
        table.setStyle(table_style)
        elements.append(table)
        
        # Create summary table
        summary_data = [
            [arabic_text("البيان"), arabic_text("المبلغ")],
            [arabic_text("إجمالي الرواتب الأساسية"), f"{total_basic:.2f}"],
            [arabic_text("إجمالي البدلات"), f"{total_allowances:.2f}"],
            [arabic_text("إجمالي الخصومات"), f"{total_deductions:.2f}"],
            [arabic_text("إجمالي المكافآت"), f"{total_bonus:.2f}"],
            [arabic_text("إجمالي صافي الرواتب"), f"{total_net:.2f}"],
        ]
        
        elements.append(Spacer(1, 20))
        
        # Create summary table
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ])
        
        # Add alternating row colors for summary table
        for i in range(1, len(summary_data)):
            if i % 2 == 0:
                summary_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                
        summary_table.setStyle(summary_style)
        elements.append(summary_table)
        
        # Add footer
        elements.append(Spacer(1, 30))
        
        # Create footer table for better alignment
        footer_data = [
            [arabic_text(f'تم إنشاء هذا التقرير في {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')],
            [arabic_text('نظام إدارة الموظفين - جميع الحقوق محفوظة')],
        ]
        
        footer_table = Table(footer_data, colWidths=[18*cm])
        footer_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ])
        
        footer_table.setStyle(footer_style)
        elements.append(footer_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")
