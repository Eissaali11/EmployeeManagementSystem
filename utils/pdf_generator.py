from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import pdfkit

def generate_salary_report_pdf(salaries, month, year):
    """
    Generate a PDF report for salary data
    
    Args:
        salaries: List of Salary objects
        month: Month number
        year: Year
        
    Returns:
        Bytes containing the PDF file
    """
    try:
        # Reshape Arabic text for PDF
        def reshape_arabic(text):
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        
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
        
        # Create HTML
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 20px;
                    direction: rtl;
                    text-align: right;
                }}
                h1, h2 {{
                    text-align: center;
                    color: #333;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: right;
                }}
                th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .summary {{
                    margin-top: 30px;
                    border-top: 2px solid #333;
                    padding-top: 10px;
                }}
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #666;
                }}
            </style>
            <title>تقرير الرواتب</title>
        </head>
        <body>
            <h1>تقرير الرواتب</h1>
            <h2>شهر {reshape_arabic(month_name)} {year}</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>م</th>
                        <th>اسم الموظف</th>
                        <th>الرقم الوظيفي</th>
                        <th>الراتب الأساسي</th>
                        <th>البدلات</th>
                        <th>الخصومات</th>
                        <th>المكافآت</th>
                        <th>صافي الراتب</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add rows for each salary
        for i, salary in enumerate(salaries):
            html_content += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{reshape_arabic(salary.employee.name)}</td>
                    <td>{reshape_arabic(salary.employee.employee_id)}</td>
                    <td>{salary.basic_salary:.2f}</td>
                    <td>{salary.allowances:.2f}</td>
                    <td>{salary.deductions:.2f}</td>
                    <td>{salary.bonus:.2f}</td>
                    <td>{salary.net_salary:.2f}</td>
                </tr>
            """
        
        # Add summary row
        html_content += f"""
                </tbody>
                <tfoot>
                    <tr>
                        <th colspan="3">المجموع</th>
                        <th>{total_basic:.2f}</th>
                        <th>{total_allowances:.2f}</th>
                        <th>{total_deductions:.2f}</th>
                        <th>{total_bonus:.2f}</th>
                        <th>{total_net:.2f}</th>
                    </tr>
                </tfoot>
            </table>
            
            <div class="summary">
                <p><strong>إجمالي الرواتب الأساسية:</strong> {total_basic:.2f}</p>
                <p><strong>إجمالي البدلات:</strong> {total_allowances:.2f}</p>
                <p><strong>إجمالي الخصومات:</strong> {total_deductions:.2f}</p>
                <p><strong>إجمالي المكافآت:</strong> {total_bonus:.2f}</p>
                <p><strong>إجمالي صافي الرواتب:</strong> {total_net:.2f}</p>
            </div>
            
            <div class="footer">
                <p>تم إنشاء هذا التقرير في {reshape_arabic(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
                <p>نظام إدارة الموظفين - جميع الحقوق محفوظة</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF from HTML
        options = {
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdf = pdfkit.from_string(html_content, False, options=options)
        return pdf
    
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")
