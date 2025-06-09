"""
مولد PDF بسيط باستخدام reportlab لتجنب مشاكل الترميز
"""

from utils.enhanced_arabic_handover_pdf import create_vehicle_handover_pdf as generate_enhanced_pdf

def create_vehicle_handover_pdf(handover_data):
    """
    استخدام المولد المحسن مع ترجمة آمنة للنصوص العربية
    """
    return generate_enhanced_pdf(handover_data)