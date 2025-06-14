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