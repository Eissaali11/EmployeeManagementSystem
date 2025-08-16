"""
نظام الذكاء الاصطناعي للتحليل المالي
AI Financial Analysis System
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from flask import current_app
from sqlalchemy import func

class AIFinancialAnalyzer:
    """محلل مالي ذكي باستخدام GPT-4o"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def analyze_company_finances(self, db, Employee, Salary, Vehicle, Transaction):
        """تحليل شامل للوضع المالي للشركة"""
        try:
            # جلب البيانات المالية الحقيقية
            today = datetime.now().date()
            
            # إحصائيات الرواتب
            total_salaries = db.session.query(func.sum(Salary.net_salary)).scalar() or 0
            employees_count = Employee.query.filter_by(status='active').count()
            
            # إحصائيات السيارات
            vehicles_count = Vehicle.query.count()
            vehicles_rental_cost = vehicles_count * 1500  # تقدير تكلفة الإيجار
            
            # إحصائيات المعاملات
            transactions_count = Transaction.query.count()
            total_transactions_amount = db.session.query(func.sum(Transaction.total_amount)).scalar() or 0
            
            # إعداد البيانات للذكاء الاصطناعي
            financial_data = {
                "date": today.strftime("%Y-%m-%d"),
                "employees": {
                    "total_count": employees_count,
                    "total_salaries": float(total_salaries),
                    "average_salary": float(total_salaries / employees_count) if employees_count > 0 else 0
                },
                "vehicles": {
                    "total_count": vehicles_count,
                    "estimated_rental_cost": vehicles_rental_cost
                },
                "transactions": {
                    "total_count": transactions_count,
                    "total_amount": float(total_transactions_amount)
                }
            }
            
            # إنشاء prompt للذكاء الاصطناعي
            prompt = f"""
            أنت مستشار مالي خبير متخصص في تحليل البيانات المالية للشركات السعودية.
            
            البيانات المالية للشركة:
            {json.dumps(financial_data, ensure_ascii=False, indent=2)}
            
            يرجى تقديم تحليل مالي شامل يتضمن:
            1. تحليل الوضع المالي الحالي
            2. نقاط القوة والضعف
            3. توصيات لتحسين الأداء المالي
            4. تحليل التكاليف والإيرادات
            5. مؤشرات الأداء الرئيسية
            
            اجعل التحليل باللغة العربية ومناسب للسوق السعودي.
            """
            
            # طلب التحليل من OpenAI
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مستشار مالي سعودي خبير في تحليل البيانات المالية للشركات."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis_result = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis_result,
                'data_summary': financial_data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            current_app.logger.error(f"Error in AI financial analysis: {e}")
            return {
                'success': False,
                'message': f'حدث خطأ في تحليل الذكاء الاصطناعي: {str(e)}',
                'error_details': str(e)
            }
    
    def get_smart_recommendations(self, focus_area='general'):
        """الحصول على توصيات ذكية لتحسين الأداء المالي"""
        try:
            # إعداد prompt حسب المجال المحدد
            prompts = {
                'general': 'قدم توصيات عامة لتحسين الأداء المالي للشركات السعودية',
                'salaries': 'ركز على تحسين إدارة الرواتب والتكاليف البشرية في السوق السعودي',
                'vehicles': 'قدم توصيات لتحسين إدارة أسطول المركبات وتقليل التكاليف',
                'efficiency': 'ركز على تحسين الكفاءة التشغيلية وتقليل الهدر'
            }
            
            prompt = prompts.get(focus_area, prompts['general'])
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت خبير استشاري للشركات السعودية متخصص في تحسين الأداء المالي."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}. قدم 5 توصيات عملية قابلة للتطبيق مع أمثلة محددة."
                    }
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            recommendations = response.choices[0].message.content
            
            return {
                'success': True,
                'recommendations': recommendations,
                'focus_area': focus_area,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            current_app.logger.error(f"Error in AI recommendations: {e}")
            return {
                'success': False,
                'message': f'حدث خطأ في الحصول على التوصيات: {str(e)}'
            }
    
    def analyze_expense_patterns(self, transactions_data):
        """تحليل أنماط المصروفات واكتشاف الاتجاهات"""
        try:
            prompt = f"""
            قم بتحليل أنماط المصروفات التالية للشركة:
            {json.dumps(transactions_data, ensure_ascii=False, indent=2)}
            
            حلل النقاط التالية:
            1. الاتجاهات في المصروفات
            2. النقاط المطلوب تحسينها
            3. توقعات مستقبلية
            4. مقارنة مع معايير الصناعة
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت محلل مالي متخصص في تحليل أنماط المصروفات للشركات."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            return {
                'success': True,
                'analysis': response.choices[0].message.content,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في تحليل أنماط المصروفات: {str(e)}'
            }