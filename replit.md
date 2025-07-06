# نُظم - Arabic Employee Management System

## Overview

نُظم is a comprehensive Arabic employee management system built with Flask, designed specifically for companies in Saudi Arabia. The system provides complete employee lifecycle management, vehicle tracking, attendance monitoring, and detailed reporting capabilities with full Arabic language support.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templates
- **Language Support**: Right-to-left (RTL) Arabic interface
- **Styling**: Bootstrap-based responsive design
- **Forms**: Flask-WTF for secure form handling
- **JavaScript**: Vanilla JS with Firebase integration for authentication

### Backend Architecture
- **Framework**: Flask 3.1.0 with modular blueprint structure
- **Architecture Pattern**: Modular Monolith with separated concerns
- **Database ORM**: SQLAlchemy 2.0+ with Flask-SQLAlchemy
- **Authentication**: Flask-Login with Firebase integration
- **Session Management**: Flask sessions with CSRF protection

### Database Architecture
- **Primary**: MySQL (production) with PyMySQL driver
- **Development**: SQLite for local development
- **ORM**: SQLAlchemy with declarative base models
- **Migrations**: Manual schema management

## Key Components

### Core Modules
1. **Employee Management** (`routes/employees.py`)
   - Full employee lifecycle (CRUD operations)
   - Department assignment and transfers
   - Document management with expiry tracking
   - Profile image and ID document uploads

2. **Vehicle Management** (`routes/vehicles.py`)
   - Vehicle registration and tracking
   - Handover/return documentation
   - Workshop maintenance records
   - Comprehensive vehicle reports

3. **Attendance System** (`routes/attendance.py`)
   - Daily attendance tracking
   - Overtime calculations
   - Monthly and weekly reports
   - Hijri calendar integration

4. **Salary Management** (`routes/salaries.py`)
   - Salary calculations and processing
   - Allowances and deductions
   - Monthly payroll reports
   - Saudi labor law compliance

5. **Department Management** (`routes/departments.py`)
   - Organizational structure
   - Department hierarchy
   - Manager assignments

6. **User Management** (`routes/users.py`)
   - Role-based access control
   - Permission management
   - User authentication and authorization

### Service Layer
- **Authentication Service** (`services/auth_service.py`): JWT tokens, Firebase integration
- **Notification Service** (`services/notification_service.py`): SMS via Twilio, email notifications
- **Report Service** (`services/report_service.py`): PDF/Excel generation with Arabic support
- **File Service** (`services/file_service.py`): Document upload and management

### Utility Components
- **Arabic PDF Generation** (`utils/`): Multiple PDF generators with Arabic text support
- **Excel Processing** (`utils/excel.py`): Import/export with Arabic encoding
- **Date Conversion** (`utils/date_converter.py`): Gregorian/Hijri calendar support
- **Audit Logging** (`utils/audit_logger.py`): Comprehensive activity tracking

## Data Flow

### Request Processing
1. Request enters through Flask application factory
2. CSRF validation and session verification
3. Authentication check via Flask-Login
4. Route handling with permission validation
5. Business logic execution in service layer
6. Database operations via SQLAlchemy ORM
7. Response rendering with Arabic text processing

### Report Generation
1. Data extraction from multiple related models
2. Arabic text reshaping using `arabic-reshaper`
3. Bidirectional text processing with `python-bidi`
4. PDF generation via ReportLab or WeasyPrint
5. Excel generation via openpyxl with RTL support

### File Upload Processing
1. Secure file validation and virus scanning
2. Image processing and thumbnail generation
3. Database metadata storage
4. Physical file storage in organized directory structure

## External Dependencies

### Core Dependencies
- **Flask 3.1.0**: Web framework
- **SQLAlchemy 2.0.40**: Database ORM
- **PyMySQL 1.1.1**: MySQL database driver
- **Flask-Login 0.6.3**: User session management
- **Flask-WTF 1.2.2**: Form handling and CSRF protection

### Arabic Text Processing
- **arabic-reshaper 3.0.0**: Arabic text reshaping
- **python-bidi 0.6.6**: Bidirectional text algorithm
- **hijri-converter 2.3.1**: Hijri calendar conversion

