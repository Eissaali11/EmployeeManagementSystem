# test_sender.py
from whatsapp_client import WhatsAppWrapper
import os

# استبدل هذا برقم هاتفك الشخصي مع رمز الدولة (للتجربة)
# يجب أن يكون هذا الرقم قد أرسل رسالة للرقم التجريبي أو يكون مضافاً كمتلقي في لوحة التحكم
RECIPIENT_WAID = "967737972946" # <--- غيّر هذا الرقم

def test_sending():
    print("Initializing WhatsApp client...")
    whatsapp = WhatsAppWrapper()
    
    # --- اختبار إرسال رسالة قالبية ---
    # "hello_world" هو اسم القالب الافتراضي الذي توفره Meta
    print(f"Sending 'hello_world' template to {RECIPIENT_WAID}...")
    response = whatsapp.send_template_message(
        recipient_number=RECIPIENT_WAID,
        template_name="hello_world",
        language_code="en_US"
    )
    
    if response:
        print("Template message sent successfully!")
        print("Response:", response)
    else:
        print("Failed to send template message.")

if __name__ == "__main__":
    # تأكد من أنك في نفس المجلد الذي به .env و whatsapp_client.py
    if not os.getenv("WHATSAPP_ACCESS_TOKEN"):
        print("Error: Could not find environment variables. Make sure .env file is present.")
    else:
        test_sending()