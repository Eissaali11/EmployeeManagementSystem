// إصلاح التوقيعات في صفحة فحص السيارة
console.log('🔧 تحميل إصلاح التوقيعات...');

// انتظار تحميل Fabric.js والصفحة
function initializeSignatureFix() {
    console.log('🔧 بدء إصلاح التوقيعات...');
    
    if (!window.fabric) {
        console.log('⚠️ Fabric.js غير متاح، إعادة المحاولة...');
        setTimeout(initializeSignatureFix, 1000);
        return;
    }

    ['supervisor', 'driver', 'movement-officer'].forEach(type => {
        const canvasId = `${type}-signature-canvas`;
        const el = document.getElementById(canvasId);
        
        if (el && (!window.signaturePads || !window.signaturePads[canvasId] || !window.signaturePads[canvasId].isDrawingMode)) {
            try {
                // تنظيف Canvas السابق إن وجد
                if (window.signaturePads && window.signaturePads[canvasId]) {
                    try {
                        window.signaturePads[canvasId].dispose();
                    } catch (e) {
                        console.log(`تنظيف ${canvasId}:`, e.message);
                    }
                }
                
                // إعداد أبعاد Canvas
                const container = el.closest('.signature-pad-container') || el.parentElement;
                const rect = container.getBoundingClientRect();
                const width = Math.max(Math.min(rect.width || 300, 400), 280);
                const height = 150;
                
                // تحديد أبعاد HTML Canvas
                el.width = width;
                el.height = height;
                el.style.width = '100%';
                el.style.height = height + 'px';
                el.style.border = '2px dashed #007bff';
                el.style.borderRadius = '8px';
                el.style.backgroundColor = '#f8f9fa';
                el.style.cursor = 'crosshair';
                
                // إنشاء Fabric Canvas جديد
                const canvas = new fabric.Canvas(canvasId, {
                    isDrawingMode: true,
                    backgroundColor: 'transparent',
                    width: width,
                    height: height
                });
                
                // إعداد فرشاة الرسم
                canvas.freeDrawingBrush.color = "#000";
                canvas.freeDrawingBrush.width = 2;
                
                // إعداد المتغير العام
                if (!window.signaturePads) window.signaturePads = {};
                window.signaturePads[canvasId] = canvas;
                
                // إعادة حساب الإحداثيات بعد التحميل
                setTimeout(() => {
                    canvas.calcOffset();
                    canvas.renderAll();
                }, 200);
                
                // إضافة مؤشر بصري عند الرسم
                canvas.on('path:created', function() {
                    console.log(`✏️ تم إضافة توقيع في: ${type}`);
                });
                
                console.log(`✅ إصلاح تم بنجاح: ${type} (${width}x${height})`);
            } catch (error) {
                console.error(`❌ فشل إصلاح ${type}:`, error);
            }
        }
    });
    
    // إعادة تفعيل أزرار المسح
    document.querySelectorAll('.clear-signature').forEach(btn => {
        btn.onclick = () => {
            const canvasId = btn.dataset.canvasId;
            if (window.signaturePads && window.signaturePads[canvasId]) {
                window.signaturePads[canvasId].clear();
                console.log(`🧹 تم مسح التوقيع: ${canvasId}`);
            }
        };
    });
    
    console.log('✅ تم إكمال إصلاح التوقيعات');
}

// تشغيل الإصلاح عند تحميل الصفحة
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initializeSignatureFix, 3000);
    });
} else {
    setTimeout(initializeSignatureFix, 3000);
}

// إصلاح إضافي عند تغيير التبويبات
document.addEventListener('DOMContentLoaded', function() {
    // مراقبة تغيير التبويبات
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const targetId = e.target.dataset.bsTarget;
            if (targetId && targetId.includes('-draw-tab')) {
                const canvasId = targetId.replace('#','').replace('-draw-tab','-signature-canvas');
                setTimeout(() => {
                    if (window.signaturePads && window.signaturePads[canvasId]) {
                        window.signaturePads[canvasId].calcOffset();
                        console.log(`📐 تم إعادة حساب إحداثيات: ${canvasId}`);
                    }
                }, 100);
            }
        });
    });
    
    // تحسين حفظ التوقيعات عند الإرسال
    const mainForm = document.getElementById('main-handover-form');
    if (mainForm) {
        mainForm.addEventListener('submit', function(e) {
            console.log('💾 حفظ التوقيعات قبل الإرسال...');
            
            // حفظ بيانات التوقيعات
            if (window.signaturePads) {
                Object.keys(window.signaturePads).forEach(canvasId => {
                    const canvas = window.signaturePads[canvasId];
                    const inputId = canvasId.replace('-canvas', '-data');
                    const input = document.getElementById(inputId);
                    
                    if (canvas && input) {
                        try {
                            // التحقق من وجود رسم في Canvas
                            const objects = canvas.getObjects();
                            if (objects.length > 0) {
                                const dataURL = canvas.toDataURL('image/png');
                                input.value = dataURL;
                                console.log(`💾 تم حفظ التوقيع: ${canvasId} (${objects.length} عناصر)`);
                            } else {
                                console.log(`⚠️ لا يوجد رسم في: ${canvasId}`);
                            }
                        } catch (error) {
                            console.error(`❌ فشل حفظ ${canvasId}:`, error);
                        }
                    }
                });
            }
        });
    }
});

// إصلاح إضافي عند تغيير حجم النافذة
window.addEventListener('resize', () => {
    setTimeout(() => {
        if (window.signaturePads) {
            Object.keys(window.signaturePads).forEach(canvasId => {
                if (window.signaturePads[canvasId]) {
                    window.signaturePads[canvasId].calcOffset();
                }
            });
        }
    }, 300);
});