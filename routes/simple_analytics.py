"""
نظام التحليل المالي المبسط
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import random

simple_analytics_bp = Blueprint('simple_analytics', __name__, url_prefix='/accounting/analytics')

@simple_analytics_bp.route('/')
def dashboard():
    """لوحة التحليل المالي المبسطة"""
    
    # بيانات تجريبية للعرض
    try:
        # المؤشرات المالية الأساسية
        total_revenue = 450000.0
        total_expenses = 380000.0
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # البيانات الشهرية
        revenue_data = [35000, 42000, 38000, 45000, 41000, 47000, 43000, 48000, 44000, 46000, 49000, 52000]
        expense_data = [28000, 32000, 30000, 35000, 33000, 37000, 34000, 38000, 36000, 37000, 39000, 41000]
        
        # توزيع المصروفات
        expense_distribution = [150000, 120000, 80000, 30000]  # رواتب، مركبات، تشغيل، أخرى
        
        # أداء الأقسام
        department_names = ['الإدارة', 'المبيعات', 'التسويق', 'المحاسبة', 'الصيانة']
        department_revenues = [50000, 80000, 30000, 20000, 15000]
        department_expenses = [25000, 40000, 15000, 35000, 18000]
        
        # تكاليف المركبات
        vehicle_names = ['مركبة-001', 'مركبة-002', 'مركبة-003', 'مركبة-004', 'مركبة-005']
        fuel_costs = [5000, 4500, 6000, 3800, 5200]
        maintenance_costs = [2000, 3500, 1800, 2800, 2200]
        
        # التنبؤات (متوسط متحرك بسيط)
        recent_revenue = sum(revenue_data[-3:]) / 3
        recent_expense = sum(expense_data[-3:]) / 3
        
        prediction_data = revenue_data + [recent_revenue, recent_revenue * 1.05, recent_revenue * 1.1]
        actual_data = revenue_data
        prediction_months = [f"شهر {i}" for i in range(1, len(prediction_data) + 1)]
        
        predicted_revenue = recent_revenue * 1.05
        predicted_expenses = recent_expense * 1.03
        predicted_profit = predicted_revenue - predicted_expenses
        
        # البيانات للمقارنة
        salary_expenses = 150000
        prev_salary_expenses = 145000
        salary_change = ((salary_expenses - prev_salary_expenses) / prev_salary_expenses * 100) if prev_salary_expenses > 0 else 0
        salary_percentage = (salary_expenses / total_expenses * 100) if total_expenses > 0 else 0
        
        vehicle_expenses = 120000
        prev_vehicle_expenses = 118000
        vehicle_change = ((vehicle_expenses - prev_vehicle_expenses) / prev_vehicle_expenses * 100) if prev_vehicle_expenses > 0 else 0
        vehicle_percentage = (vehicle_expenses / total_expenses * 100) if total_expenses > 0 else 0
        
        operation_expenses = 80000
        prev_operation_expenses = 82000
        operation_change = ((operation_expenses - prev_operation_expenses) / prev_operation_expenses * 100) if prev_operation_expenses > 0 else 0
        operation_percentage = (operation_expenses / total_expenses * 100) if total_expenses > 0 else 0
        
        return render_template('accounting/analytics/dashboard.html',
            # المؤشرات الرئيسية
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=net_profit,
            profit_margin=profit_margin,
            
            # البيانات الشهرية
            revenue_data=revenue_data,
            expense_data=expense_data,
            
            # توزيع المصروفات
            expense_distribution=expense_distribution,
            
            # أداء الأقسام
            department_names=department_names,
            department_revenues=department_revenues,
            department_expenses=department_expenses,
            
            # تكاليف المركبات
            vehicle_names=vehicle_names,
            fuel_costs=fuel_costs,
            maintenance_costs=maintenance_costs,
            
            # التنبؤات
            prediction_data=prediction_data,
            actual_data=actual_data,
            prediction_months=prediction_months,
            predicted_revenue=predicted_revenue,
            predicted_expenses=predicted_expenses,
            predicted_profit=predicted_profit,
            
            # التحليل التفصيلي
            salary_expenses=salary_expenses,
            prev_salary_expenses=prev_salary_expenses,
            salary_change=salary_change,
            salary_percentage=salary_percentage,
            
            vehicle_expenses=vehicle_expenses,
            prev_vehicle_expenses=prev_vehicle_expenses,
            vehicle_change=vehicle_change,
            vehicle_percentage=vehicle_percentage,
            
            operation_expenses=operation_expenses,
            prev_operation_expenses=prev_operation_expenses,
            operation_change=operation_change,
            operation_percentage=operation_percentage
        )
        
    except Exception as e:
        flash(f'خطأ في تحميل البيانات: {str(e)}', 'danger')
        return render_template('accounting/analytics/dashboard.html',
            total_revenue=0, total_expenses=0, net_profit=0, profit_margin=0,
            revenue_data=[], expense_data=[], expense_distribution=[],
            department_names=[], department_revenues=[], department_expenses=[],
            vehicle_names=[], fuel_costs=[], maintenance_costs=[],
            prediction_data=[], actual_data=[], prediction_months=[],
            predicted_revenue=0, predicted_expenses=0, predicted_profit=0,
            salary_expenses=0, prev_salary_expenses=0, salary_change=0, salary_percentage=0,
            vehicle_expenses=0, prev_vehicle_expenses=0, vehicle_change=0, vehicle_percentage=0,
            operation_expenses=0, prev_operation_expenses=0, operation_change=0, operation_percentage=0
        )