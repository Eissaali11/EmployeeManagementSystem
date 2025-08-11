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
                
                // إعداد أبعاد Canvas بشكل ثابت
                const width = 350;
                const height = 150;
                
                // تحديد أبعاد HTML Canvas بشكل صريح
                el.setAttribute('width', width);
                el.setAttribute('height', height);
                el.style.width = width + 'px';
                el.style.height = height + 'px';
                el.style.border = '2px dashed #007bff';
                el.style.borderRadius = '8px';
                el.style.backgroundColor = '#ffffff';
                el.style.cursor = 'crosshair';
                el.style.touchAction = 'none'; // منع التمرير على الأجهزة اللمسية
                
                // إنشاء Fabric Canvas جديد مع إعدادات محسنة
                const canvas = new fabric.Canvas(canvasId, {
                    isDrawingMode: true,
                    backgroundColor: '#ffffff',
                    width: width,
                    height: height,
                    selection: false,
                    preserveObjectStacking: true
                });
                
                // إعداد فرشاة الرسم بإعدادات محسنة
                canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
                canvas.freeDrawingBrush.color = "#000000";
                canvas.freeDrawingBrush.width = 3;
                canvas.freeDrawingBrush.shadowColor = 'rgba(0,0,0,0.2)';
                canvas.freeDrawingBrush.shadowOffsetX = 1;
                canvas.freeDrawingBrush.shadowOffsetY = 1;
                
                // إعداد المتغير العام
                if (!window.signaturePads) window.signaturePads = {};
                window.signaturePads[canvasId] = canvas;
                
                // إعادة حساب الإحداثيات بعد التحميل
                setTimeout(() => {
                    canvas.calcOffset();
                    canvas.renderAll();
                }, 200);
                
                // إضافة أحداث للتفاعل
                canvas.on('path:created', function(e) {
                    console.log(`✏️ تم إضافة توقيع في: ${type}`);
                    // تأكيد الحفظ
                    e.path.selectable = false;
                    e.path.evented = false;
                });
                
                // منع فقدان الرسم عند التفاعل
                canvas.on('selection:created', function() {
                    canvas.discardActiveObject();
                });
                
                // إضافة دعم للمس
                canvas.on('mouse:down', function() {
                    canvas.isDrawingMode = true;
                });
                
                // إعداد للأجهزة اللمسية
                el.addEventListener('touchstart', function(e) {
                    e.preventDefault();
                    canvas.isDrawingMode = true;
                }, { passive: false });
                
                el.addEventListener('touchmove', function(e) {
                    e.preventDefault();
                }, { passive: false });
                
                console.log(`✅ إصلاح تم بنجاح: ${type} (${width}x${height})`);
            } catch (error) {
                console.error(`❌ فشل إصلاح ${type}:`, error);
            }
        }
    });
    
    // إعادة تفعيل أزرار المسح مع تأكيد
    document.querySelectorAll('.clear-signature').forEach(btn => {
        btn.onclick = () => {
            const canvasId = btn.dataset.canvasId;
            if (window.signaturePads && window.signaturePads[canvasId]) {
                if (confirm('هل تريد مسح التوقيع؟')) {
                    window.signaturePads[canvasId].clear();
                    window.signaturePads[canvasId].backgroundColor = '#ffffff';
                    window.signaturePads[canvasId].renderAll();
                    console.log(`🧹 تم مسح التوقيع: ${canvasId}`);
                }
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