"""
إنشاء وإدارة شجرة الحسابات الرئيسية
"""
from app import db
from models_accounting import Account, AccountType


def create_default_chart_of_accounts():
    """إنشاء شجرة الحسابات الافتراضية"""
    
    # التحقق من وجود حسابات مسبقاً
    if Account.query.count() > 0:
        return False, "توجد حسابات في النظام مسبقاً"
    
    try:
        # الحسابات الرئيسية - المستوى الأول
        main_accounts = [
            # الأصول
            {'code': '1', 'name': 'الأصول', 'name_en': 'Assets', 'type': AccountType.ASSETS, 'level': 1},
            {'code': '2', 'name': 'الخصوم', 'name_en': 'Liabilities', 'type': AccountType.LIABILITIES, 'level': 1},
            {'code': '3', 'name': 'حقوق الملكية', 'name_en': 'Equity', 'type': AccountType.EQUITY, 'level': 1},
            {'code': '4', 'name': 'الإيرادات', 'name_en': 'Revenue', 'type': AccountType.REVENUE, 'level': 1},
            {'code': '5', 'name': 'المصروفات', 'name_en': 'Expenses', 'type': AccountType.EXPENSES, 'level': 1},
        ]
        
        # إنشاء الحسابات الرئيسية
        created_accounts = {}
        for acc_data in main_accounts:
            account = Account()
            account.code = acc_data['code']
            account.name = acc_data['name']
            account.name_en = acc_data['name_en']
            account.account_type = acc_data['type']
            account.level = acc_data['level']
            account.parent_id = None
            account.is_active = True
            account.balance = 0
            db.session.add(account)
            db.session.flush()  # للحصول على الـ ID
            created_accounts[acc_data['code']] = account
        
        # الحسابات الفرعية - المستوى الثاني
        sub_accounts = [
            # الأصول الفرعية
            {'code': '11', 'name': 'الأصول المتداولة', 'name_en': 'Current Assets', 'type': AccountType.ASSETS, 'parent': '1', 'level': 2},
            {'code': '12', 'name': 'الأصول الثابتة', 'name_en': 'Fixed Assets', 'type': AccountType.ASSETS, 'parent': '1', 'level': 2},
            {'code': '13', 'name': 'الأصول غير الملموسة', 'name_en': 'Intangible Assets', 'type': AccountType.ASSETS, 'parent': '1', 'level': 2},
            
            # الخصوم الفرعية
            {'code': '21', 'name': 'الخصوم المتداولة', 'name_en': 'Current Liabilities', 'type': AccountType.LIABILITIES, 'parent': '2', 'level': 2},
            {'code': '22', 'name': 'الخصوم طويلة الأجل', 'name_en': 'Long-term Liabilities', 'type': AccountType.LIABILITIES, 'parent': '2', 'level': 2},
            
            # حقوق الملكية الفرعية
            {'code': '31', 'name': 'رأس المال', 'name_en': 'Capital', 'type': AccountType.EQUITY, 'parent': '3', 'level': 2},
            {'code': '32', 'name': 'الأرباح المحتجزة', 'name_en': 'Retained Earnings', 'type': AccountType.EQUITY, 'parent': '3', 'level': 2},
            
            # الإيرادات الفرعية
            {'code': '41', 'name': 'إيرادات التشغيل', 'name_en': 'Operating Revenue', 'type': AccountType.REVENUE, 'parent': '4', 'level': 2},
            {'code': '42', 'name': 'الإيرادات الأخرى', 'name_en': 'Other Revenue', 'type': AccountType.REVENUE, 'parent': '4', 'level': 2},
            
            # المصروفات الفرعية
            {'code': '51', 'name': 'مصروفات التشغيل', 'name_en': 'Operating Expenses', 'type': AccountType.EXPENSES, 'parent': '5', 'level': 2},
            {'code': '52', 'name': 'المصروفات الإدارية', 'name_en': 'Administrative Expenses', 'type': AccountType.EXPENSES, 'parent': '5', 'level': 2},
            {'code': '53', 'name': 'المصروفات المالية', 'name_en': 'Financial Expenses', 'type': AccountType.EXPENSES, 'parent': '5', 'level': 2},
        ]
        
        # إنشاء الحسابات الفرعية
        for acc_data in sub_accounts:
            parent_account = created_accounts[acc_data['parent']]
            account = Account()
            account.code = acc_data['code']
            account.name = acc_data['name']
            account.name_en = acc_data['name_en']
            account.account_type = acc_data['type']
            account.level = acc_data['level']
            account.parent_id = parent_account.id
            account.is_active = True
            account.balance = 0
            db.session.add(account)
            db.session.flush()
            created_accounts[acc_data['code']] = account
        
        # حسابات تفصيلية - المستوى الثالث
        detailed_accounts = [
            # الأصول المتداولة التفصيلية
            {'code': '111', 'name': 'النقدية في الصندوق', 'name_en': 'Cash on Hand', 'type': AccountType.ASSETS, 'parent': '11', 'level': 3},
            {'code': '112', 'name': 'النقدية في البنوك', 'name_en': 'Cash at Banks', 'type': AccountType.ASSETS, 'parent': '11', 'level': 3},
            {'code': '113', 'name': 'حسابات العملاء', 'name_en': 'Accounts Receivable', 'type': AccountType.ASSETS, 'parent': '11', 'level': 3},
            {'code': '114', 'name': 'المخزون', 'name_en': 'Inventory', 'type': AccountType.ASSETS, 'parent': '11', 'level': 3},
            {'code': '115', 'name': 'المصروفات المدفوعة مقدماً', 'name_en': 'Prepaid Expenses', 'type': AccountType.ASSETS, 'parent': '11', 'level': 3},
            
            # الأصول الثابتة التفصيلية
            {'code': '121', 'name': 'الأراضي والمباني', 'name_en': 'Land and Buildings', 'type': AccountType.ASSETS, 'parent': '12', 'level': 3},
            {'code': '122', 'name': 'المعدات والآلات', 'name_en': 'Equipment and Machinery', 'type': AccountType.ASSETS, 'parent': '12', 'level': 3},
            {'code': '123', 'name': 'المركبات', 'name_en': 'Vehicles', 'type': AccountType.ASSETS, 'parent': '12', 'level': 3},
            {'code': '124', 'name': 'الأثاث والتجهيزات', 'name_en': 'Furniture and Fixtures', 'type': AccountType.ASSETS, 'parent': '12', 'level': 3},
            {'code': '125', 'name': 'الحاسوب والبرامج', 'name_en': 'Computer and Software', 'type': AccountType.ASSETS, 'parent': '12', 'level': 3},
            
            # الخصوم المتداولة التفصيلية
            {'code': '211', 'name': 'حسابات الموردين', 'name_en': 'Accounts Payable', 'type': AccountType.LIABILITIES, 'parent': '21', 'level': 3},
            {'code': '212', 'name': 'رواتب مستحقة الدفع', 'name_en': 'Accrued Salaries', 'type': AccountType.LIABILITIES, 'parent': '21', 'level': 3},
            {'code': '213', 'name': 'ضرائب مستحقة', 'name_en': 'Accrued Taxes', 'type': AccountType.LIABILITIES, 'parent': '21', 'level': 3},
            {'code': '214', 'name': 'مصروفات مستحقة أخرى', 'name_en': 'Other Accrued Expenses', 'type': AccountType.LIABILITIES, 'parent': '21', 'level': 3},
            
            # إيرادات التشغيل التفصيلية
            {'code': '411', 'name': 'مبيعات الخدمات', 'name_en': 'Service Revenue', 'type': AccountType.REVENUE, 'parent': '41', 'level': 3},
            {'code': '412', 'name': 'رسوم الاستشارات', 'name_en': 'Consulting Fees', 'type': AccountType.REVENUE, 'parent': '41', 'level': 3},
            {'code': '413', 'name': 'إيرادات الإدارة', 'name_en': 'Management Revenue', 'type': AccountType.REVENUE, 'parent': '41', 'level': 3},
            
            # مصروفات التشغيل التفصيلية
            {'code': '511', 'name': 'رواتب الموظفين', 'name_en': 'Employee Salaries', 'type': AccountType.EXPENSES, 'parent': '51', 'level': 3},
            {'code': '512', 'name': 'بدلات ومكافآت', 'name_en': 'Allowances and Bonuses', 'type': AccountType.EXPENSES, 'parent': '51', 'level': 3},
            {'code': '513', 'name': 'التأمينات الاجتماعية', 'name_en': 'Social Insurance', 'type': AccountType.EXPENSES, 'parent': '51', 'level': 3},
            {'code': '514', 'name': 'مصروفات المركبات', 'name_en': 'Vehicle Expenses', 'type': AccountType.EXPENSES, 'parent': '51', 'level': 3},
            {'code': '515', 'name': 'صيانة وإصلاح', 'name_en': 'Maintenance and Repairs', 'type': AccountType.EXPENSES, 'parent': '51', 'level': 3},
            
            # المصروفات الإدارية التفصيلية
            {'code': '521', 'name': 'رواتب الإدارة', 'name_en': 'Management Salaries', 'type': AccountType.EXPENSES, 'parent': '52', 'level': 3},
            {'code': '522', 'name': 'إيجارات', 'name_en': 'Rent Expenses', 'type': AccountType.EXPENSES, 'parent': '52', 'level': 3},
            {'code': '523', 'name': 'كهرباء وماء وهاتف', 'name_en': 'Utilities', 'type': AccountType.EXPENSES, 'parent': '52', 'level': 3},
            {'code': '524', 'name': 'مستلزمات مكتبية', 'name_en': 'Office Supplies', 'type': AccountType.EXPENSES, 'parent': '52', 'level': 3},
            {'code': '525', 'name': 'رسوم حكومية', 'name_en': 'Government Fees', 'type': AccountType.EXPENSES, 'parent': '52', 'level': 3},
        ]
        
        # إنشاء الحسابات التفصيلية
        for acc_data in detailed_accounts:
            parent_account = created_accounts[acc_data['parent']]
            account = Account()
            account.code = acc_data['code']
            account.name = acc_data['name']
            account.name_en = acc_data['name_en']
            account.account_type = acc_data['type']
            account.level = acc_data['level']
            account.parent_id = parent_account.id
            account.is_active = True
            account.balance = 0
            db.session.add(account)
        
        # حفظ التغييرات
        db.session.commit()
        
        return True, f"تم إنشاء {len(main_accounts) + len(sub_accounts) + len(detailed_accounts)} حساب بنجاح"
        
    except Exception as e:
        db.session.rollback()
        return False, f"خطأ في إنشاء الحسابات: {str(e)}"


