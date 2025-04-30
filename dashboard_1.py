@attendance_bp.route("/dashboard")
def dashboard():
    """لوحة معلومات الحضور مع إحصائيات يومية وأسبوعية وشهرية"""
    # 1. الحصول على المشروع المحدد (إذا وجد)
    project_name = request.args.get("project", None)
    
    # 2. الحصول على التاريخ الحالي
    today = datetime.now().date()
    current_month = today.month
    current_year = today.year
    
    # 3. حساب تاريخ بداية ونهاية الأسبوع الحالي بناءً على تاريخ بداية الشهر
    start_of_month = today.replace(day=1)  # أول يوم في الشهر الحالي
    
    # نحسب عدد الأيام منذ بداية الشهر حتى اليوم الحالي
    days_since_month_start = (today - start_of_month).days
    
    # نحسب عدد الأسابيع الكاملة منذ بداية الشهر (كل أسبوع 7 أيام)
    weeks_since_month_start = days_since_month_start // 7
    
    # نحسب بداية الأسبوع الحالي (بناءً على أسابيع من بداية الشهر)
    start_of_week = start_of_month + timedelta(days=weeks_since_month_start * 7)
    
    # نهاية الأسبوع بعد 6 أيام من البداية
    end_of_week = start_of_week + timedelta(days=6)
    
    # إذا كانت نهاية الأسبوع بعد نهاية الشهر، نجعلها آخر يوم في الشهر
    last_day = calendar.monthrange(current_year, current_month)[1]
    end_of_month = today.replace(day=last_day)
    if end_of_week > end_of_month:
        end_of_week = end_of_month
    
    # 4. حساب تاريخ بداية ونهاية الشهر الحالي
    start_of_month = today.replace(day=1)
    last_day = calendar.monthrange(current_year, current_month)[1]
    end_of_month = today.replace(day=last_day)
