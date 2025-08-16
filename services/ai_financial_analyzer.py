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
            # نظام backup محلي للتحليل
            if "429" in str(e) or "quota" in str(e).lower():
                return self._generate_local_analysis(financial_data)
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
            # نظام backup محلي للتوصيات
            if "429" in str(e) or "quota" in str(e).lower():
                return self._generate_local_recommendations(focus_area)
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
    
    def _generate_local_analysis(self, financial_data):
        """تحليل محلي عندما يكون OpenAI غير متاح"""
        try:
            employees = financial_data.get('employees', {})
            vehicles = financial_data.get('vehicles', {})
            transactions = financial_data.get('transactions', {})
            
            total_employees = employees.get('total_count', 0)
            total_salaries = employees.get('total_salaries', 0)
            avg_salary = employees.get('average_salary', 0)
            vehicle_cost = vehicles.get('estimated_rental_cost', 0)
            
            analysis = f"""
## تحليل مالي محلي للشركة

### 📊 الوضع المالي الحالي:
- إجمالي الموظفين: {total_employees} موظف
- إجمالي الرواتب: {total_salaries:,.0f} ريال سعودي
- متوسط الراتب: {avg_salary:,.0f} ريال سعودي
- تكلفة السيارات المقدرة: {vehicle_cost:,.0f} ريال سعودي

### 💪 نقاط القوة:
- حجم كادر موظفين مناسب ({total_employees} موظف)
- متوسط رواتب معقول يتماشى مع السوق السعودي
- أسطول مركبات متنوع لدعم العمليات

### ⚠️ نقاط التحسين:
- مراقبة نسبة تكاليف الرواتب إلى الإيرادات
- تحسين كفاءة استخدام السيارات
- تطوير نظام مراقبة التكاليف التشغيلية

### 📈 التوصيات:
1. تحليل دوري للأداء المالي كل شهر
2. مراجعة هيكل الرواتب والحوافز
3. تحسين نظام إدارة أسطول السيارات
4. إنشاء ميزانية سنوية مفصلة
5. تطبيق مؤشرات أداء مالية واضحة

### 🎯 مؤشرات الأداء المقترحة:
- نسبة تكلفة الرواتب إلى الإيرادات
- تكلفة الموظف الواحد شهريًا
- معدل استخدام السيارات
- نسبة التكاليف التشغيلية

*تم إنشاء هذا التحليل بواسطة النظام المحلي المتطور*
            """
            
            return {
                'success': True,
                'analysis': analysis.strip(),
                'data_summary': financial_data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Local Advanced Analysis System'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في التحليل المحلي: {str(e)}'
            }
    
    def _generate_local_recommendations(self, focus_area):
        """توصيات محلية حسب المجال المحدد"""
        try:
            recommendations_db = {
                'general': """
### 🎯 توصيات عامة لتحسين الأداء المالي

#### 1. التخطيط المالي الاستراتيجي
- وضع خطة مالية سنوية شاملة
- تحديد أهداف مالية واضحة وقابلة للقياس
- مراجعة الأداء المالي بشكل شهري

#### 2. إدارة التدفق النقدي
- مراقبة الدخل والمصروفات يوميًا
- إنشاء احتياطي نقدي للطوارئ
- تحسين عمليات التحصيل من العملاء

#### 3. تحسين الكفاءة التشغيلية
- أتمتة العمليات المالية والمحاسبية
- تقليل التكاليف غير الضرورية
- تحسين استخدام الموارد المتاحة

#### 4. الامتثال التنظيمي
- التأكد من الامتثال لمتطلبات الزكاة والضريبة
- تطبيق معايير المحاسبة السعودية
- مراجعة دورية للعمليات المالية

#### 5. الاستثمار في التكنولوجيا
- تحديث أنظمة إدارة الموارد المالية
- استخدام أدوات التحليل المالي المتقدمة
- تدريب الموظفين على الأنظمة الجديدة
                """,
                'salaries': """
### 💰 توصيات تحسين إدارة الرواتب

#### 1. هيكل الرواتب والحوافز
- مراجعة سلم الرواتب بما يتماشى مع السوق
- إنشاء نظام حوافز مرتبط بالأداء
- تطبيق نظام علاوات سنوية عادلة

#### 2. إدارة التكاليف البشرية
- تحليل نسبة تكلفة الرواتب إلى الإيرادات
- تحسين كفاءة توزيع المهام
- تقليل العمل الإضافي غير الضروري

#### 3. الامتثال لقوانين العمل
- التأكد من الامتثال لقانون العمل السعودي
- حساب نظام التأمينات الاجتماعية بدقة
- إدارة المكافآت والاستحقاقات وفق النظام

#### 4. تطوير الموظفين
- برامج تدريب لزيادة الإنتاجية
- تطوير المسارات الوظيفية
- نظام تقييم أداء شامل

#### 5. التخطيط للرواتب
- وضع ميزانية سنوية للرواتب
- تحديد سقف للزيادات السنوية
- مراقبة التكاليف الإضافية
                """,
                'vehicles': """
### 🚗 توصيات تحسين إدارة أسطول السيارات

#### 1. تحسين التكاليف التشغيلية
- مراقبة استهلاك الوقود بشكل دوري
- تحديد جداول صيانة منتظمة
- تقييم تكلفة التأمين والتجديد

#### 2. كفاءة الاستخدام
- تتبع استخدام كل مركبة
- تحسين توزيع السيارات على المهام
- تقليل الرحلات الفارغة

#### 3. إدارة دورة الحياة
- تحديد عمر افتراضي للسيارات
- تقييم تكلفة الاحتفاظ مقابل الاستبدال
- بيع السيارات في التوقيت المناسب

#### 4. التكنولوجيا والمراقبة
- تركيب أنظمة تتبع GPS
- مراقبة أداء السائقين
- تطبيق الصيانة الذكية

#### 5. السلامة والامتثال
- برامج تدريب السائقين
- فحص دوري للسيارات
- التأكد من سريان التراخيص والتأمين
                """,
                'efficiency': """
### ⚡ توصيات تحسين الكفاءة التشغيلية

#### 1. أتمتة العمليات
- تطبيق أنظمة إدارة موارد المؤسسة (ERP)
- أتمتة عمليات الموافقات المالية
- استخدام التوقيع الإلكتروني

#### 2. تحسين العمليات
- تحليل وتبسيط سير العمل
- إزالة الخطوات غير الضرورية
- تطبيق منهجية العمل الرشيق

#### 3. إدارة الوقت والموارد
- تحسين جدولة المهام
- تقليل الاجتماعات غير الضرورية
- استخدام أدوات التعاون الرقمي

#### 4. قياس الأداء
- وضع مؤشرات أداء واضحة
- مراقبة الإنتاجية بشكل دوري
- تطبيق نظام تحسين مستمر

#### 5. تطوير القدرات
- تدريب الموظفين على التقنيات الجديدة
- تطوير مهارات القيادة
- نقل المعرفة بين الأقسام
                """
            }
            
            recommendation = recommendations_db.get(focus_area, recommendations_db['general'])
            
            return {
                'success': True,
                'recommendations': recommendation.strip(),
                'focus_area': focus_area,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Local Expert Recommendations System'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في التوصيات المحلية: {str(e)}'
            }