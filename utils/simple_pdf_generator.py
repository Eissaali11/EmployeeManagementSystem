"""
مولد PDF بسيط باستخدام reportlab لتجنب مشاكل الترميز
"""

from utils.professional_handover_pdf import create_vehicle_handover_pdf as generate_professional_pdf

def create_vehicle_handover_pdf(handover_data):
    """
    استخدام المولد الاحترافي الجديد لتسليم المركبات
    """
    return generate_professional_pdf(handover_data)