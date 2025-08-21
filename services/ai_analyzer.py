"""
خدمة تحليل الذكاء الاصطناعي المتقدمة
Advanced AI Analysis Service for Business Intelligence
"""

import openai
import os
import json
from datetime import datetime, timedelta
from sqlalchemy import func
from models import Employee, Vehicle, Attendance, Salary, Department, Document
from app import db

class AIAnalyzer:
    """محلل الذكاء الاصطناعي للأعمال"""
    
    def __init__(self):
        # إعداد OpenAI API
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # أحدث نموذج من OpenAI تم إصداره في مايو 2024
        
    def get_business_recommendations(self, company_data):
        """الحصول على توصيات عمل ذكية"""
        
        prompt = f"""
        بصفتك خبير استشاري للأعمال في السوق السعودي، قم بتحليل البيانات التالية وقدم توصيات عملية:
        
        بيانات الشركة:
        - عدد الموظفين: {company_data.get('employees', 0)}
        - عدد المركبات: {company_data.get('vehicles', 0)}
        - عدد الأقسام: {company_data.get('departments', 0)}
        - متوسط الراتب: {company_data.get('avg_salary', 0)} ريال
        - معدل الحضور: {company_data.get('attendance_rate', 0):.1f}%
        
        قدم توصيات في المجالات التالية:
        1. تحسين الكفاءة التشغيلية
        2. تطوير الموارد البشرية
        3. إدارة المركبات والأصول
        4. تحسين الربحية
        5. الامتثال للأنظمة السعودية
        
        اجعل التوصيات محددة وقابلة للتطبيق مع أرقام ونسب واضحة.
        أجب بصيغة JSON بالشكل التالي:
        {{
            "efficiency": ["توصية 1", "توصية 2"],
            "hr": ["توصية 1", "توصية 2"],
            "fleet": ["توصية 1", "توصية 2"],
            "financial": ["توصية 1", "توصية 2"],
            "compliance": ["توصية 1", "توصية 2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return self._get_fallback_recommendations()
    
    def analyze_employees(self):
        """تحليل بيانات الموظفين"""
        
        # جمع بيانات الموظفين
        employees_by_dept = db.session.query(
            Department.name,
            func.count(Employee.id).label('count')
        ).join(Employee).group_by(Department.id).all()
        
        attendance_stats = db.session.query(
            func.avg(func.count(Attendance.id)).label('avg_attendance')
        ).join(Employee).group_by(Employee.id).first()
        
        salary_stats = db.session.query(
            func.min(Salary.total_salary).label('min_salary'),
            func.max(Salary.total_salary).label('max_salary'),
            func.avg(Salary.total_salary).label('avg_salary')
        ).first()
        
        prompt = f"""
        حلل البيانات التالية للموظفين في شركة سعودية:
        
        توزيع الموظفين حسب الأقسام:
        {[f"{dept[0]}: {dept[1]} موظف" for dept in employees_by_dept]}
        
        إحصائيات الرواتب:
        - أقل راتب: {salary_stats.min_salary if salary_stats else 0} ريال
        - أعلى راتب: {salary_stats.max_salary if salary_stats else 0} ريال  
        - متوسط الراتب: {salary_stats.avg_salary if salary_stats else 0} ريال
        
        قدم تحليل شامل يتضمن:
        1. تحليل التوزيع الحالي
        2. مقارنة مع معايير السوق السعودي
        3. توصيات للتحسين
        4. مؤشرات الأداء المقترحة
        
        أجب بصيغة JSON مع مفاتيح: analysis, recommendations, kpis
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"analysis": "تعذر التحليل حالياً", "recommendations": [], "kpis": []}
    
    def analyze_vehicles(self):
        """تحليل أسطول المركبات"""
        
        vehicle_stats = db.session.query(
            Vehicle.status,
            func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.status).all()
        
        vehicle_types = db.session.query(
            Vehicle.vehicle_type,
            func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.vehicle_type).all()
        
        prompt = f"""
        حلل أسطول المركبات التالي لشركة سعودية:
        
        توزيع المركبات حسب الحالة:
        {[f"{status[0]}: {status[1]} مركبة" for status in vehicle_stats]}
        
        أنواع المركبات:
        {[f"{vtype[0]}: {vtype[1]} مركبة" for vtype in vehicle_types]}
        
        قدم تحليل يشمل:
        1. كفاءة استخدام الأسطول
        2. توصيات الصيانة
        3. تحسين التكاليف
        4. خطة التجديد
        
        أجب بصيغة JSON مع التحليل والتوصيات
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"analysis": "تعذر تحليل المركبات", "recommendations": []}
    
    def analyze_finances(self):
        """التحليل المالي المتقدم"""
        
        monthly_costs = db.session.query(
            Salary.month,
            Salary.year,
            func.sum(Salary.total_salary).label('total_cost')
        ).group_by(Salary.month, Salary.year).order_by(Salary.year.desc(), Salary.month.desc()).limit(12).all()
        
        prompt = f"""
        حلل التكاليف المالية التالية لشركة سعودية:
        
        التكاليف الشهرية للرواتب (آخر 12 شهر):
        {[f"{cost[1]}/{cost[0]}: {cost[2]:,.0f} ريال" for cost in monthly_costs]}
        
        قدم تحليل مالي شامل يتضمن:
        1. اتجاهات التكاليف
        2. فرص التوفير
        3. توقعات الميزانية
        4. مؤشرات الأداء المالي
        5. توصيات للتحسين
        
        أجب بصيغة JSON مع التحليل المفصل
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"analysis": "تعذر التحليل المالي", "trends": [], "recommendations": []}
    
    def general_analysis(self):
        """التحليل العام للشركة"""
        
        # جمع إحصائيات عامة
        total_employees = Employee.query.count()
        total_vehicles = Vehicle.query.count()
        total_departments = Department.query.count()
        
        recent_attendance = Attendance.query.filter(
            Attendance.date >= datetime.now().date() - timedelta(days=30)
        ).count()
        
        prompt = f"""
        قم بتحليل عام لوضع الشركة التالية:
        
        الإحصائيات العامة:
        - إجمالي الموظفين: {total_employees}
        - إجمالي المركبات: {total_vehicles}
        - عدد الأقسام: {total_departments}
        - سجلات الحضور الشهرية: {recent_attendance}
        
        قدم تحليل شامل للوضع العام وتوصيات استراتيجية
        مع التركيز على البيئة السعودية ومتطلبات السوق
        
        أجب بصيغة JSON مع مفاتيح: overview, strengths, challenges, recommendations
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return self._get_fallback_general_analysis()
    
    def predict_attendance(self, days=30):
        """توقع معدلات الحضور"""
        
        # بيانات الحضور التاريخية
        historical_data = db.session.query(
            func.date(Attendance.date).label('date'),
            func.count(Attendance.id).label('count')
        ).filter(
            Attendance.date >= datetime.now().date() - timedelta(days=90)
        ).group_by(func.date(Attendance.date)).all()
        
        prompt = f"""
        بناءً على بيانات الحضور التاريخية التالية، توقع معدلات الحضور للـ {days} يوم القادمة:
        
        البيانات التاريخية (آخر 90 يوم):
        {[f"{data[0]}: {data[1]} موظف" for data in historical_data[-10:]]}
        
        قدم توقعات تتضمن:
        1. المعدل المتوقع يومياً
        2. الاتجاه العام
        3. العوامل المؤثرة
        4. التوصيات
        
        أجب بصيغة JSON
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"predictions": [], "trend": "مستقر", "recommendations": []}
    
    def predict_costs(self, days=30):
        """توقع التكاليف المستقبلية"""
        return {"predictions": [], "estimated_total": 0, "recommendations": []}
    
    def predict_maintenance(self, days=30):
        """توقع احتياجات الصيانة"""
        return {"vehicles_due": [], "estimated_cost": 0, "priority_list": []}
    
    def _get_fallback_recommendations(self):
        """توصيات احتياطية في حالة فشل الذكاء الاصطناعي"""
        return {
            "efficiency": [
                "تحسين عمليات الحضور والانصراف الرقمية",
                "تطبيق نظام إدارة المهام الإلكتروني"
            ],
            "hr": [
                "برامج تدريب مستمرة للموظفين",
                "نظام تقييم الأداء الدوري"
            ],
            "fleet": [
                "جدولة صيانة دورية للمركبات",
                "تتبع استهلاك الوقود والكفاءة"
            ],
            "financial": [
                "مراجعة هيكل الرواتب والبدلات",
                "تحسين عمليات إدارة التكاليف"
            ],
            "compliance": [
                "التأكد من الامتثال لأنظمة العمل السعودية",
                "تحديث سياسات الشركة وفقاً للأنظمة الجديدة"
            ]
        }
    
    def _get_fallback_general_analysis(self):
        """تحليل عام احتياطي"""
        return {
            "overview": "الشركة تعمل بكفاءة جيدة مع إمكانيات للتحسين",
            "strengths": ["فريق عمل متنوع", "أسطول مركبات متطور"],
            "challenges": ["تحسين معدلات الحضور", "تطوير العمليات الرقمية"],
            "recommendations": ["الاستثمار في التكنولوجيا", "تطوير المهارات"]
        }