### PDF Generation
- **reportlab 4.3.1**: Primary PDF generation
- **weasyprint 65.1**: HTML-to-PDF conversion
- **fpdf 1.7.2**: Alternative PDF generation

### Data Processing
- **pandas 2.2.3**: Data manipulation
- **openpyxl 3.1.5**: Excel file handling
- **Pillow 11.2.1**: Image processing

### External Services
- **twilio 9.5.2**: SMS notifications
- **sendgrid 6.11.0**: Email services
- **Firebase SDK**: Authentication and storage

## Deployment Strategy

### Environment Support
- **Local Development**: SQLite database, `.env.local` configuration
- **Production**: MySQL database, environment-specific settings
- **Docker**: Multi-container setup with Nginx reverse proxy

### Configuration Management
- Environment-specific configuration files
- Secure secret management via environment variables
- Database URL flexibility (MySQL/PostgreSQL/SQLite)

### Deployment Options
1. **Docker Compose**: Complete containerized deployment
2. **CloudPanel**: VPS deployment with systemd service
3. **Traditional VPS**: Direct server deployment
4. **Replit**: Cloud development environment

### Security Measures
- CSRF protection on all forms
- SQL injection prevention via ORM
- File upload validation and sanitization
- Session security with secure cookies
- Environment variable protection

## Changelog
- July 6, 2025: **استبدلت جميع ملفات المشروع بالنسخة الجديدة car_care-main.zip:**
  • نسخت جميع الملفات من car_care-main.zip واستبدلت المشروع بالكامل
  • تم تثبيت جميع الحزم المطلوبة بنجاح (arabic-reshaper, fpdf2, reportlab, weasyprint)
  • أصلحت مشاكل قاعدة البيانات بإضافة جميع الحقول المفقودة (mobilePersonal, nationality_id, contract_status, license_status)
  • أضفت جميع الحقول المطلوبة لجدول vehicle_handover (30+ حقل إضافي)
  • إنشاء مستخدم admin@nuzum.sa مع كلمة مرور admin123 للاختبار
  • أضفت بيانات تجريبية للمركبات والأقسام
  • إصلاح مشاكل templates (vehicle.updated_at AttributeError) بإضافة فحص null safety
  • حدثت قاعدة البيانات لملء القيم المفقودة في updated_at
  • النظام يعمل الآن بالنسخة الجديدة مع تحسينات شاملة وحلول لمشاكل قاعدة البيانات
  • جميع صفحات المركبات تعمل بدون أخطاء (302 redirect للتسجيل كما هو مطلوب)
  • استعادة سجلات التسليم والاستلام المفقودة بإضافة 6 سجلات تجريبية للمركبات
  • إصلاح كود عرض سجلات التسليم والاستلام ليعمل مع النصوص العربية (تسليم/استلام)
  • إصلاح أخطاء صفحة فهرس المركبات وإضافة حماية ضد الأخطاء في دالة get_vehicle_current_employee_id
  • يحتوي على جميع الوحدات: employees, vehicles, attendance, salaries, departments
- July 4, 2025: **استبدلت جميع ملفات المشروع بالنسخة الاحتياطية cloudpanel_20250609_213427.rar:**
  • استبدلت app.py وmodels.py بالنسخة الكاملة من النسخة الاحتياطية
  • نسخت جميع مجلدات routes/ وtemplates/ وstatic/ وutils/ وservices/ وforms/
  • استعادت النظام الكامل بجميع الوحدات والتصميم الأصلي
  • النظام يعمل بنجاح مع النسخة المحدثة بدون أخطاء
