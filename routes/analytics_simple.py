"""
نظام تحليل مالي مبسط مع البيانات الحقيقية
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from models import UserRole, Module, Employee, Department
from models_accounting import Transaction, Account, TransactionType, AccountType
from app import db

analytics_simple_bp = Blueprint('analytics_simple', __name__, url_prefix='/accounting/analytics')

@analytics_simple_bp.route('/')
@login_required
def dashboard():
    """لوحة التحليل المالي المبسطة"""
    
    # التحقق من الصلاحيات
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        return redirect(url_for('dashboard.index'))
    
    # جلب البيانات المبسطة
    try:
        analytics_data = get_simple_analytics_data()
        return render_template('accounting/analytics_simple.html', data=analytics_data)
    except Exception as e:
        # في حالة وجود خطأ، عرض بيانات افتراضية
        analytics_data = get_fallback_data()
        return render_template('accounting/analytics_simple.html', data=analytics_data, error=str(e))

def get_simple_analytics_data():
    """جلب البيانات المبسطة للتحليل المالي"""
    
    # 1. إحصائيات أساسية
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    total_transactions = Transaction.query.count()
    
    # 2. إحصائيات المعاملات
    total_amount = db.session.query(func.sum(Transaction.total_amount)).scalar() or 0
    
    # 3. معاملات الرواتب
    salary_transactions = Transaction.query.filter_by(transaction_type=TransactionType.SALARY).all()
    total_salaries = sum([float(t.total_amount or 0) for t in salary_transactions])
    
    # 4. معاملات المركبات
    vehicle_transactions = Transaction.query.filter_by(transaction_type=TransactionType.VEHICLE_EXPENSE).all()
    total_vehicle_expenses = sum([float(t.total_amount or 0) for t in vehicle_transactions])
    
    # 5. الحسابات المحاسبية
    total_accounts = Account.query.count()
    revenue_accounts_count = Account.query.filter_by(account_type=AccountType.REVENUE).count()
    expense_accounts_count = Account.query.filter_by(account_type=AccountType.EXPENSES).count()
    
    # 6. آخر المعاملات
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    
    # 7. الإحصائيات الشهرية المبسطة
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_transactions = Transaction.query.filter(
        extract('month', Transaction.transaction_date) == current_month,
        extract('year', Transaction.transaction_date) == current_year
    ).all()
    
    monthly_total = sum([float(t.total_amount or 0) for t in monthly_transactions])
    
    return {
        'basic_stats': {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'total_transactions': total_transactions,
            'total_accounts': total_accounts
        },
        'financial_summary': {
            'total_amount': round(float(total_amount), 2),
            'total_salaries': round(total_salaries, 2),
            'total_vehicle_expenses': round(total_vehicle_expenses, 2),
            'monthly_total': round(monthly_total, 2)
        },
        'account_breakdown': {
            'revenue_accounts': revenue_accounts_count,
            'expense_accounts': expense_accounts_count,
            'total_accounts': total_accounts
        },
        'recent_activity': [
            {
                'id': t.id,
                'type': t.transaction_type.value if t.transaction_type else 'غير محدد',
                'amount': float(t.total_amount or 0),
                'date': t.transaction_date.strftime('%Y-%m-%d') if t.transaction_date else 'غير محدد',
                'description': t.description or 'بدون وصف'
            } for t in recent_transactions
        ],
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_fallback_data():
    """بيانات احتياطية في حالة فشل جلب البيانات الحقيقية"""
    return {
        'basic_stats': {
            'total_employees': 0,
            'total_departments': 0,
            'total_transactions': 0,
            'total_accounts': 0
        },
        'financial_summary': {
            'total_amount': 0.0,
            'total_salaries': 0.0,
            'total_vehicle_expenses': 0.0,
            'monthly_total': 0.0
        },
        'account_breakdown': {
            'revenue_accounts': 0,
            'expense_accounts': 0,
            'total_accounts': 0
        },
        'recent_activity': [],
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': 'لا توجد بيانات متاحة حالياً'
    }

# API للذكاء الاصطناعي
@analytics_simple_bp.route('/api/ai-predictions')
@login_required
def api_ai_predictions():
    """API للحصول على تنبؤات الذكاء الاصطناعي"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        return jsonify({'error': 'غير مسموح'}), 403
    
    try:
        from services.ai_analytics import get_ai_analytics
        ai_service = get_ai_analytics()
        predictions = ai_service.generate_financial_predictions()
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_simple_bp.route('/api/pattern-analysis')
@login_required 
def api_pattern_analysis():
    """API لتحليل أنماط المعاملات"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        return jsonify({'error': 'غير مسموح'}), 403
    
    try:
        from services.ai_analytics import get_ai_analytics
        ai_service = get_ai_analytics()
        patterns = ai_service.analyze_transaction_patterns()
        return jsonify(patterns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_simple_bp.route('/api/budget-recommendations')
@login_required
def api_budget_recommendations():
    """API لتوصيات الميزانية"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        return jsonify({'error': 'غير مسموح'}), 403
    
    try:
        from services.ai_analytics import get_ai_analytics
        ai_service = get_ai_analytics()
        recommendations = ai_service.generate_budget_recommendations()
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500