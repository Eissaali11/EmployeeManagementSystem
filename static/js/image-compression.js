/**
 * Image Compression Utility for Mobile Upload
 * يقوم بضغط الصور قبل رفعها لتجنب خطأ "Request Entity Too Large"
 */

class ImageCompressor {
    constructor(options = {}) {
        this.maxWidth = options.maxWidth || 1024;
        this.maxHeight = options.maxHeight || 1024;
        this.quality = options.quality || 0.8;
        this.maxFileSize = options.maxFileSize || 2 * 1024 * 1024; // 2MB
        this.outputFormat = options.outputFormat || 'image/jpeg';
    }

    /**
     * ضغط الصورة
     * @param {File} file - ملف الصورة
     * @returns {Promise<File>} - الصورة المضغوطة
     */
    async compressImage(file) {
        return new Promise((resolve, reject) => {
            // التحقق من نوع الملف
            if (!file.type.startsWith('image/')) {
                resolve(file); // إرجاع الملف كما هو إذا لم يكن صورة
                return;
            }

            // التحقق من حجم الملف
            if (file.size <= this.maxFileSize) {
                resolve(file); // إرجاع الملف كما هو إذا كان صغيراً
                return;
            }

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // حساب الأبعاد الجديدة
                const { width, height } = this.calculateDimensions(img.width, img.height);
                
                // تعيين أبعاد الكانفاس
                canvas.width = width;
                canvas.height = height;

                // رسم الصورة مع الأبعاد الجديدة
                ctx.drawImage(img, 0, 0, width, height);

                // تحويل الكانفاس إلى blob
                canvas.toBlob((blob) => {
                    if (blob) {
                        // إنشاء ملف جديد مع نفس الاسم
                        const compressedFile = new File([blob], file.name, {
                            type: this.outputFormat,
                            lastModified: Date.now()
                        });
                        
                        console.log(`Original size: ${(file.size / 1024 / 1024).toFixed(2)}MB`);
                        console.log(`Compressed size: ${(compressedFile.size / 1024 / 1024).toFixed(2)}MB`);
                        
                        resolve(compressedFile);
                    } else {
                        reject(new Error('فشل في ضغط الصورة'));
                    }
                }, this.outputFormat, this.quality);
            };

            img.onerror = () => {
                reject(new Error('فشل في تحميل الصورة'));
            };

            // قراءة الملف كـ data URL
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    /**
     * حساب الأبعاد الجديدة مع الحفاظ على نسبة العرض إلى الارتفاع
     * @param {number} width - العرض الأصلي
     * @param {number} height - الارتفاع الأصلي
     * @returns {Object} - الأبعاد الجديدة
     */
    calculateDimensions(width, height) {
        let newWidth = width;
        let newHeight = height;

        // إذا كانت الصورة أكبر من الحد الأقصى
        if (width > this.maxWidth || height > this.maxHeight) {
            const aspectRatio = width / height;

            if (width > height) {
                newWidth = this.maxWidth;
                newHeight = this.maxWidth / aspectRatio;
            } else {
                newHeight = this.maxHeight;
                newWidth = this.maxHeight * aspectRatio;
            }

            // التأكد من عدم تجاوز الحد الأقصى
            if (newWidth > this.maxWidth) {
                newWidth = this.maxWidth;
                newHeight = this.maxWidth / aspectRatio;
            }
            if (newHeight > this.maxHeight) {
                newHeight = this.maxHeight;
                newWidth = this.maxHeight * aspectRatio;
            }
        }

        return {
            width: Math.round(newWidth),
            height: Math.round(newHeight)
        };
    }

    /**
     * ضغط عدة صور
     * @param {FileList} files - قائمة الملفات
     * @returns {Promise<File[]>} - الصور المضغوطة
     */
    async compressMultipleImages(files) {
        const compressedFiles = [];
        
        for (let i = 0; i < files.length; i++) {
            try {
                const compressedFile = await this.compressImage(files[i]);
                compressedFiles.push(compressedFile);
            } catch (error) {
                console.error(`فشل في ضغط الصورة ${files[i].name}:`, error);
                compressedFiles.push(files[i]); // إضافة الملف الأصلي في حالة الفشل
            }
        }
        
        return compressedFiles;
    }
}

/**
 * تطبيق ضغط الصور على حقول الرفع
 * @param {string} selector - محدد حقول الرفع
 * @param {Object} options - خيارات الضغط
 */
function applyImageCompression(selector = 'input[type="file"]', options = {}) {
    const compressor = new ImageCompressor(options);
    const fileInputs = document.querySelectorAll(selector);

    fileInputs.forEach(input => {
        input.addEventListener('change', async function(event) {
            if (this.files && this.files.length > 0) {
                // إظهار مؤشر التحميل
                showLoadingIndicator(this);

                try {
                    const compressedFiles = await compressor.compressMultipleImages(this.files);
                    
                    // إنشاء DataTransfer جديد للملفات المضغوطة
                    const dataTransfer = new DataTransfer();
                    compressedFiles.forEach(file => {
                        dataTransfer.items.add(file);
                    });
                    
                    // تحديث الملفات في حقل الإدخال
                    this.files = dataTransfer.files;
                    
                    // إخفاء مؤشر التحميل
                    hideLoadingIndicator(this);
                    
                    // عرض معاينة الصور (اختياري)
                    showImagePreview(this);
                    
                } catch (error) {
                    console.error('خطأ في ضغط الصور:', error);
                    hideLoadingIndicator(this);
                    showError('فشل في ضغط الصور. سيتم رفع الصور الأصلية.');
                }
            }
        });
    });
}

/**
 * إظهار مؤشر التحميل
 * @param {HTMLElement} input - حقل الإدخال
 */
function showLoadingIndicator(input) {
    let indicator = input.parentNode.querySelector('.compression-loading');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'compression-loading';
        indicator.innerHTML = `
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                color: #667eea;
                font-size: 0.9rem;
                margin-top: 8px;
            ">
                <div style="
                    width: 16px;
                    height: 16px;
                    border: 2px solid #e2e8f0;
                    border-top: 2px solid #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
                جاري ضغط الصور...
            </div>
        `;
        input.parentNode.appendChild(indicator);
    }
    indicator.style.display = 'block';
}

/**
 * إخفاء مؤشر التحميل
 * @param {HTMLElement} input - حقل الإدخال
 */
function hideLoadingIndicator(input) {
    const indicator = input.parentNode.querySelector('.compression-loading');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

/**
 * عرض معاينة الصور
 * @param {HTMLElement} input - حقل الإدخال
 */
function showImagePreview(input) {
    let preview = input.parentNode.querySelector('.image-preview');
    if (!preview) {
        preview = document.createElement('div');
        preview.className = 'image-preview';
        preview.style.cssText = `
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        `;
        input.parentNode.appendChild(preview);
    }
    
    preview.innerHTML = '';
    
    Array.from(input.files).forEach((file, index) => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.cssText = `
                    width: 60px;
                    height: 60px;
                    object-fit: cover;
                    border-radius: 8px;
                    border: 2px solid #e2e8f0;
                `;
                preview.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    });
}

/**
 * عرض رسالة خطأ
 * @param {string} message - نص الرسالة
 */
function showError(message) {
    // يمكن تخصيص هذه الدالة حسب نظام الإشعارات المستخدم
    console.warn(message);
    
    // إنشاء إشعار بسيط
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 10000;
        max-width: 300px;
        font-size: 0.9rem;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// إضافة CSS للرسوم المتحركة
if (!document.querySelector('#image-compression-styles')) {
    const style = document.createElement('style');
    style.id = 'image-compression-styles';
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

// تصدير للاستخدام العالمي
window.ImageCompressor = ImageCompressor;
window.applyImageCompression = applyImageCompression;