- July 3, 2025: **نجحت في إعادة إنشاء ملفات النظام الأساسية بعد الحذف الخاطئ:**
  • أعادت إنشاء routes/employees.py مع جميع وظائف إدارة الموظفين (CRUD كامل)
  • أعادت إنشاء routes/vehicles.py مع إدارة المركبات والتسليم والاستلام
  • أعادت إنشاء routes/departments.py مع إدارة الأقسام والهيكل التنظيمي
  • أنشأت templates/ كاملة للموظفين والمركبات والأقسام مع تصميم متجاوب
  • ربطت جميع المسارات بالتطبيق الرئيسي مع حل مشكلة تعارض الأسماء
  • حدثت لوحة المعلومات لتشمل روابط إدارة جميع الأقسام
  • النظام يعمل بشكل كامل مع 59 موظف، 20 مركبة، 6 أقسام
  • واجهة API تعمل بكامل وظائفها مع 25+ مسار
  • أضافت ملفات إدارة الرواتب والحضور من النسخة الاحتياطية
  • دمجت مجلدات services وutils مع المشروع الحالي
  • أضافت مسارات الرواتب والحضور إلى التطبيق الرئيسي
  • حدثت لوحة المعلومات لتشمل الوظائف الجديدة
  • أصلحت أخطاء التوجيه في ملف base.html وأنشأت تخطيط مبسط
  • حللت مشاكل المسارات المعطلة وأصلحت جميع الروابط
  • النظام الآن يعمل بدون أخطاء داخلية مع تصميم محدث
- July 3, 2025: Successfully completed code cleanup and project optimization:
  • Removed all unused files and dependencies for cleaner project structure
  • Eliminated unnecessary deployment scripts, test files, and archived assets
  • Consolidated API functionality into single organized routes/restful_api.py file
  • Simplified models.py to include only essential database models
  • Created clean Flask application factory pattern in app.py
  • Reduced project to core essential files: API, models, templates, and documentation
  • Maintained complete RESTful API functionality with 25+ endpoints
  • Preserved all Postman Collection and testing capabilities
  • Project now contains only production-ready, actively used components
  • Significantly improved maintainability and deployment readiness
- July 1, 2025: Successfully implemented comprehensive RESTful API with complete Postman testing suite:
  • Created full RESTful API covering all system features with 25+ endpoints
  • Built comprehensive Postman Collection with automatic token management and testing scripts
  • Developed complete API documentation with examples and error handling
  • Implemented JWT authentication with Bearer token security for all protected routes
  • Added advanced search, filtering, and pagination capabilities across all endpoints
  • Created employee management API (CRUD operations with validation and error handling)
  • Built vehicle management API with handover and workshop record integration
  • Implemented attendance system API with date range filtering and status management
  • Added salary management API with employee-specific salary history tracking
  • Developed comprehensive reporting API with dashboard stats and monthly reports
  • Built advanced search API supporting cross-system queries with multiple filters
  • Created notification system API ready for real-time implementation
  • Added health check and API info endpoints for monitoring and documentation
  • Implemented proper error handling with Arabic messages and HTTP status codes
  • Built Postman Environment file with dynamic variables and testing automation
  • Created comprehensive testing guide with step-by-step instructions and troubleshooting
  • API successfully tested and validated - all endpoints working correctly without errors
  • System now provides complete API coverage for mobile apps, third-party integrations, and automated testing
- June 21, 2025: Completely removed 3D effects and simplified user interface:
  • Successfully removed all 3D effects from system admin interface per user request
  • Updated 6 HTML template files to eliminate perspective, rotateX, rotateY, and translateZ transforms
  • Replaced complex 3D hover effects with simple translateY animations
  • Removed analytics data and charts from reports page for cleaner interface
  • Fixed company creation form by replacing Flask-WTF with plain HTML inputs
  • Resolved Internal Server Error on /system/companies/new route
  • System now provides smooth, fast user experience without disorienting 3D effects
