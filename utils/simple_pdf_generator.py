"""
مولد PDF بسيط باستخدام reportlab لتجنب مشاكل الترميز
"""

from utils.arabic_handover_pdf import create_vehicle_handover_pdf as generate_arabic_pdf

def create_vehicle_handover_pdf(handover_data):
    """
    استخدام المولد العربي لتسليم المركبات مع معالجة الأخطاء
    """
    return generate_arabic_pdf(handover_data)