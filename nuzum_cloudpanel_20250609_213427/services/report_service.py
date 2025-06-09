"""
خدمة التقارير والإحصائيات
"""
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from models import Employee, Attendance, Salary, Document, Vehicle, Department
from core.extensions import db
import pandas as pd
from io import BytesIO

class ReportService:
    """خدمة إنشاء التقارير والإحصائيات"""
    
    @staticmethod
    def get_employee_statistics():
        """إحصائيات الموظفين"""
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status='active').count()
        inactive_employees = Employee.query.filter_by(status='inactive').count()
        
        # إحصائيات حسب القسم
        department_stats = db.session.query(
            Department.name,
            func.count(Employee.id).label('employee_count')
        ).outerjoin(Employee).group_by(Department.id, Department.name).all()
        
        return {
            'total': total_employees,
            'active': active_employees,
            'inactive': inactive_employees,
            'by_department': [{'name': stat[0], 'count': stat[1]} for stat in department_stats]
        }
    
    @staticmethod
    def get_attendance_statistics(start_date=None, end_date=None):
        """إحصائيات الحضور"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        query = Attendance.query.filter(
            Attendance.date.between(start_date, end_date)
        )
        
        total_records = query.count()
        present_count = query.filter_by(status='present').count()
        absent_count = query.filter_by(status='absent').count()
        leave_count = query.filter_by(status='leave').count()
        
        # إحصائيات يومية
        daily_stats = db.session.query(
            Attendance.date,
            func.count(Attendance.id).label('total'),
            func.sum(func.case([(Attendance.status == 'present', 1)], else_=0)).label('present'),
            func.sum(func.case([(Attendance.status == 'absent', 1)], else_=0)).label('absent')
        ).filter(
            Attendance.date.between(start_date, end_date)
        ).group_by(Attendance.date).order_by(Attendance.date).all()
        
        return {
            'total_records': total_records,
            'present': present_count,
            'absent': absent_count,
            'leave': leave_count,
            'daily_stats': [
                {
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'total': stat.total,
                    'present': stat.present,
                    'absent': stat.absent
                } for stat in daily_stats
            ]
        }
    
    @staticmethod
    def get_salary_statistics(year=None, month=None):
        """إحصائيات الرواتب"""
        if not year:
            year = datetime.now().year
        
        query = Salary.query.filter_by(year=year)
        if month:
            query = query.filter_by(month=month)
        
        total_salaries = query.count()
        total_amount = db.session.query(func.sum(Salary.net_salary)).filter_by(year=year)
        if month:
            total_amount = total_amount.filter_by(month=month)
        total_amount = total_amount.scalar() or 0
        
        avg_salary = db.session.query(func.avg(Salary.net_salary)).filter_by(year=year)
        if month:
            avg_salary = avg_salary.filter_by(month=month)
        avg_salary = avg_salary.scalar() or 0
        
        # إحصائيات شهرية للسنة
        monthly_stats = db.session.query(
            Salary.month,
            func.count(Salary.id).label('count'),
            func.sum(Salary.net_salary).label('total_amount'),
            func.avg(Salary.net_salary).label('avg_amount')
        ).filter_by(year=year).group_by(Salary.month).order_by(Salary.month).all()
        
        return {
            'total_salaries': total_salaries,
            'total_amount': round(total_amount, 2),
            'average_salary': round(avg_salary, 2),
            'monthly_stats': [
                {
                    'month': stat.month,
                    'count': stat.count,
                    'total_amount': round(stat.total_amount or 0, 2),
                    'avg_amount': round(stat.avg_amount or 0, 2)
                } for stat in monthly_stats
            ]
        }
    
    @staticmethod
    def get_document_expiry_report(days_ahead=30):
        """تقرير انتهاء صلاحية الوثائق"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        expiring_docs = db.session.query(
            Document,
            Employee.name.label('employee_name'),
            Employee.mobile.label('employee_mobile')
        ).join(Employee).filter(
            and_(
                Document.expiry_date.isnot(None),
                Document.expiry_date <= cutoff_date,
                Document.expiry_date >= date.today()
            )
        ).order_by(Document.expiry_date).all()
        
        expired_docs = db.session.query(
            Document,
            Employee.name.label('employee_name'),
            Employee.mobile.label('employee_mobile')
        ).join(Employee).filter(
            and_(
                Document.expiry_date.isnot(None),
                Document.expiry_date < date.today()
            )
        ).order_by(Document.expiry_date.desc()).all()
        
        return {
            'expiring_soon': [
                {
                    'document_id': doc.Document.id,
                    'employee_name': doc.employee_name,
                    'employee_mobile': doc.employee_mobile,
                    'document_type': doc.Document.document_type,
                    'document_number': doc.Document.document_number,
                    'expiry_date': doc.Document.expiry_date.strftime('%Y-%m-%d'),
                    'days_remaining': (doc.Document.expiry_date - date.today()).days
                } for doc in expiring_docs
            ],
            'expired': [
                {
                    'document_id': doc.Document.id,
                    'employee_name': doc.employee_name,
                    'employee_mobile': doc.employee_mobile,
                    'document_type': doc.Document.document_type,
                    'document_number': doc.Document.document_number,
                    'expiry_date': doc.Document.expiry_date.strftime('%Y-%m-%d'),
                    'days_overdue': (date.today() - doc.Document.expiry_date).days
                } for doc in expired_docs
            ]
        }
    
    @staticmethod
    def generate_excel_report(data, report_type, filename=None):
        """إنشاء تقرير Excel"""
        if not filename:
            filename = f'{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if report_type == 'employees':
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='الموظفين', index=False)
            
            elif report_type == 'attendance':
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='الحضور', index=False)
            
            elif report_type == 'salaries':
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='الرواتب', index=False)
            
            elif report_type == 'documents':
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='الوثائق', index=False)
        
        output.seek(0)
        return output, filename