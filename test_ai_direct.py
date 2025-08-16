#!/usr/bin/env python3
"""
اختبار مباشر لنظام الذكاء الاصطناعي
"""
import os
import sys
sys.path.append('.')

from services.ai_financial_analyzer import AIFinancialAnalyzer
from app import app, db
from models import Employee, Salary, Vehicle
from models_accounting import Transaction

def test_ai_direct():
    """اختبار مباشر للذكاء الاصطناعي"""
    
    with app.app_context():
        print("🤖 اختبار نظام الذكاء الاصطناعي مباشرة...")
        
        # تحقق من وجود مفتاح API
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("❌ مفتاح OpenAI API غير موجود")
            return
        
        print(f"✅ مفتاح API موجود: {api_key[:8]}...")
        
        try:
            # إنشاء محلل الذكاء الاصطناعي
            analyzer = AIFinancialAnalyzer()
            print("✅ تم إنشاء محلل الذكاء الاصطناعي")
            
            # اختبار التحليل المالي
            print("\n🧠 اختبار التحليل المالي الذكي...")
            result = analyzer.analyze_company_finances(db, Employee, Salary, Vehicle, Transaction)
            
            if result.get('success'):
                print("✅ نجح التحليل المالي الذكي!")
                print(f"📊 ملخص البيانات: {result.get('data_summary', {})}")
                print(f"📝 التحليل: {result.get('analysis', '')[:200]}...")
            else:
                print(f"❌ فشل التحليل: {result.get('message', 'غير محدد')}")
                
            # اختبار التوصيات الذكية
            print("\n💡 اختبار التوصيات الذكية...")
            recommendations = analyzer.get_smart_recommendations('general')
            
            if recommendations.get('success'):
                print("✅ نجحت التوصيات الذكية!")
                print(f"📝 التوصيات: {recommendations.get('recommendations', '')[:200]}...")
            else:
                print(f"❌ فشلت التوصيات: {recommendations.get('message', 'غير محدد')}")
                
        except Exception as e:
            print(f"❌ خطأ في الاختبار: {e}")
            
        print("\n✨ انتهى الاختبار المباشر!")

if __name__ == "__main__":
    test_ai_direct()