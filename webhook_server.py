# webhook_server.py

from flask import Flask, request, jsonify
import json
import os

 
from whatsapp_client import WhatsAppWrapper


# استيراد الكلاس الذي أنشأناه
# from whatsapp_client import WhatsAppWrapper

# إنشاء كائن من تطبيق فلاسك
app = Flask(__name__)

# إنشاء نسخة من غلاف واتساب للرد على الرسائل
whatsapp = WhatsAppWrapper()

# قم بإنشاء توكن تحقق سري خاص بك. يمكن أن يكون أي نص تريده.
# سنحتاجه في المرحلة الثالثة. من الأفضل وضعه في .env أيضاً.
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN") 

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    هذا الـ endpoint مخصص للتحقق الأولي من Meta.
    عندما تقوم بإضافة الـ URL في لوحة التحكم، سترسل Meta طلب GET للتحقق.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # التحقق من أن الطلب يحتوي على الـ mode و الـ token الصحيحين
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge, 200
    else:
        # إذا لم يكن الطلب صحيحاً، نرفضه
        print("WEBHOOK_VERIFICATION_FAILED")
        return "Verification token is invalid", 403

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    هذا الـ endpoint هو الذي يستقبل الرسائل الفعلية من واتساب.
    """
    data = request.get_json()
    
    # نستخدم print لطباعة البيانات الواردة للمساعدة في التصحيح
    print("Received Webhook Payload:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # معالجة الرسائل الواردة فقط
    try:
        # Meta API يرسل البيانات داخل بنية معقدة قليلاً
        # هذا الكود يستخرج الرسالة بشكل آمن
        if data and data.get("object") == "whatsapp_business_account":
            changes = data["entry"][0]["changes"][0]
            if changes["field"] == "messages":
                message_data = changes["value"]["messages"][0]
                sender_number = message_data["from"]
                
                # التحقق من نوع الرسالة (نص، صورة، تفاعل..)
                if message_data["type"] == "text":
                    message_body = message_data["text"]["body"]
                    print(f"Message from {sender_number}: '{message_body}'")

                    # --- منطق الرد التلقائي يبدأ هنا ---
                    reply_message = f"شكراً لتلقي رسالتك '{message_body}'. سيتم الرد عليك قريباً."
                    whatsapp.send_text_message(sender_number, reply_message)
                    # ------------------------------------
                else:
                    print(f"Received a non-text message from {sender_number}")
                    # يمكنك إضافة منطق للرد على أنواع أخرى من الرسائل هنا

    except (IndexError, KeyError) as e:
        # نتجاهل التحديثات الأخرى التي لا تهمنا (مثل تحديثات حالة الرسالة "تم التسليم")
        print(f"Ignored a non-message webhook update: {e}")
        pass
    
    # يجب أن نرجع دائماً 200 OK لواتساب لإخباره أننا استلمنا التحديث بنجاح
    return "OK", 200

if __name__ == "__main__":
    # شغل السيرفر على البورت 5000 واجعل الـ debug فعالاً أثناء التطوير
    app.run(port=8031, debug=True)