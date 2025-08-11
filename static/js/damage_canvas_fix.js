// إصلاح مشكلة الرسم على مخطط السيارة
console.log('🔧 تحميل إصلاح مخطط الأضرار...');

function fixDamageCanvas() {
    console.log('🔧 بدء إصلاح مخطط الأضرار...');
    
    if (!window.fabric) {
        console.log('⚠️ Fabric.js غير متاح، إعادة المحاولة...');
        setTimeout(fixDamageCanvas, 1000);
        return;
    }

    const damageCanvasEl = document.getElementById('damage-canvas');
    if (!damageCanvasEl) {
        console.log('❌ عنصر damage-canvas غير موجود');
        return;
    }

    try {
        // التنظيف السابق
        if (window.damageCanvas) {
            try {
                window.damageCanvas.dispose();
            } catch (e) {
                console.log('تنظيف damage-canvas:', e.message);
            }
        }

        // إعداد أبعاد Canvas
        const container = damageCanvasEl.parentElement;
        const width = Math.min(container.offsetWidth || 400, 450);
        const height = 300;

        damageCanvasEl.width = width;
        damageCanvasEl.height = height;
        damageCanvasEl.style.width = width + 'px';
        damageCanvasEl.style.height = height + 'px';
        damageCanvasEl.style.border = '2px solid #ddd';
        damageCanvasEl.style.borderRadius = '8px';
        damageCanvasEl.style.backgroundColor = '#ffffff';
        damageCanvasEl.style.cursor = 'crosshair';
        damageCanvasEl.style.touchAction = 'none';

        // إنشاء Canvas جديد
        const canvas = new fabric.Canvas('damage-canvas', {
            isDrawingMode: false, // نبدأ بوضع التحديد
            backgroundColor: '#ffffff',
            width: width,
            height: height,
            selection: true,
            preserveObjectStacking: true
        });

        // إعداد فرشاة الرسم
        canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
        canvas.freeDrawingBrush.color = "#E53935";
        canvas.freeDrawingBrush.width = 4;

        // رسم مخطط بسيط للسيارة
        const carBody = new fabric.Rect({
            left: 50,
            top: 80,
            width: width - 100,
            height: 140,
            fill: 'transparent',
            stroke: '#333333',
            strokeWidth: 3,
            rx: 20,
            ry: 20,
            selectable: false,
            evented: false
        });

        // الزجاج الأمامي
        const windshield = new fabric.Rect({
            left: 80,
            top: 50,
            width: width - 160,
            height: 40,
            fill: 'rgba(173, 216, 230, 0.3)',
            stroke: '#333333',
            strokeWidth: 2,
            rx: 10,
            ry: 10,
            selectable: false,
            evented: false
        });

        // العجلات
        const wheel1 = new fabric.Circle({
            left: 80,
            top: 240,
            radius: 20,
            fill: '#333333',
            selectable: false,
            evented: false
        });

        const wheel2 = new fabric.Circle({
            left: width - 120,
            top: 240,
            radius: 20,
            fill: '#333333',
            selectable: false,
            evented: false
        });

        // النص التوضيحي
        const instructionText = new fabric.Text('انقر واسحب لتحديد مواقع الأضرار', {
            left: width / 2,
            top: 150,
            fontSize: 14,
            textAlign: 'center',
            originX: 'center',
            originY: 'center',
            fill: '#666666',
            selectable: false,
            evented: false
        });

        // إضافة العناصر للـ Canvas
        canvas.add(carBody, windshield, wheel1, wheel2, instructionText);

        // إعداد أدوات التحكم
        const drawModeBtn = document.getElementById('draw-mode-btn');
        const selectModeBtn = document.getElementById('select-mode-btn');
        const colorPicker = document.getElementById('draw-color-picker');
        const lineWidth = document.getElementById('draw-line-width');
        const clearBtn = document.getElementById('clear-canvas-btn');

        if (drawModeBtn) {
            drawModeBtn.onclick = () => {
                canvas.isDrawingMode = true;
                drawModeBtn.classList.add('active');
                if (selectModeBtn) selectModeBtn.classList.remove('active');
                console.log('🖊️ تم تفعيل وضع الرسم');
            };
        }

        if (selectModeBtn) {
            selectModeBtn.onclick = () => {
                canvas.isDrawingMode = false;
                selectModeBtn.classList.add('active');
                if (drawModeBtn) drawModeBtn.classList.remove('active');
                console.log('👆 تم تفعيل وضع التحديد');
            };
        }

        if (colorPicker) {
            colorPicker.onchange = (e) => {
                canvas.freeDrawingBrush.color = e.target.value;
                console.log('🎨 تم تغيير اللون إلى:', e.target.value);
            };
        }

        if (lineWidth) {
            lineWidth.oninput = (e) => {
                canvas.freeDrawingBrush.width = parseInt(e.target.value);
                console.log('📏 تم تغيير سمك الخط إلى:', e.target.value);
            };
        }

        if (clearBtn) {
            clearBtn.onclick = () => {
                if (confirm('هل تريد مسح جميع الرسوم؟')) {
                    // مسح كل شيء عدا العناصر الأساسية
                    const objectsToKeep = [carBody, windshield, wheel1, wheel2, instructionText];
                    const allObjects = canvas.getObjects();
                    
                    allObjects.forEach(obj => {
                        if (!objectsToKeep.includes(obj)) {
                            canvas.remove(obj);
                        }
                    });
                    
                    canvas.renderAll();
                    console.log('🧹 تم مسح الرسوم');
                }
            };
        }

        // تفعيل وضع الرسم افتراضياً
        setTimeout(() => {
            canvas.isDrawingMode = true;
            if (drawModeBtn) drawModeBtn.classList.add('active');
            console.log('🎯 تم تفعيل وضع الرسم افتراضياً');
        }, 100);

        // أحداث الرسم
        canvas.on('path:created', function(e) {
            console.log('🔧 تم إضافة رسم جديد على مخطط السيارة');
            e.path.selectable = false; // منع تحديد الرسوم
        });

        // دعم الأجهزة اللمسية
        damageCanvasEl.addEventListener('touchstart', function(e) {
            e.preventDefault();
        }, { passive: false });

        damageCanvasEl.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });

        // إعادة حساب الإحداثيات
        setTimeout(() => {
            canvas.calcOffset();
            canvas.renderAll();
        }, 200);

        // حفظ المرجع العام
        window.damageCanvas = canvas;

        console.log(`✅ تم إصلاح مخطط الأضرار بنجاح (${width}x${height})`);

    } catch (error) {
        console.error('❌ فشل إصلاح مخطط الأضرار:', error);
    }
}

// تشغيل الإصلاح
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(fixDamageCanvas, 2000);
    });
} else {
    setTimeout(fixDamageCanvas, 2000);
}

// حفظ بيانات مخطط الأضرار عند الإرسال
document.addEventListener('DOMContentLoaded', function() {
    const mainForm = document.getElementById('main-handover-form');
    if (mainForm) {
        mainForm.addEventListener('submit', function(e) {
            if (window.damageCanvas) {
                try {
                    const dataURL = window.damageCanvas.toDataURL('image/png');
                    const input = document.getElementById('damage-diagram-data');
                    if (input) {
                        input.value = dataURL;
                        console.log('💾 تم حفظ مخطط الأضرار');
                    }
                } catch (error) {
                    console.error('❌ فشل حفظ مخطط الأضرار:', error);
                }
            }
        });
    }
});