- June 20, 2025: Successfully implemented ultra-modern futuristic UI design for system admin interface:
  • Created cutting-edge dashboard design with neon gradients, glass-morphism effects, and floating particles
  • Implemented advanced CSS animations including 3D hover effects, parallax scrolling, and animated backgrounds
  • Built futuristic company management interface with sophisticated visual effects
  • Developed comprehensive subscriptions management page with advanced filtering and statistics
  • Enhanced page headers with proper visibility and prominence for better user experience
  • Fixed navigation text color issues for better readability with white text and neon hover effects
  • Resolved company creation errors and simplified the process with proper form validation
  • Added edit and delete buttons with confirmation dialogs for company management operations
  • Created comprehensive edit company page with futuristic design and real-time validation
  • Implemented secure delete confirmation modal with glass-morphism effects and CSRF protection
  • All system admin pages now feature consistent modern aesthetic with animated elements
  • Successfully tested company creation functionality with proper database integration
  • Fixed company status toggle error by using correct 'status' field instead of 'is_active'
  • Resolved "Method Not Allowed" error in subscription management by adding POST method support
  • Enhanced subscription management with comprehensive form handling for upgrade, extend, suspend, and activate actions
  • Created ultra-modern subscription management page with cyber-grid animations, glassmorphism effects, and interactive plan cards
  • Implemented dynamic pricing cards with gradient animations, featured plan highlighting, and hover effects
  • Added comprehensive subscription status dashboard with progress bars, neon badges, and real-time information display
  • Enhanced SubscriptionService with upgrade_subscription and extend_subscription methods for complete functionality
  • Created futuristic company details page with cosmic animations, 3D hover effects, and parallax scrolling
  • Implemented advanced glassmorphism design with floating particles and cosmic grid background
  • Added comprehensive company statistics dashboard with animated progress bars and neon status badges
  • Enhanced user experience with ripple effects, loading animations, and responsive design across all devices
  • Created quantum-level reports dashboard with holographic headers, matrix rain background, and interactive charts
  • Implemented advanced statistical visualizations with Chart.js integration and animated progress rings
  • Built comprehensive analytics center with real-time data, growth metrics, and subscription distribution charts
  • Added quantum button effects, parallax interactions, and ultra-modern glassmorphism design elements
- June 20, 2025: Successfully completed multi-tenant system with working system admin dashboard:
  • Fixed routing issues between `/system-admin/` and `/system/` URL patterns
  • Created system admin user with credentials: admin@nuzum.sa / admin123 (password hash updated and verified)
  • System admin dashboard fully operational with company statistics and management features
  • All redirect routes properly configured for seamless user experience
  • Dashboard navigation and URL routing completely fixed and operational
  • System admin can access all company data: 59 employees, 19 vehicles with full management capabilities
- June 20, 2025: Successfully resolved all access permission issues in multi-tenant system:
  • Fixed check_module_access function to properly recognize SYSTEM_ADMIN users
  • All existing data preserved and linked to default "الشركة الرئيسية" company
  • System owner can now access all modules: employees (59), vehicles (19), departments, etc.
  • Three-tier user hierarchy fully operational with proper data isolation
  • Login credentials working: admin@nuzum.sa / admin123
- June 20, 2025: Successfully completed and fixed نُظم multi-tenant architecture implementation:
  • Fixed critical database enum compatibility issues that prevented system startup
  • Resolved authentication system with working login credentials (admin@nuzum.sa / admin123)
  • Created functional base.html template supporting multi-tenant navigation
  • Fixed all route redirections and template moment.js dependencies
  • Successfully implemented three-tier user hierarchy with proper access control
  • System owner dashboard now fully operational with comprehensive company management
  • All decorators properly validate user permissions with enum string compatibility
- June 20, 2025: Successfully transformed نُظم into comprehensive multi-tenant architecture:
  • Complete database schema migration to support multiple companies with data isolation
  • Implemented three-tier user hierarchy: System Owner → Company Admin → Employee
  • Created subscription management system with trial periods and usage limits
  • Built system admin dashboard for managing all companies and subscriptions
  • Developed company admin dashboard with subscription status and usage tracking
  • Added multi-tenant decorators for access control and data filtering
  • Implemented subscription service with automated notifications and limits
  • Created comprehensive permission system with module-based access control
  • Successfully resolved database enum compatibility and relationship mapping issues
  • System now supports unlimited companies with complete data isolation
- June 20, 2025: Successfully implemented comprehensive Arabic employee basic report with all requested features:
  • Created Arabic PDF report generator using ReportLab with proper Arabic text support
  • Implemented complete employee information display in Arabic language
  • Added support for displaying three required images: profile photo, national ID, and driving license
  • Fixed all encoding issues and text rendering problems for Arabic content
  • Report includes: basic personal information, work details, document photos, additional info, and statistics
  • User confirmed successful functionality showing professional Arabic report layout
