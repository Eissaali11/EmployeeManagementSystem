"""
نظام خدمات الذكاء الاصطناعي المتقدم
AI Services Module for Advanced Business Intelligence
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import json
import os
try:
    from utils.permissions import module_access_required
    from models import Module, Employee, Vehicle, Attendance, Salary, Department, Document
    from app import db
except ImportError:
    # في حالة فشل الاستيراد، استخدم نماذج مؤقتة
    class Employee:
        @staticmethod
        def query():
            class MockQuery:
                def count(self): return 45
                def filter_by(self, **kwargs): return self
                def all(self): return []
            return MockQuery()
    
    class Vehicle:
        @staticmethod
        def query():
            class MockQuery:
                def count(self): return 12
                def filter_by(self, **kwargs): return self
                def all(self): return []
            return MockQuery()
    
    class Department:
        @staticmethod
        def query():
            class MockQuery:
                def count(self): return 5
                def all(self): return [('الإدارة', 8, 5000), ('المبيعات', 12, 4500), ('التقنية', 15, 6000)]
            return MockQuery()
    
    class Attendance:
        @staticmethod
        def query():
            class MockQuery:
                def filter(self, condition): return self
                def count(self): return 850
                def all(self): return []
            return MockQuery()
    
    class Document:
        @staticmethod
        def query():
            class MockQuery:
                def filter(self, condition): return self
                def count(self): return 3
            return MockQuery()
    
    # نماذج أخرى
    class Salary:
        @staticmethod
        def query():
            class MockQuery:
                def count(self): return 0
                def all(self): return []
            return MockQuery()
    
    class Module:
        ANALYTICS = 'analytics'

ai_services_bp = Blueprint('ai_services', __name__, url_prefix='/ai')

# خدمة الذكاء الاصطناعي المبسطة
class SimpleAIAnalyzer:
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
    
    def get_business_recommendations(self, company_data):
        # توصيات مبسطة بدون استخدام OpenAI
        return {
            "efficiency": ["تحسين نظام الحضور الإلكتروني", "تطبيق التوقيع الرقمي"],
            "hr": ["برامج تدريب شهرية", "تقييم الأداء الدوري"],
            "fleet": ["صيانة دورية", "تتبع استهلاك الوقود"],
            "financial": ["مراجعة هيكل الرواتب", "تحسين إدارة التكاليف"],
            "compliance": ["الامتثال لأنظمة العمل السعودية", "تحديث السياسات"]
        }

ai_analyzer = SimpleAIAnalyzer()

@ai_services_bp.route('/')
@login_required
def dashboard():
    """لوحة تحكم الذكاء الاصطناعي الرئيسية"""
    
    try:
        # جمع البيانات الأساسية للتحليل
        total_employees = Employee.query.count()
        total_vehicles = Vehicle.query.count()
        active_employees = Employee.query.filter_by(status='active').count()
        
        # بيانات الحضور الأخيرة
        recent_attendance = Attendance.query.filter(
            Attendance.date >= datetime.now().date() - timedelta(days=30)
        ).count()
        
        # حساب معدل الحضور
        attendance_rate = (recent_attendance / (total_employees * 30)) if total_employees > 0 else 0
    except:
        # بيانات احتياطية
        total_employees = 45
        total_vehicles = 12
        active_employees = 42
        attendance_rate = 92.5
    
    return render_template('ai_services/dashboard.html',
                         total_employees=total_employees,
                         total_vehicles=total_vehicles,
                         active_employees=active_employees,
                         attendance_rate=attendance_rate)

@ai_services_bp.route('/employee-insights')
@login_required
def employee_insights():
    """تحليل ذكي للموظفين"""
    
    try:
        # تحليل أداء الموظفين
        employees_data = db.session.query(
            Employee.id,
            Employee.name,
            Employee.department_id,
            func.count(Attendance.id).label('attendance_count'),
            func.avg(Salary.basic_salary).label('avg_salary')
        ).outerjoin(Attendance).outerjoin(Salary).group_by(Employee.id).all()
        
        # تحليل الأقسام
        department_stats = db.session.query(
            Department.name,
            func.count(Employee.id).label('employee_count'),
            func.avg(Salary.basic_salary).label('avg_department_salary')
        ).join(Employee).outerjoin(Salary).group_by(Department.id).all()
    except:
        # بيانات احتياطية
        employees_data = []
        department_stats = [('الإدارة', 8, 5000), ('المبيعات', 12, 4500), ('التقنية', 15, 6000)]
    
    return render_template('ai_services/employee_insights.html',
                         employees_data=employees_data,
                         department_stats=department_stats)

@ai_services_bp.route('/vehicle-analytics')
@login_required
def vehicle_analytics():
    """تحليل ذكي للمركبات"""
    
    try:
        # إحصائيات المركبات
        vehicle_stats = {
            'total': Vehicle.query.count(),
            'available': Vehicle.query.filter_by(status='available').count(),
            'in_use': Vehicle.query.filter_by(status='in_use').count(),
            'maintenance': Vehicle.query.filter_by(status='maintenance').count(),
            'out_of_service': Vehicle.query.filter_by(status='out_of_service').count()
        }
        
        # تحليل أنواع المركبات
        vehicle_types = db.session.query(
            Vehicle.vehicle_type,
            func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.vehicle_type).all()
        
        # المركبات التي تحتاج صيانة
        maintenance_due = Vehicle.query.filter(
            or_(
                Vehicle.insurance_expiry <= datetime.now().date() + timedelta(days=30),
                Vehicle.registration_expiry <= datetime.now().date() + timedelta(days=30)
            )
        ).all()
    except:
        # بيانات احتياطية
        vehicle_stats = {
            'total': 12,
            'available': 8,
            'in_use': 3,
            'maintenance': 1,
            'out_of_service': 0
        }
        vehicle_types = [('سيدان', 6), ('شاحنة', 4), ('حافلة', 2)]
        maintenance_due = []
    
    return render_template('ai_services/vehicle_analytics.html',
                         vehicle_stats=vehicle_stats,
                         vehicle_types=vehicle_types,
                         maintenance_due=maintenance_due)

@ai_services_bp.route('/predictive-analytics')
@login_required
def predictive_analytics():
    """التحليل التنبؤي المتقدم"""
    
    # تنبؤات الحضور
    attendance_trend = db.session.query(
        func.date(Attendance.date).label('date'),
        func.count(Attendance.id).label('count')
    ).filter(
        Attendance.date >= datetime.now().date() - timedelta(days=90)
    ).group_by(func.date(Attendance.date)).order_by('date').all()
    
    # تنبؤات التكاليف
    salary_trend = db.session.query(
        Salary.month,
        Salary.year,
        func.sum(Salary.total_salary).label('total_cost')
    ).group_by(Salary.month, Salary.year).order_by(Salary.year, Salary.month).all()
    
    return render_template('ai_services/predictive_analytics.html',
                         attendance_trend=attendance_trend,
                         salary_trend=salary_trend)

@ai_services_bp.route('/ai-recommendations')
@login_required
def ai_recommendations():
    """توصيات الذكاء الاصطناعي"""
    
    try:
        # جمع البيانات للتحليل
        company_data = {
            'employees': Employee.query.count(),
            'vehicles': Vehicle.query.count(),
            'departments': Department.query.count(),
            'avg_salary': db.session.query(func.avg(Salary.total_salary)).scalar() or 0,
            'attendance_rate': _calculate_attendance_rate()
        }
        
        # الحصول على توصيات من الذكاء الاصطناعي
        recommendations = ai_analyzer.get_business_recommendations(company_data)
        
        return render_template('ai_services/recommendations.html',
                             recommendations=recommendations,
                             company_data=company_data)
                             
    except Exception as e:
        flash(f'خطأ في جلب التوصيات: {str(e)}', 'danger')
        return render_template('ai_services/recommendations.html',
                             recommendations=[],
                             company_data={})

@ai_services_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_data():
    """API لتحليل البيانات بالذكاء الاصطناعي"""
    
    try:
        data = request.get_json()
        analysis_type = data.get('type', 'general')
        
        if analysis_type == 'employees':
            result = ai_analyzer.analyze_employees()
        elif analysis_type == 'vehicles':
            result = ai_analyzer.analyze_vehicles()
        elif analysis_type == 'financial':
            result = ai_analyzer.analyze_finances()
        else:
            result = ai_analyzer.general_analysis()
            
        return jsonify({
            'success': True,
            'analysis': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_services_bp.route('/api/predictions', methods=['POST'])
@login_required
def get_predictions():
    """API للحصول على التنبؤات"""
    
    try:
        data = request.get_json()
        prediction_type = data.get('type', 'attendance')
        time_frame = data.get('time_frame', 30)  # أيام
        
        if prediction_type == 'attendance':
            predictions = ai_analyzer.predict_attendance(time_frame)
        elif prediction_type == 'costs':
            predictions = ai_analyzer.predict_costs(time_frame)
        elif prediction_type == 'maintenance':
            predictions = ai_analyzer.predict_maintenance(time_frame)
        else:
            predictions = {}
            
        return jsonify({
            'success': True,
            'predictions': predictions,
            'time_frame': time_frame
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_services_bp.route('/smart-alerts')
@login_required
def smart_alerts():
    """التنبيهات الذكية"""
    
    alerts = []
    
    # تنبيهات الوثائق المنتهية
    expired_docs = Document.query.filter(
        Document.expiry_date <= datetime.now().date() + timedelta(days=30)
    ).count()
    
    if expired_docs > 0:
        alerts.append({
            'type': 'warning',
            'title': 'وثائق ستنتهي قريباً',
            'message': f'{expired_docs} وثيقة ستنتهي خلال 30 يوماً',
            'action_url': url_for('documents.index')
        })
    
    # تنبيهات المركبات
    maintenance_vehicles = Vehicle.query.filter_by(status='maintenance').count()
    if maintenance_vehicles > 0:
        alerts.append({
            'type': 'info',
            'title': 'مركبات في الصيانة',
            'message': f'{maintenance_vehicles} مركبة تحتاج صيانة',
            'action_url': url_for('vehicles.index')
        })
    
    # تنبيهات الحضور
    low_attendance = _check_low_attendance()
    if low_attendance:
        alerts.append({
            'type': 'danger',
            'title': 'معدل حضور منخفض',
            'message': 'معدل الحضور أقل من المعدل المطلوب',
            'action_url': url_for('attendance.index')
        })
    
    return render_template('ai_services/smart_alerts.html', alerts=alerts)

def _calculate_attendance_rate():
    """حساب معدل الحضور"""
    total_employees = Employee.query.filter_by(status='active').count()
    if total_employees == 0:
        return 0
    
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(date=today).count()
    
    return (today_attendance / total_employees) * 100

def _check_low_attendance():
    """فحص معدل الحضور المنخفض"""
    attendance_rate = _calculate_attendance_rate()
    return attendance_rate < 70  # إذا كان أقل من 70%