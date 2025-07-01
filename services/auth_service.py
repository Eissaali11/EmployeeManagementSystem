"""
خدمة المصادقة والترخيص
"""

import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from models import User, Employee
import os

class AuthService:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'default-secret-key')
    
    @classmethod
    def authenticate_user(cls, email, password):
        """مصادقة المستخدم"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return {
                    'success': False,
                    'message': 'بيانات غير صحيحة'
                }
            
            if not check_password_hash(user.password_hash, password):
                return {
                    'success': False,
                    'message': 'كلمة المرور غير صحيحة'
                }
            
            # إنشاء Token
            token = cls.generate_token(user.id, user.company_id)
            
            return {
                'success': True,
                'data': {
                    'token': token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'company_id': user.company_id
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'خطأ في المصادقة'
            }
    
    @classmethod
    def generate_employee_token(cls, employee):
        """إنشاء Token للموظف"""
        try:
            payload = {
                'employee_id': employee.id,
                'company_id': employee.company_id,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, cls.SECRET_KEY, algorithm='HS256')
            
            return {
                'token': token,
                'expires_in': 86400  # 24 hours
            }
            
        except Exception as e:
            raise Exception(f"خطأ في إنشاء Token: {str(e)}")
    
    @classmethod
    def generate_token(cls, user_id, company_id):
        """إنشاء JWT Token"""
        try:
            payload = {
                'user_id': user_id,
                'company_id': company_id,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            return jwt.encode(payload, cls.SECRET_KEY, algorithm='HS256')
            
        except Exception as e:
            raise Exception(f"خطأ في إنشاء Token: {str(e)}")
    
    @classmethod
    def refresh_token(cls, user):
        """تجديد Token"""
        return cls.generate_token(user.id, user.company_id)
    
    @classmethod
    def verify_token(cls, token):
        """التحقق من صحة Token"""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None