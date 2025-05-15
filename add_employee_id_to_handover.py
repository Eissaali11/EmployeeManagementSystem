from app import db, app
import traceback
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, ForeignKey, text

"""
سكريبت لإضافة عمود employee_id لجدول vehicle_handover
"""

def execute_sql(sql):
    try:
        db.session.execute(sql)
        return True
    except Exception as e:
        print(f"Error executing SQL: {e}")
        traceback.print_exc()
        return False

def add_employee_id():
    """إضافة عمود employee_id لجدول vehicle_handover"""
    
    # تحقق أولاً ما إذا كان العمود موجوداً بالفعل
    check_sql = text("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='vehicle_handover' AND column_name='employee_id';
    """)
    
    result = db.session.execute(check_sql).fetchone()
    
    if result:
        print("Column employee_id already exists in vehicle_handover table.")
        return True
    
    # إضافة العمود
    add_column_sql = text("""
    ALTER TABLE vehicle_handover 
    ADD COLUMN employee_id INTEGER;
    """)
    
    if not execute_sql(add_column_sql):
        return False
    
    print("Added employee_id column to vehicle_handover table.")
    
    # إضافة مفتاح أجنبي للعمود
    add_fk_sql = text("""
    ALTER TABLE vehicle_handover 
    ADD CONSTRAINT fk_vehicle_handover_employee 
    FOREIGN KEY (employee_id) 
    REFERENCES employee (id);
    """)
    
    if not execute_sql(add_fk_sql):
        return False
    
    print("Added foreign key constraint to employee_id column.")
    
    # تحديث عمود employee_id باستخدام person_name
    print("Note: This migration doesn't update existing records. You'll need to manually set employee_id values.")
    
    db.session.commit()
    return True

if __name__ == "__main__":
    with app.app_context():
        if add_employee_id():
            print("Migration completed successfully.")
        else:
            print("Migration failed.")