def get_accounts_tree():
    """الحصول على شجرة الحسابات المنظمة"""
    try:
        # جلب جميع الحسابات مرتبة
        accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
        
        # تنظيم الحسابات في شجرة
        tree = {}
        for account in accounts:
            if account.level == 1:  # الحسابات الرئيسية
                tree[account.id] = {
                    'account': account,
                    'children': {}
                }
        
        # إضافة الحسابات الفرعية
        for account in accounts:
            if account.level == 2 and account.parent_id:
                if account.parent_id in tree:
                    tree[account.parent_id]['children'][account.id] = {
                        'account': account,
                        'children': {}
                    }
        
        # إضافة الحسابات التفصيلية
        for account in accounts:
            if account.level == 3 and account.parent_id:
                # العثور على الحساب الأب
                for main_id, main_data in tree.items():
                    if account.parent_id in main_data['children']:
                        main_data['children'][account.parent_id]['children'][account.id] = {
                            'account': account,
                            'children': {}
                        }
                        break
        
        return tree
        
    except Exception as e:
        print(f"خطأ في جلب شجرة الحسابات: {e}")
        return {}


def get_account_hierarchy(account_id):
    """الحصول على التسلسل الهرمي لحساب معين"""
    try:
        account = Account.query.get(account_id)
        if not account:
            return []
        
        hierarchy = [account]
        current = account
        
        # التنقل صعوداً في الهيكل
        while current.parent_id:
            parent = Account.query.get(current.parent_id)
            if parent:
                hierarchy.insert(0, parent)
                current = parent
            else:
                break
        
        return hierarchy
        
    except Exception as e:
        print(f"خطأ في جلب التسلسل الهرمي: {e}")
        return []


def calculate_account_balance(account_id, include_children=True):
    """حساب رصيد حساب مع أو بدون الحسابات الفرعية"""
    try:
        account = Account.query.get(account_id)
        if not account:
            return 0
        
        total_balance = account.balance
        
        if include_children:
            # جلب جميع الحسابات الفرعية
            children = Account.query.filter_by(parent_id=account_id, is_active=True).all()
            for child in children:
                total_balance += calculate_account_balance(child.id, True)
        
        return total_balance
        
    except Exception as e:
        print(f"خطأ في حساب الرصيد: {e}")
        return 0