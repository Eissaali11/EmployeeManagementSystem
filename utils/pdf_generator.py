from datetime import datetime
from utils.arabic_pdf import reshape_arabic_text, get_arabic_styles, create_rtl_table, create_arabic_pdf
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
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
        
        # Get Arabic styles
        styles = get_arabic_styles()
        
        # Create elements list
        elements = []
        
        # Add title
        elements.append(Paragraph(reshape_arabic_text('تقرير الرواتب'), styles['title']))
        elements.append(Paragraph(reshape_arabic_text(f'شهر {month_name} {year}'), styles['heading']))
        elements.append(Spacer(1, 10))
        
        # Create table data
        data = [
            [
                reshape_arabic_text('م'),
                reshape_arabic_text('اسم الموظف'),
                reshape_arabic_text('الرقم الوظيفي'),
                reshape_arabic_text('الراتب الأساسي'),
                reshape_arabic_text('البدلات'),
                reshape_arabic_text('الخصومات'),
                reshape_arabic_text('المكافآت'),
                reshape_arabic_text('صافي الراتب')
            ]
        ]
        
        # Add rows for each salary
        for i, salary in enumerate(salaries):
            data.append([
                str(i+1),
                reshape_arabic_text(salary.employee.name),
                reshape_arabic_text(salary.employee.employee_id),
                f"{salary.basic_salary:.2f}",
                f"{salary.allowances:.2f}",
                f"{salary.deductions:.2f}",
                f"{salary.bonus:.2f}",
                f"{salary.net_salary:.2f}"
            ])
        
        # Add summary row
        data.append([
            '',
            reshape_arabic_text('المجموع'),
            '',
            f"{total_basic:.2f}",
            f"{total_allowances:.2f}",
            f"{total_deductions:.2f}",
            f"{total_bonus:.2f}",
            f"{total_net:.2f}"
        ])
        
        # Create table with specific column widths
        col_widths = [1*cm, 4*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm]
        
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
        
        # Create and add table
        table = Table(data, repeatRows=1, colWidths=col_widths)
        table.setStyle(table_style)
        elements.append(table)
        
        # Create summary table
        elements.append(Spacer(1, 20))
        
        summary_data = [
            [reshape_arabic_text("البيان"), reshape_arabic_text("المبلغ")],
            [reshape_arabic_text("إجمالي الرواتب الأساسية"), f"{total_basic:.2f}"],
            [reshape_arabic_text("إجمالي البدلات"), f"{total_allowances:.2f}"],
            [reshape_arabic_text("إجمالي الخصومات"), f"{total_deductions:.2f}"],
            [reshape_arabic_text("إجمالي المكافآت"), f"{total_bonus:.2f}"],
            [reshape_arabic_text("إجمالي صافي الرواتب"), f"{total_net:.2f}"],
        ]
        
        # Create summary table style
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
        
        # Create and add summary table
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_table.setStyle(summary_style)
        elements.append(summary_table)
        
        # Add footer
        elements.append(Spacer(1, 30))
        
        # Create footer data
        footer_data = [
            [reshape_arabic_text(f'تم إنشاء هذا التقرير في {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')],
            [reshape_arabic_text('نظام إدارة الموظفين - جميع الحقوق محفوظة')],
        ]
        
        # Create footer style
        footer_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ])
        
        # Create and add footer table
        footer_table = Table(footer_data, colWidths=[18*cm])
        footer_table.setStyle(footer_style)
        elements.append(footer_table)
        
        # Create PDF with landscape orientation and return data
        return create_arabic_pdf(elements, title="تقرير الرواتب", landscape_mode=True)
    
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")
