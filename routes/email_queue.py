"""
مسارات إدارة قائمة الإيميلات المحفوظة محلياً
"""
from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from services.fallback_email_service import FallbackEmailService
import os

email_queue_bp = Blueprint('email_queue', __name__, url_prefix='/email-queue')


@email_queue_bp.route('/')
def email_queue_list():
    """عرض قائمة الإيميلات المحفوظة"""
    fallback_service = FallbackEmailService()
    emails = fallback_service.get_queued_emails()
    
    return render_template('email_queue/list.html', emails=emails)


@email_queue_bp.route('/details/<email_id>')
@login_required
def email_details(email_id):
    """عرض تفاصيل إيميل محدد"""
    fallback_service = FallbackEmailService()
    email_data = fallback_service.get_email_details(email_id)
    
    if not email_data:
        return jsonify({'success': False, 'message': 'الإيميل غير موجود'})
    
    return render_template('email_queue/details.html', email=email_data)


@email_queue_bp.route('/view/<email_id>')
def view_email_html(email_id):
    """عرض محتوى HTML للإيميل"""
    fallback_service = FallbackEmailService()
    html_file_path = os.path.join(fallback_service.emails_dir, f"{email_id}.html")
    
    if not os.path.exists(html_file_path):
        return "الملف غير موجود", 404
    
    return send_file(html_file_path)


@email_queue_bp.route('/delete/<email_id>', methods=['POST'])
@login_required
def delete_email(email_id):
    """حذف إيميل من القائمة"""
    fallback_service = FallbackEmailService()
    
    if fallback_service.delete_email(email_id):
        return jsonify({
            'success': True,
            'message': 'تم حذف الإيميل بنجاح'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'فشل في حذف الإيميل'
        })


@email_queue_bp.route('/download-attachment/<email_id>/<int:attachment_index>')
def download_attachment(email_id, attachment_index):
    """تحميل مرفق من إيميل محدد"""
    fallback_service = FallbackEmailService()
    email_data = fallback_service.get_email_details(email_id)
    
    if not email_data or 'attachments' not in email_data:
        return "الإيميل غير موجود", 404
    
    if attachment_index >= len(email_data['attachments']):
        return "المرفق غير موجود", 404
    
    attachment = email_data['attachments'][attachment_index]
    attachment_path = attachment.get('file_path')
    
    if not attachment_path or not os.path.exists(attachment_path):
        return "ملف المرفق غير موجود", 404
    
    return send_file(
        attachment_path,
        as_attachment=True,
        download_name=attachment.get('filename', 'attachment')
    )


@email_queue_bp.route('/api/count')
@login_required
def get_email_count():
    """الحصول على عدد الإيميلات المحفوظة"""
    fallback_service = FallbackEmailService()
    emails = fallback_service.get_queued_emails()
    
    return jsonify({
        'count': len(emails),
        'recent_count': len([e for e in emails[:5]]),  # آخر 5 إيميلات
    })