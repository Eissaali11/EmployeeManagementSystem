#!/bin/bash

# نص نسخ احتياطي لقاعدة البيانات والملفات
echo "===== بدء عملية النسخ الاحتياطي ====="

# إنشاء مجلد النسخ الاحتياطية
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="nuzum_backup_${DATE}.sql"

mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
echo "إنشاء نسخة احتياطية من قاعدة البيانات..."
docker-compose exec -T db pg_dump -U username nuzum_db > $BACKUP_DIR/$BACKUP_FILE

# ضغط النسخة الاحتياطية
echo "ضغط النسخة الاحتياطية..."
gzip $BACKUP_DIR/$BACKUP_FILE

# نسخ احتياطي للملفات المرفوعة
echo "نسخ الملفات المرفوعة..."
tar -czf $BACKUP_DIR/uploads_backup_${DATE}.tar.gz uploads/

# حذف النسخ الاحتياطية القديمة (أكثر من 30 يوم)
echo "حذف النسخ الاحتياطية القديمة..."
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "===== تم إكمال النسخ الاحتياطي بنجاح ====="
echo "ملف النسخة الاحتياطية: $BACKUP_DIR/${BACKUP_FILE}.gz"
echo "ملف الملفات المرفوعة: $BACKUP_DIR/uploads_backup_${DATE}.tar.gz"