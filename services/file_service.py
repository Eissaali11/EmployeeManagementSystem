"""
خدمة إدارة الملفات والمرفقات
"""
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from pillow_heif import register_heif_opener

# تسجيل plugin الـ HEIC/HEIF للتعامل مع صور الآيفون
register_heif_opener()
from flask import current_app
from utils.audit_logger import log_activity
from flask_login import current_user

class FileService:
    """خدمة إدارة الملفات والمرفقات"""
    
    # أنواع الملفات المسموحة (مع دعم HEIC من الآيفون)
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'heif', 'webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xlsx', 'xls'}
    ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_DOCUMENT_EXTENSIONS)
    
    # أحجام الملفات القصوى (بالبايت)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def allowed_file(filename):
        """التحقق من امتداد الملف المسموح"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def is_image_file(filename):
        """التحقق من كون الملف صورة"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_IMAGE_EXTENSIONS
    
    @staticmethod
    def generate_unique_filename(filename):
        """إنشاء اسم ملف فريد"""
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_name = str(uuid.uuid4())
        return f"{unique_name}.{file_extension}"
    
    @staticmethod
    def create_upload_directory(directory_path):
        """إنشاء مجلد الرفع إذا لم يكن موجوداً"""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        return directory_path
    
    @staticmethod
    def save_uploaded_file(file, upload_folder, max_size=None):
        """حفظ الملف المرفوع"""
        if not file or file.filename == '':
            return False, "لم يتم اختيار ملف"
        
        if not FileService.allowed_file(file.filename):
            return False, "نوع الملف غير مسموح"
        
        # التحقق من حجم الملف
        if max_size and hasattr(file, 'content_length') and file.content_length > max_size:
            return False, f"حجم الملف كبير جداً. الحد الأقصى: {max_size // (1024*1024)}MB"
        
        try:
            # إنشاء مجلد الرفع
            FileService.create_upload_directory(upload_folder)
            
            # إنشاء اسم ملف فريد
            secure_name = secure_filename(file.filename)
            unique_filename = FileService.generate_unique_filename(secure_name)
            file_path = os.path.join(upload_folder, unique_filename)
            
            # حفظ الملف
            file.save(file_path)
            
            # تسجيل العملية في السجل
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='file_upload',
                entity_type='file',
                entity_id=None,
                details=f'تم رفع الملف: {secure_name} -> {unique_filename}'
            )
            
            return True, unique_filename
            
        except Exception as e:
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='file_upload_failed',
                entity_type='file',
                entity_id=None,
                details=f'فشل رفع الملف {file.filename}: {str(e)}'
            )
            return False, f"خطأ في حفظ الملف: {str(e)}"
    
    @staticmethod
    def resize_image(image_path, max_width=800, max_height=600):
        """تغيير حجم الصورة مع دعم HEIC وتحويل إلى JPEG"""
        try:
            # تحديد المسار الجديد مع امتداد .jpg
            path_without_ext = os.path.splitext(image_path)[0]
            new_image_path = f"{path_without_ext}.jpg"
            
            with Image.open(image_path) as img:
                # تحويل أي تنسيق إلى RGB
                if img.mode != 'RGB':
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                
                # حساب الحجم الجديد مع الحفاظ على النسبة
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # حفظ الصورة المحسنة كـ JPEG
                img.save(new_image_path, 'JPEG', quality=85, optimize=True)
                
                # حذف الملف الأصلي إذا كان مختلف عن الجديد
                if image_path != new_image_path:
                    try:
                        os.remove(image_path)
                    except:
                        pass  # تجاهل الخطأ في حذف الملف الأصلي
                
                return new_image_path
        except Exception as e:
            return None
    
    @staticmethod
    def delete_file(file_path):
        """حذف ملف من النظام"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                
                log_activity(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    action='file_delete',
                    entity_type='file',
                    entity_id=None,
                    details=f'تم حذف الملف: {file_path}'
                )
                
                return True
            return False
        except Exception as e:
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='file_delete_failed',
                entity_type='file',
                entity_id=None,
                details=f'فشل حذف الملف {file_path}: {str(e)}'
            )
            return False
    
    @staticmethod
    def get_file_info(file_path):
        """جلب معلومات الملف"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'exists': True
        }
    
    @staticmethod
    def save_employee_image(file, employee_id, image_type='profile'):
        """حفظ صورة الموظف (شخصية، هوية، رخصة)"""
        upload_folder = os.path.join('static', 'uploads', 'employees', str(employee_id))
        
        success, result = FileService.save_uploaded_file(
            file, 
            upload_folder, 
            max_size=FileService.MAX_IMAGE_SIZE
        )
        
        if success:
            # تحسين الصورة
            image_path = os.path.join(upload_folder, result)
            FileService.resize_image(image_path)
            
            return True, result
        
        return False, result
    
    @staticmethod
    def save_vehicle_document(file, vehicle_id):
        """حفظ وثيقة المركبة"""
        upload_folder = os.path.join('static', 'uploads', 'vehicles', str(vehicle_id))
        
        return FileService.save_uploaded_file(
            file,
            upload_folder,
            max_size=FileService.MAX_DOCUMENT_SIZE
        )
    
    @staticmethod
    def save_employee_document(file, employee_id):
        """حفظ وثيقة الموظف"""
        upload_folder = os.path.join('static', 'uploads', 'employees', str(employee_id), 'documents')
        
        return FileService.save_uploaded_file(
            file,
            upload_folder,
            max_size=FileService.MAX_DOCUMENT_SIZE
        )