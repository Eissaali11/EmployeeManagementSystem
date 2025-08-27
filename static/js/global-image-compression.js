/**
 * Global Image Compression Configuration
 * إعدادات ضغط الصور العامة للتطبيق
 */

// إعدادات ضغط الصور حسب نوع الاستخدام
const COMPRESSION_PRESETS = {
    // للصور الشخصية (موظفين)
    profile: {
        maxWidth: 800,
        maxHeight: 800,
        quality: 0.85,
        maxFileSize: 1.5 * 1024 * 1024, // 1.5MB
        outputFormat: 'image/jpeg'
    },
    
    // للوثائق
    document: {
        maxWidth: 1200,
        maxHeight: 1200,
        quality: 0.85,
        maxFileSize: 3 * 1024 * 1024, // 3MB
        outputFormat: 'image/jpeg'
    },
    
    // للمركبات
    vehicle: {
        maxWidth: 1024,
        maxHeight: 1024,
        quality: 0.8,
        maxFileSize: 2 * 1024 * 1024, // 2MB
        outputFormat: 'image/jpeg'
    },
    
    // للتقارير والمرفقات العامة
    general: {
        maxWidth: 1024,
        maxHeight: 1024,
        quality: 0.8,
        maxFileSize: 2 * 1024 * 1024, // 2MB
        outputFormat: 'image/jpeg'
    }
};

/**
 * تطبيق ضغط الصور تلقائياً على الصفحة
 * @param {string} preset - نوع الإعداد المستخدم
 */
function initializeImageCompression(preset = 'general') {
    if (!window.ImageCompressor || !window.applyImageCompression) {
        console.warn('Image compression library not loaded');
        return;
    }
    
    const config = COMPRESSION_PRESETS[preset] || COMPRESSION_PRESETS.general;
    
    // تطبيق الضغط على جميع حقول رفع الملفات
    window.applyImageCompression('input[type="file"]', config);
    
    // إضافة مؤشرات بصرية للضغط
    addCompressionIndicators();
    
    // تحسين تجربة إرسال النماذج
    enhanceFormSubmission();
    
    console.log(`Image compression initialized with preset: ${preset}`, config);
}

/**
 * إضافة مؤشرات بصرية لعملية الضغط
 */
function addCompressionIndicators() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // إضافة مؤشر التحميل
        const indicator = document.createElement('div');
        indicator.className = 'compression-status';
        indicator.style.cssText = `
            display: none;
            margin-top: 8px;
            padding: 8px 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 6px;
            font-size: 0.85rem;
            text-align: center;
        `;
        
        if (input.parentNode) {
            input.parentNode.appendChild(indicator);
        }
        
        // مراقبة تغيير الملفات
        input.addEventListener('change', function() {
            const files = Array.from(this.files);
            const imageFiles = files.filter(file => file.type.startsWith('image/'));
            const largeFiles = imageFiles.filter(file => file.size > 5 * 1024 * 1024);
            
            if (largeFiles.length > 0) {
                indicator.style.display = 'block';
                indicator.innerHTML = `
                    <i class="fas fa-compress-alt"></i>
                    جاري ضغط ${largeFiles.length} صورة...
                `;
                
                // إخفاء المؤشر بعد 3 ثواني
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 3000);
            }
        });
    });
}

/**
 * تحسين تجربة إرسال النماذج
 */
function enhanceFormSubmission() {
    const forms = document.querySelectorAll('form[enctype*="multipart"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButtons = this.querySelectorAll('button[type="submit"], input[type="submit"]');
            
            submitButtons.forEach(button => {
                if (button.disabled) return;
                
                button.disabled = true;
                const originalContent = button.innerHTML || button.value;
                
                if (button.innerHTML) {
                    button.innerHTML = `
                        <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                            <div style="
                                width: 16px;
                                height: 16px;
                                border: 2px solid transparent;
                                border-top: 2px solid currentColor;
                                border-radius: 50%;
                                animation: spin 1s linear infinite;
                            "></div>
                            جاري الحفظ...
                        </div>
                    `;
                } else {
                    button.value = 'جاري الحفظ...';
                }
                
                // إعادة تفعيل الزر في حالة فشل الإرسال
                setTimeout(() => {
                    button.disabled = false;
                    if (button.innerHTML) {
                        button.innerHTML = originalContent;
                    } else {
                        button.value = originalContent;
                    }
                }, 30000);
            });
        });
    });
}

/**
 * عرض إحصائيات الضغط
 * @param {File} originalFile - الملف الأصلي
 * @param {File} compressedFile - الملف المضغوط
 */
function showCompressionStats(originalFile, compressedFile) {
    if (!originalFile || !compressedFile) return;
    
    const originalSize = (originalFile.size / 1024 / 1024).toFixed(2);
    const compressedSize = (compressedFile.size / 1024 / 1024).toFixed(2);
    const savings = (((originalFile.size - compressedFile.size) / originalFile.size) * 100).toFixed(1);
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 16px;
        border-radius: 8px;
        z-index: 10000;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    notification.innerHTML = `
        <div style="text-align: center;">
            <div style="margin-bottom: 8px;">
                <i class="fas fa-compress-alt" style="color: #4CAF50;"></i>
                <strong>تم ضغط الصورة بنجاح</strong>
            </div>
            <div style="font-size: 0.8rem; opacity: 0.8;">
                الحجم الأصلي: ${originalSize}MB → الحجم الجديد: ${compressedSize}MB
                <br>
                توفير في المساحة: ${savings}%
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// إضافة CSS للرسوم المتحركة
if (!document.querySelector('#global-compression-styles')) {
    const style = document.createElement('style');
    style.id = 'global-compression-styles';
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .compression-status {
            transition: all 0.3s ease;
        }
        
        .compression-status.processing {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

// تصدير للاستخدام العالمي
window.initializeImageCompression = initializeImageCompression;
window.COMPRESSION_PRESETS = COMPRESSION_PRESETS;
window.showCompressionStats = showCompressionStats;