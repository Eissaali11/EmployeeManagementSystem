# whatsapp_client.py

import os
import requests
import json
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class WhatsAppWrapper:
    """
    غلاف (Wrapper) منظم للتعامل مع WhatsApp Cloud API.
    """
    
    API_URL = "https://graph.facebook.com"

    def __init__(self):
        """
        عند إنشاء نسخة من الكلاس، يتم تحميل الإعدادات من متغيرات البيئة.
        """
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v19.0") # "v19.0" كقيمة افتراضية

        if not all([self.access_token, self.phone_number_id]):
            raise ValueError(
                "يرجى التأكد من تعيين WHATSAPP_ACCESS_TOKEN و WHATSAPP_PHONE_NUMBER_ID في ملف .env"
            )

        self.base_url = f"{self.API_URL}/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _send_request(self, payload):
        """
        دالة داخلية لإرسال الطلبات إلى API.
        """
        url = f"{self.base_url}/messages"
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()  # يثير استثناء إذا كان هناك خطأ في الطلب (e.g., 4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"حدث خطأ أثناء إرسال الطلب إلى واتساب: {e}")
            print(f"Response content: {e.response.text if e.response else 'No response'}")
            return None

    def send_template_message(self, recipient_number, template_name, language_code="ar", components=None):
        """
        إرسال رسالة قالبية.

        Args:
            recipient_number (str): رقم هاتف المستلم (مع رمز الدولة).
            template_name (str): اسم القالب المعتمد.
            language_code (str, optional): رمز اللغة (مثل "ar" أو "en_US"). Defaults to "ar".
            components (list, optional): قائمة بالمكونات للمتغيرات في القالب (header, body, buttons).
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
            }
        }
        if components:
            payload["template"]["components"] = components
            
        print(f"Sending template '{template_name}' to {recipient_number}...")
        return self._send_request(payload)

    def send_text_message(self, recipient_number, message_text, preview_url=False):
        """
        إرسال رسالة نصية حرة (ضمن نافذة الـ 24 ساعة).

        Args:
            recipient_number (str): رقم هاتف المستلم.
            message_text (str): نص الرسالة.
            preview_url (bool, optional): هل يتم عرض معاينة للروابط. Defaults to False.
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message_text
            }
        }
        print(f"Sending text message to {recipient_number}...")
        return self._send_request(payload)

    def send_image_message(self, recipient_number, image_url, caption=""):
        """
        إرسال رسالة صورة (باستخدام رابط URL عام).
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }
        print(f"Sending image to {recipient_number}...")
        return self._send_request(payload)

    # يمكنك إضافة المزيد من الدوال هنا (send_document, send_location, etc.)