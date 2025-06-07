#!/usr/bin/env python3
"""
نص اختبار تكوين النشر للتأكد من صحة جميع الملفات والإعدادات
"""

import os
import sys
import json

def test_docker_compose():
    """اختبار ملف docker-compose.yml"""
    print("🔍 اختبار docker-compose.yml...")
    
    if not os.path.exists('docker-compose.yml'):
        print("❌ ملف docker-compose.yml غير موجود")
        return False
    
    try:
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        
        # التحقق من الخدمات المطلوبة
        required_services = ['web:', 'db:', 'nginx:']
        
        for service in required_services:
            if service not in content:
                print(f"❌ الخدمة {service} غير موجودة")
                return False
        
        print("✅ docker-compose.yml صحيح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في docker-compose.yml: {e}")
        return False

def test_nginx_config():
    """اختبار تكوين nginx"""
    print("🔍 اختبار nginx.conf...")
    
    if not os.path.exists('nginx.conf'):
        print("❌ ملف nginx.conf غير موجود")
        return False
    
    with open('nginx.conf', 'r') as f:
        content = f.read()
    
    # التحقق من العناصر المطلوبة
    required_elements = [
        'upstream app',
        'proxy_pass http://app',
        'ssl_certificate',
        'client_max_body_size'
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ العنصر المطلوب '{element}' غير موجود في nginx.conf")
            return False
    
    print("✅ nginx.conf صحيح")
    return True

def test_deployment_scripts():
    """اختبار نصوص النشر"""
    print("🔍 اختبار نصوص النشر...")
    
    scripts = [
        'deployment/deploy.sh',
        'deployment/backup.sh'
    ]
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"❌ النص {script} غير موجود")
            return False
        
        if not os.access(script, os.X_OK):
            print(f"❌ النص {script} غير قابل للتنفيذ")
            return False
    
    print("✅ نصوص النشر صحيحة")
    return True

def test_environment_file():
    """اختبار ملف متغيرات البيئة"""
    print("🔍 اختبار deployment/production.env...")
    
    env_file = 'deployment/production.env'
    if not os.path.exists(env_file):
        print("❌ ملف production.env غير موجود")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    # التحقق من المتغيرات المطلوبة
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET',
        'FIREBASE_API_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_APP_ID'
    ]
    
    for var in required_vars:
        if var not in content:
            print(f"❌ المتغير {var} غير موجود")
            return False
    
    print("✅ ملف متغيرات البيئة صحيح")
    return True

def test_application_structure():
    """اختبار هيكل التطبيق"""
    print("🔍 اختبار هيكل التطبيق...")
    
    required_files = [
        'app.py',
        'main.py',
        'models.py',
        'Dockerfile',
        'pyproject.toml'
    ]
    
    required_dirs = [
        'templates',
        'static',
        'routes',
        'services',
        'utils'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ الملف {file} غير موجود")
            return False
    
    for dir in required_dirs:
        if not os.path.exists(dir):
            print(f"❌ المجلد {dir} غير موجود")
            return False
    
    print("✅ هيكل التطبيق صحيح")
    return True

def test_dockerfile():
    """اختبار Dockerfile"""
    print("🔍 اختبار Dockerfile...")
    
    if not os.path.exists('Dockerfile'):
        print("❌ ملف Dockerfile غير موجود")
        return False
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    required_elements = [
        'FROM python',
        'COPY pyproject.toml',
        'RUN pip install',
        'EXPOSE 5000',
        'CMD'
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ العنصر '{element}' غير موجود في Dockerfile")
            return False
    
    print("✅ Dockerfile صحيح")
    return True

def create_deployment_summary():
    """إنشاء ملخص النشر"""
    summary = {
        "نظام": "نُظم - نظام إدارة الموظفين والمركبات",
        "الإصدار": "1.0.0",
        "تاريخ_التحضير": "2025-06-07",
        "ملفات_النشر": {
            "docker-compose.yml": "تكوين الحاويات الرئيسي",
            "nginx.conf": "إعدادات خادم الويب",
            "Dockerfile": "تكوين حاوية التطبيق",
            "deployment/deploy.sh": "نص النشر التلقائي",
            "deployment/backup.sh": "نص النسخ الاحتياطي",
            "deployment/production.env": "متغيرات البيئة للإنتاج",
            "deployment/README_DEPLOYMENT.md": "دليل النشر المفصل"
        },
        "متطلبات_الخادم": {
            "نظام_التشغيل": "Ubuntu 20.04+",
            "الذاكرة": "4GB RAM minimum",
            "التخزين": "50GB minimum",
            "البرامج": ["Docker", "Docker Compose", "Nginx"]
        },
        "خطوات_النشر": [
            "رفع الملفات للخادم",
            "تخصيص متغيرات البيئة",
            "تشغيل ./deployment/deploy.sh",
            "إعداد SSL (اختياري)"
        ]
    }
    
    with open('deployment/deployment_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("✅ تم إنشاء ملخص النشر في deployment/deployment_summary.json")

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار تكوين النشر...\n")
    
    tests = [
        test_application_structure,
        test_dockerfile,
        test_docker_compose,
        test_nginx_config,
        test_deployment_scripts,
        test_environment_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # إنشاء ملخص النشر
    create_deployment_summary()
    
    print(f"📊 نتائج الاختبار: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للنشر.")
        print("\n📦 ملفات النشر جاهزة:")
        print("   • docker-compose.yml")
        print("   • nginx.conf")
        print("   • deployment/deploy.sh")
        print("   • deployment/backup.sh")
        print("   • deployment/production.env")
        print("   • deployment/README_DEPLOYMENT.md")
        print("\n🚀 لبدء النشر: ./deployment/deploy.sh")
        return True
    else:
        print(f"❌ فشل {total - passed} اختبار. يجب إصلاح المشاكل قبل النشر.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)