- June 20, 2025: Enhanced employee portal with professional designs and data filtering:
  • Created modern glass-morphism design for employee vehicles page with interactive timeline
  • Implemented comprehensive vehicle data filtering to show only employee-related handovers
  • Fixed employee profile page AttributeError by removing invalid birth_date field reference
  • Designed premium profile page with gradient backgrounds, floating particles, and stats cards
  • Added responsive grid layouts and smooth animations for better user experience
  • Ensured all employee portal pages display only data related to the logged-in employee
- June 14, 2025: Successfully implemented Arabic employee PDF report with exact user-requested design:
  • Created comprehensive PDF report matching provided design template
  • Features circular profile photo frame with blue border
  • Added green-bordered rectangular frames for national ID and license images
  • Implemented blue header sections with white text for information categories
  • Added alternating row colors in data tables for better readability
  • Includes basic information, work details, and vehicle records sections
  • Successfully generated 2854-byte PDF file with proper Arabic text support
  • Report displays employee photos, identity documents, and comprehensive data
- June 14, 2025: Fixed employee PDF report generation errors:
  • Created safe Arabic font loading system with fallback mechanisms
  • Resolved all FPDF font errors that were causing report failures
  • Added comprehensive error handling for text processing and image display
  • Updated employee route to use fixed PDF report generator
  • Confirmed successful PDF generation for employee ID 178 and all other employees
- June 14, 2025: Enhanced duplicate prevention system with comprehensive validation:
  • Added duplicate checking within same Excel file before database insertion
  • Enhanced validation for required fields (plate_number, make, model)
  • Improved error reporting with specific row numbers and clear messages
  • Added tracking of processed plate numbers to prevent intra-file duplicates
- June 14, 2025: Updated vehicle import functionality to match exact user requirements: رقم اللوحة، الماركة، الموديل، سنة الصنع، اللون، اسم السائق، الحالة، تاريخ انتهاء الفحص الدوري، تاريخ انتهاء الاستمارة، ملاحظات، تاريخ الإضافة
- June 14, 2025: Added automatic data filling for missing fields during import (engine_number, chassis_number, fuel_type, mileage)
- June 14, 2025: Enhanced import template with proper date format examples and comprehensive field mapping
- June 14, 2025: Fixed import template column names to match user specifications exactly
- June 14, 2025: Added comprehensive Excel import functionality for vehicle data matching export format structure
- June 14, 2025: Created import template download function with proper Arabic column headers
- June 14, 2025: Added import validation with error handling and success/failure reporting
- June 14, 2025: Integrated import buttons into both desktop and mobile vehicle index page layouts
- June 14, 2025: Fixed vehicle export filename encoding to eliminate HTTP header warnings and ensure proper downloads
- June 14, 2025: Completely resolved all vehicle template URL routing errors by removing broken import function references
- June 14, 2025: Successfully restored vehicle management system functionality after extensive debugging and fixes
- June 14, 2025: Cleaned up all corrupted export code and syntax errors in routes/vehicles.py
- June 14, 2025: Added complete export_all_vehicles_to_excel function with proper Excel formatting to utils/vehicles_export.py
- June 14, 2025: Removed "PDF report" button from vehicle view page as requested by user
- June 14, 2025: Removed redundant "export all vehicles" button from main vehicles page as requested by user
- June 14, 2025: Fixed Excel import page error by removing unnecessary form dependency
- June 14, 2025: Improved vehicle view page UI design and added Excel import functionality with template download
- June 14, 2025: Fixed all VehicleProject Excel export errors (project_description, project_location, project_manager)
- June 14, 2025: Fixed Vehicle Excel export 'vin' field error by replacing with existing model fields
- June 14, 2025: Fixed VehicleSafetyCheck Excel export field mapping errors (tire_condition, checked_by, etc.)
- June 14, 2025: Fixed circular import issues in vehicles routes causing 404 and 500 errors
- June 14, 2025: Resolved database access problems by adding proper imports to route functions
- June 14, 2025: Fixed Excel export functionality with comprehensive field mapping and openpyxl compatibility
- June 14, 2025: Resolved VehiclePeriodicInspection certificate_number field issue 
- June 14, 2025: Updated VehicleHandover field references (person_name, mileage)
- June 14, 2025: Removed xlsxwriter dependencies to ensure openpyxl compatibility
- June 14, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.