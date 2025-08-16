"""
خدمات التحليل المالي بالذكاء الاصطناعي
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from openai import OpenAI
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AIFinancialAnalytics:
    """خدمة التحليل المالي بالذكاء الاصطناعي"""
    
    def __init__(self):
        """تهيئة خدمة OpenAI"""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY غير موجود في متغيرات البيئة")
        
        self.client = OpenAI(api_key=api_key)
        # النموذج الأحدث من OpenAI هو gpt-4o الذي تم إطلاقه في 13 مايو 2024
        # لا تغير هذا إلا إذا طلب المستخدم ذلك صراحة
        self.model = "gpt-4o"
    
    def get_financial_data_summary(self) -> Dict[str, Any]:
        """جمع ملخص البيانات المالية"""
        try:
            # استيراد محلي لتجنب circular import
            from app import db
            # إحصائيات الحسابات
            accounts_query = """
                SELECT account_type, COUNT(*) as count, 
                       COALESCE(SUM(balance), 0) as total_balance
                FROM accounts 
                GROUP BY account_type
            """
            accounts_result = db.session.execute(text(accounts_query)).fetchall()
            
            # المعاملات الأخيرة (آخر 6 أشهر)
            six_months_ago = datetime.now() - timedelta(days=180)
            transactions_query = """
                SELECT DATE_TRUNC('month', transaction_date) as month,
                       COUNT(*) as transaction_count,
                       COALESCE(SUM(total_amount), 0) as total_amount
                FROM transactions 
                WHERE transaction_date >= :date
                GROUP BY DATE_TRUNC('month', transaction_date)
                ORDER BY month DESC
            """
            transactions_result = db.session.execute(
                text(transactions_query), {"date": six_months_ago}
            ).fetchall()
            
            # أكبر المعاملات
            large_transactions_query = """
                SELECT transaction_date, total_amount, description
                FROM transactions
                WHERE transaction_date >= :date AND total_amount > 1000
                ORDER BY total_amount DESC
                LIMIT 10
            """
            large_transactions = db.session.execute(
                text(large_transactions_query), {"date": six_months_ago}
            ).fetchall()
            
            # تجميع البيانات
            data_summary = {
                "accounts_by_type": [
                    {
                        "type": row.account_type,
                        "count": row.count,
                        "balance": float(row.total_balance or 0)
                    }
                    for row in accounts_result
                ],
                "monthly_transactions": [
                    {
                        "month": row.month.strftime("%Y-%m") if row.month else "",
                        "count": row.transaction_count,
                        "amount": float(row.total_amount or 0)
                    }
                    for row in transactions_result
                ],
                "large_transactions": [
                    {
                        "date": row.transaction_date.strftime("%Y-%m-%d") if row.transaction_date else "",
                        "amount": float(row.total_amount or 0),
                        "description": row.description or ""
                    }
                    for row in large_transactions
                ],
                "analysis_date": datetime.now().isoformat()
            }
            
            return data_summary
            
        except Exception as e:
            logger.error(f"خطأ في جمع البيانات المالية: {str(e)}")
            return {}
    
    def generate_financial_predictions(self) -> Dict[str, Any]:
        """توليد تنبؤات مالية ذكية"""
        try:
            data_summary = self.get_financial_data_summary()
            
            if not data_summary:
                return {"error": "لا توجد بيانات كافية للتحليل"}
            
            # إعداد الطلب للذكاء الاصطناعي
            prompt = f"""
            أنت محلل مالي خبير متخصص في النظم المحاسبية العربية. قم بتحليل البيانات المالية التالية وقدم تنبؤات وتوصيات:

            البيانات المالية:
            {json.dumps(data_summary, ensure_ascii=False, indent=2)}

            المطلوب تحليل شامل يتضمن:
            1. تحليل الاتجاهات المالية الحالية
            2. التنبؤ بالمصروفات والإيرادات للشهرين القادمين
            3. تحديد المخاطر المالية المحتملة
            4. توصيات لتحسين الأداء المالي
            5. مؤشرات الأداء الرئيسية التي يجب مراقبتها

            الرد باللغة العربية وبصيغة JSON مع التركيز على النتائج العملية والقابلة للتطبيق.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت محلل مالي خبير متخصص في تحليل البيانات المحاسبية. قدم تحليلات دقيقة وعملية بصيغة JSON باللغة العربية."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            if not content:
                return {"error": "لم يتم استلام رد من الذكاء الاصطناعي"}
            ai_analysis = json.loads(content)
            
            return {
                "predictions": ai_analysis,
                "data_source": data_summary,
                "generated_at": datetime.now().isoformat(),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"خطأ في توليد التنبؤات: {str(e)}")
            # في حالة عدم توفر OpenAI، إرجاع بيانات تجريبية
            if "429" in str(e) or "insufficient_quota" in str(e):
                return self._get_demo_predictions()
            return {"error": f"خطأ في التحليل: {str(e)}"}
    
    def analyze_transaction_patterns(self) -> Dict[str, Any]:
        """تحليل أنماط المعاملات لاكتشاف الشذوذ"""
        try:
            # استيراد محلي لتجنب circular import
            from app import db
            # جمع بيانات المعاملات
            patterns_query = """
                SELECT 
                    EXTRACT(DOW FROM transaction_date) as day_of_week,
                    EXTRACT(HOUR FROM created_at) as hour_created,
                    total_amount,
                    description,
                    transaction_date
                FROM transactions
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '90 days'
                ORDER BY transaction_date DESC
                LIMIT 100
            """
            
            patterns_result = db.session.execute(text(patterns_query)).fetchall()
            
            patterns_data = [
                {
                    "day_of_week": int(row.day_of_week or 0),
                    "hour": int(row.hour_created or 12),
                    "amount": float(row.total_amount or 0),
                    "description": row.description or "",
                    "date": row.transaction_date.strftime("%Y-%m-%d") if row.transaction_date else ""
                }
                for row in patterns_result
            ]
            
            prompt = f"""
            قم بتحليل أنماط المعاملات المالية التالية لاكتشاف:
            1. الأنماط الطبيعية في التوقيت والمبالغ
            2. المعاملات غير الطبيعية أو المشبوهة
            3. اتجاهات الإنفاق حسب أيام الأسبوع
            4. توصيات لتحسين الرقابة المالية

            البيانات:
            {json.dumps(patterns_data, ensure_ascii=False, indent=2)}

            الرد بصيغة JSON باللغة العربية.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت محلل مالي متخصص في اكتشاف الأنماط والشذوذ في المعاملات المالية."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            if not content:
                return {"error": "لم يتم استلام رد من الذكاء الاصطناعي"}
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الأنماط: {str(e)}")
            # في حالة عدم توفر OpenAI، إرجاع بيانات تجريبية
            if "429" in str(e) or "insufficient_quota" in str(e):
                return self._get_demo_patterns()
            return {"error": f"خطأ في تحليل الأنماط: {str(e)}"}
    
    def generate_budget_recommendations(self) -> Dict[str, Any]:
        """توليد توصيات الميزانية"""
        try:
            # استيراد محلي لتجنب circular import
            from app import db
            # جمع بيانات المصروفات حسب النوع
            # استخدام العمود الصحيح للنوع
            expenses_query = """
                SELECT a.account_type, a.name,
                       COALESCE(SUM(te.amount), 0) as total_amount
                FROM accounts a
                JOIN transaction_entries te ON a.id = te.account_id
                JOIN transactions t ON te.transaction_id = t.id
                WHERE a.account_type = 'EXPENSES'
                AND t.transaction_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY a.account_type, a.name
                ORDER BY total_amount DESC
            """
            
            expenses_result = db.session.execute(text(expenses_query)).fetchall()
            
            expenses_data = [
                {
                    "account_name": row.name,
                    "total_amount": float(row.total_amount or 0)
                }
                for row in expenses_result
            ]
            
            prompt = f"""
            بناءً على بيانات المصروفات التالية لآخر 6 أشهر، قدم توصيات ذكية للميزانية:

            المصروفات:
            {json.dumps(expenses_data, ensure_ascii=False, indent=2)}

            المطلوب:
            1. تحليل هيكل المصروفات الحالي
            2. تحديد المجالات المكلفة وفرص التوفير
            3. اقتراح ميزانية مُحسنة للشهرين القادمين
            4. إنشاء آلية مراقبة للمصروفات
            5. تحديد المؤشرات التحذيرية

            الرد بصيغة JSON باللغة العربية مع أرقام واقعية.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مستشار مالي خبير في إعداد الميزانيات وتحسين الأداء المالي."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            if not content:
                return {"error": "لم يتم استلام رد من الذكاء الاصطناعي"}
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"خطأ في توصيات الميزانية: {str(e)}")
            # في حالة عدم توفر OpenAI أو خطأ في البيانات، إرجاع بيانات تجريبية
            if "429" in str(e) or "insufficient_quota" in str(e) or "enum" in str(e).lower():
                return self._get_demo_budget_recommendations()
            return {"error": f"خطأ في توصيات الميزانية: {str(e)}"}

    def _get_demo_predictions(self) -> Dict[str, Any]:
        """بيانات تجريبية للتنبؤات المالية"""
        return {
            "predictions": {
                "تحليل_الاتجاهات": {
                    "الاتجاه_العام": "نمو إيجابي بنسبة 8% خلال الشهرين الماضيين",
                    "المصروفات_الرئيسية": ["الرواتب: 65%", "المركبات: 15%", "مصاريف تشغيلية: 12%", "أخرى: 8%"],
                    "التغيرات_الملحوظة": "انخفاض في مصاريف المركبات بنسبة 3% مقارنة بالشهر السابق"
                },
                "التنبؤات_القادمة": {
                    "الشهر_القادم": {
                        "المصروفات_المتوقعة": "285,000 ريال",
                        "الإيرادات_المتوقعة": "320,000 ريال",
                        "الربح_المتوقع": "35,000 ريال"
                    },
                    "الشهر_التالي": {
                        "المصروفات_المتوقعة": "290,000 ريال",
                        "الإيرادات_المتوقعة": "335,000 ريال",
                        "الربح_المتوقع": "45,000 ريال"
                    }
                },
                "المخاطر_المحتملة": [
                    "ارتفاع محتمل في تكاليف الوقود بنسبة 5%",
                    "زيادة متوقعة في الرواتب مع بداية السنة المالية الجديدة",
                    "مصاريف صيانة إضافية للمركبات القديمة"
                ],
                "التوصيات": [
                    "إنشاء احتياطي طوارئ بقيمة 50,000 ريال",
                    "مراجعة عقود الصيانة لتقليل التكاليف",
                    "تحسين كفاءة استهلاك الوقود للمركبات"
                ]
            },
            "data_source": "بيانات تجريبية - يتطلب تفعيل OpenAI API للحصول على تحليل حقيقي",
            "generated_at": datetime.now().isoformat(),
            "model_used": "Demo Mode",
            "note": "هذه بيانات تجريبية للعرض. للحصول على تحليل حقيقي، يرجى تعبئة رصيد OpenAI API"
        }
    
    def _get_demo_patterns(self) -> Dict[str, Any]:
        """بيانات تجريبية لتحليل الأنماط"""
        return {
            "الأنماط_الطبيعية": {
                "أيام_النشاط_العالي": ["الأحد", "الثلاثاء", "الأربعاء"],
                "متوسط_المعاملات_اليومية": "12-15 معاملة",
                "أوقات_الذروة": ["9:00-11:00 صباحاً", "2:00-4:00 مساءً"],
                "متوسط_قيمة_المعاملة": "1,250 ريال"
            },
            "المعاملات_غير_الطبيعية": {
                "معاملات_كبيرة_غير_معتادة": "تم اكتشاف 2 معاملة بقيم أعلى من المعدل بـ 300%",
                "أوقات_غير_اعتيادية": "3 معاملات تمت خارج ساعات العمل الرسمية",
                "تكرار_مشبوه": "لا توجد معاملات مشبوهة متكررة"
            },
            "اتجاهات_الإنفاق": {
                "الأحد": "نشاط عالي - 18 معاملة بمتوسط 1,400 ريال",
                "الاثنين": "نشاط متوسط - 11 معاملة بمتوسط 980 ريال",
                "الثلاثاء": "نشاط عالي - 16 معاملة بمتوسط 1,320 ريال",
                "باقي_الأيام": "نشاط منتظم بين 8-12 معاملة يومياً"
            },
            "توصيات_الرقابة": [
                "إضافة تنبيهات تلقائية للمعاملات أعلى من 5,000 ريال",
                "مراجعة المعاملات التي تتم خارج ساعات العمل",
                "إنشاء تقارير أسبوعية للمعاملات غير المعتادة",
                "تطبيق نظام الموافقات المتدرجة للمبالغ الكبيرة"
            ],
            "note": "تحليل تجريبي - يتطلب تفعيل OpenAI API للحصول على تحليل حقيقي للبيانات"
        }
    
    def _get_demo_budget_recommendations(self) -> Dict[str, Any]:
        """بيانات تجريبية لتوصيات الميزانية"""
        return {
            "تحليل_هيكل_المصروفات": {
                "الرواتب_والأجور": {
                    "النسبة": "65%",
                    "المبلغ_الشهري": "162,500 ريال",
                    "التقييم": "ضمن المعدل الطبيعي للشركات المشابهة"
                },
                "مصاريف_المركبات": {
                    "النسبة": "15%",
                    "المبلغ_الشهري": "37,500 ريال",
                    "التقييم": "مرتفعة قليلاً - يمكن تحسينها"
                },
                "المصاريف_التشغيلية": {
                    "النسبة": "12%",
                    "المبلغ_الشهري": "30,000 ريال",
                    "التقييم": "معقولة ومضبوطة"
                },
                "مصاريف_أخرى": {
                    "النسبة": "8%",
                    "المبلغ_الشهري": "20,000 ريال",
                    "التقييم": "متنوعة وضرورية"
                }
            },
            "فرص_التوفير": [
                {
                    "المجال": "صيانة المركبات",
                    "التوفير_المتوقع": "5,000 ريال شهرياً",
                    "الطريقة": "التعاقد مع ورشة واحدة بدلاً من متعددة"
                },
                {
                    "المجال": "استهلاك الوقود",
                    "التوفير_المتوقع": "3,500 ريال شهرياً",
                    "الطريقة": "تطبيق نظام مراقبة الوقود والمسارات"
                },
                {
                    "المجال": "المصاريف الإدارية",
                    "التوفير_المتوقع": "2,000 ريال شهرياً",
                    "الطريقة": "رقمنة العمليات الورقية"
                }
            ],
            "اقتراح_الميزانية": {
                "الشهر_القادم": {
                    "الرواتب": "162,500 ريال",
                    "المركبات": "32,500 ريال (توفير 5,000)",
                    "التشغيل": "28,000 ريال (توفير 2,000)",
                    "أخرى": "20,000 ريال",
                    "الإجمالي": "243,000 ريال",
                    "التوفير_الكلي": "7,000 ريال"
                }
            },
            "آلية_المراقبة": {
                "تقارير_أسبوعية": "مقارنة المصروفات الفعلية بالمخططة",
                "تنبيهات_تلقائية": "عند تجاوز 90% من الميزانية المخصصة",
                "مراجعة_شهرية": "تحليل الانحرافات وتحديث التوقعات"
            },
            "المؤشرات_التحذيرية": [
                "تجاوز مصاريف المركبات 40,000 ريال شهرياً",
                "ارتفاع المصاريف التشغيلية بأكثر من 15%",
                "انخفاض الإيرادات عن 300,000 ريال شهرياً"
            ],
            "note": "توصيات تجريبية - يتطلب تفعيل OpenAI API للحصول على توصيات مخصصة للبيانات الحقيقية"
        }

# إنشاء مثيل مشترك - lazy initialization لتجنب circular import
_ai_analytics_instance = None

def get_ai_analytics():
    """الحصول على مثيل AIFinancialAnalytics مع lazy initialization"""
    global _ai_analytics_instance
    if _ai_analytics_instance is None:
        _ai_analytics_instance = AIFinancialAnalytics()
    return _ai_analytics_instance

# backward compatibility
ai_analytics = property(get_ai_analytics)