# نُظم - Arabic Employee Management System


## clone it -> make env file -> activate it ->  config the .env like the following -> run create_test_data.py -> run project 


## env file 
```
# متغيرات قاعدة البيانات
# ملاحظة: يبدو أن الاستضافة تستخدم MySQL وليس PostgreSQL
# صيغة الاتصال بـ MySQL مع ترميز الرموز الخاصة في كلمة المرور
DATABASE_URL="mysql://username:password@localhost:3306/u800258840_eissa"

# مفتاح سري للتطبيق (مطلوب لـ Flask)
SECRET_KEY=1234567890987654321

# إعدادات تويليو للإشعارات عبر الرسائل النصية 
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token  
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# إعدادات Firebase للمصادقة
FIREBASE_API_KEY=AIzaSyCUATPbRt7hMivQwtDkMNg7G1skrOVuBSA
FIREBASE_PROJECT_ID=tesstapfir-1adc0
FIREBASE_APP_ID=1:120689771242:web:d9984d7affe482717f8d93
FIREBASE_AUTH_DOMAIN=tesstapfir-1adc0.firebaseapp.com
FIREBASE_STORAGE_BUCKET=tesstapfir-1adc0.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=120689771242

# إعدادات التطبيق
FLASK_ENV=production
FLASK_DEBUG=False

# المنطقة الزمنية (مهم للتواريخ الهجرية)
TZ=Asia/Riyadh

# إعدادات إضافية للنشر على استضافة مشتركة
SERVER_NAME=eissa.site
APPLICATION_ROOT=/
PREFERRED_URL_SCHEME=https
```

## Overview

نُظم is a comprehensive Arabic employee management system with a complete RESTful API. The system provides employee lifecycle management, vehicle tracking, attendance monitoring, and detailed reporting capabilities with full Arabic language support.

## 🚀 Quick Start

### API Testing
1. Import `NUZUM_API_Collection.postman_collection.json` into Postman
2. Import `NUZUM_Environment.postman_environment.json` as environment
3. Start testing with the health check: `GET /api/v1/health`

### Login Credentials
- **Email**: admin@nuzum.sa
- **Password**: admin123

## 📊 API Endpoints

### Core Features
- **Authentication**: User login with JWT tokens
- **Employee Management**: Complete CRUD operations
- **Vehicle Management**: Vehicle tracking and handovers
- **Attendance System**: Time tracking and reporting
- **Salary Management**: Payroll processing
- **Dashboard Statistics**: Real-time analytics
- **Advanced Search**: Cross-system search capabilities

### Health Check
```
GET /api/v1/health
```

### API Information
```
GET /api/v1/info
```

## 📋 Features

### ✅ RESTful API (25+ endpoints)
- Employee management (CRUD)
- Vehicle management and tracking
- Attendance system with status tracking
- Salary management and reporting
- Department management
- Advanced search functionality
- Dashboard statistics
- Notification system

### ✅ Security Features
- JWT Authentication
- Bearer token authorization
- Input validation
- Error handling with Arabic messages

### ✅ Data Management
- Pagination support
- Advanced filtering
- Sorting capabilities
- Search functionality

## 📚 Documentation

### Available Files
- `API_DOCUMENTATION.md` - Complete API reference
- `POSTMAN_TESTING_GUIDE.md` - Step-by-step testing guide
- `API_SUMMARY.md` - Project overview and features
- `NUZUM_API_Collection.postman_collection.json` - Postman collection
- `NUZUM_Environment.postman_environment.json` - Environment variables

## 🏗️ Project Structure

```
├── routes/
│   └── restful_api.py          # All API endpoints
├── templates/                  # HTML templates
├── static/                     # Static assets
├── models.py                   # Database models
├── app.py                      # Flask application
├── main.py                     # Application entry point
└── README.md                   # This file
```

## 🔧 Technology Stack

- **Backend**: Python Flask 3.1.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login + JWT
- **API**: RESTful design with JSON responses
- **Documentation**: Comprehensive Postman collection

## 🧪 Testing

### Using Postman
1. Import the collection and environment files
2. Run "Health Check" to verify system status
3. Use "Login" to get authentication token
4. Test any endpoint with automatic token management

### Quick API Test
```bash
curl -X GET http://localhost:5000/api/v1/health
```

## 📱 Use Cases

### For Developers
- Mobile app backend
- Third-party integrations
- Automated testing
- Data synchronization

### For Businesses
- Employee management
- Vehicle fleet tracking
- Attendance monitoring
- Payroll processing

## 🔒 Security

- JWT tokens with 24-hour expiration
- Secure password hashing
- Input validation and sanitization
- Proper error handling without sensitive data exposure

## 🚀 Deployment

The system is ready for deployment on any platform supporting Python Flask applications. All dependencies are managed and the database schema is automatically created.

## 📞 Support

For technical support or questions about the API, refer to the comprehensive documentation files included in this project.

---

**نُظم** - Building the future of Arabic employee management systems 🇸🇦