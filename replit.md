# نُظم - Arabic Employee Management System

## Overview
نُظم is a comprehensive Arabic employee management system built with Flask, designed for companies in Saudi Arabia. Its primary purpose is to provide complete employee lifecycle management, vehicle tracking, attendance monitoring, and detailed reporting capabilities. The system supports full Arabic language from right-to-left. The business vision is to streamline HR and vehicle fleet operations, offering a localized, efficient solution with strong market potential in the Saudi Arabian business landscape.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
### Frontend Architecture
- **Framework**: Flask with Jinja2 templates.
- **Language Support**: Right-to-left (RTL) Arabic interface.
- **Styling**: Bootstrap-based responsive design. Color schemes utilize dark backgrounds (e.g., `#1e3a5c`, `#1a1a1a`) with gradients (linear-gradient) for headers and buttons. UI elements often feature transparent cards with backdrop-filter and glow effects. Icons are larger and clearer, with specific colors for different document types.
- **Forms**: Flask-WTF for secure form handling.
- **JavaScript**: Vanilla JS with Firebase integration for authentication. Includes advanced features like drag-and-drop for file uploads, Canvas API for image compression, and Web Share API for content sharing.

### Backend Architecture
- **Framework**: Flask 3.1.0 with a modular blueprint structure.
- **Architecture Pattern**: Modular Monolith with separated concerns, supporting a multi-tenant architecture. This enables data isolation for multiple companies and a three-tier user hierarchy (System Owner → Company Admin → Employee).
- **Database ORM**: SQLAlchemy 2.0+ with Flask-SQLAlchemy.
- **Authentication**: Flask-Login with Firebase integration and JWT tokens.
- **Session Management**: Flask sessions with CSRF protection.

### Database Architecture
- **Primary**: MySQL (production) with PyMySQL driver.
- **Development**: SQLite for local development.
- **ORM**: SQLAlchemy with declarative base models.
- **Migrations**: Manual schema management.

### Key Features & Design Decisions
- **Employee Management**: Comprehensive CRUD operations, department assignments, document management with expiry tracking, profile image/ID uploads, and bulk import/export from Excel with intelligent field mapping.
- **Vehicle Management**: Registration, tracking, handover/return documentation, workshop maintenance records, and detailed reports. Includes management of vehicle documents (registration, plates, insurance) with secure file uploads, image previews, and sharing capabilities. Integrates with Google Drive for file management. Supports external safety checks with photo uploads and admin review workflow. Automated vehicle return system.
- **Attendance System**: Daily tracking, overtime calculation, monthly/weekly reports, Hijri calendar integration.
- **Salary Management**: Calculation, processing, allowances/deductions, monthly payroll reports. Features smart saving for individual and bulk salary entries, leaving empty fields as NULL.
- **Department Management**: Organizational structure and hierarchy.
- **User Management**: Role-based access control, permission management, and multi-tenant user authentication/authorization.
- **Report Generation**: Supports PDF and Excel generation with full Arabic text support (reshaping, bidirectional processing). Professional report designs with company branding and detailed data.
- **File Management**: Secure validation, virus scanning, image processing (compression, thumbnails), and organized physical file storage.
- **Mobile Device Management**: Full CRUD operations for mobile devices, IMEI tracking, optional phone number support, department/brand/status filtering, Excel import/export, employee assignment with advanced search.
- **API**: Comprehensive RESTful API with 25+ endpoints covering all system features, including JWT authentication, advanced search, filtering, and pagination.

## External Dependencies
- **Web Framework**: Flask 3.1.0
- **Database ORM**: SQLAlchemy 2.0.40
- **MySQL Driver**: PyMySQL 1.1.1
- **User Management**: Flask-Login 0.6.3
- **Form Handling**: Flask-WTF 1.2.2
- **Arabic Text Processing**: arabic-reshaper 3.0.0, python-bidi 0.6.6
- **Hijri Calendar**: hijri-converter 2.3.1
- **PDF Generation**: reportlab 4.3.1, weasyprint 65.1, fpdf 1.7.2
- **Data Manipulation**: pandas 2.2.3
- **Excel Handling**: openpyxl 3.1.5
- **Image Processing**: Pillow 11.2.1
- **SMS Notifications**: twilio 9.5.2
- **Email Services**: sendgrid 6.11.0
- **Authentication/Storage**: Firebase SDK
- **Charting**: Chart.js (for report visualizations)
- **Mapping**: Fabric.js (for damage diagrams)