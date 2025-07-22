/**
 * نظام خريطة أضرار السيارة - نُظم
 * يستخدم Fabric.js لرسم علامات الضرر على صورة السيارة
 */

let canvas = null;
let currentDrawingMode = 'damage';
let isDrawingEnabled = true;

// ألوان علامات الضرر
const damageColors = {
    damage: '#dc3545',    // أحمر للضرر
    scratch: '#ffc107',   // أصفر للخدوش
    dent: '#17a2b8'       // أزرق للانبعاجات
};

// أيقونات علامات الضرر
const damageIcons = {
    damage: '⚠️',
    scratch: '🔸',
    dent: '🔵'
};

/**
 * تهيئة نظام خريطة الضرر
 */
function initializeDamageMap() {
    console.log('🎨 بدء تهيئة نظام خريطة الضرر');
    
    try {
        // إنشاء Fabric.js canvas
        canvas = new fabric.Canvas('damage-canvas', {
            width: 400,
            height: 300,
            backgroundColor: 'white',
            selection: true,
            isDrawingMode: false
        });

        // تحميل صورة السيارة كخلفية
        loadVehicleImage();

        // إضافة مستمعي الأحداث
        addCanvasEventListeners();
        
        // إخفاء مؤشر التحميل
        hideLoadingIndicator();
        
        console.log('✅ تم تهيئة نظام خريطة الضرر بنجاح');
        
    } catch (error) {
        console.error('❌ خطأ في تهيئة نظام خريطة الضرر:', error);
        showCanvasError('فشل في تحميل نظام خريطة الضرر');
    }
}

/**
 * تحميل صورة السيارة كخلفية للـ canvas
 */
function loadVehicleImage() {
    const imagePaths = [
        '/static/images/vehicle_diagram_new.png',
        '/static/images/vehicle_diagram.png',
        '/static/images/vehicle_diagram1.png',
        '/static/images/front-car.png'
    ];
    
    loadImageWithFallback(imagePaths, 0);
}

/**
 * تحميل الصورة مع آلية fallback
 */
function loadImageWithFallback(imagePaths, index) {
    if (index >= imagePaths.length) {
        console.warn('⚠️ لم يتم العثور على صورة السيارة، استخدام خلفية افتراضية');
        drawDefaultVehicleOutline();
        return;
    }
    
    const imagePath = imagePaths[index];
    console.log(`🔄 محاولة تحميل الصورة: ${imagePath}`);
    
    fabric.Image.fromURL(imagePath, function(img) {
        if (img.getElement() && img.getElement().complete && img.getElement().naturalHeight !== 0) {
            // نجح التحميل
            console.log(`✅ تم تحميل صورة السيارة: ${imagePath}`);
            
            // تعديل حجم الصورة لتناسب الـ canvas
            const canvasWidth = canvas.getWidth();
            const canvasHeight = canvas.getHeight();
            
            img.scaleToWidth(canvasWidth * 0.8);
            img.scaleToHeight(canvasHeight * 0.8);
            
            // توسيط الصورة
            img.set({
                left: (canvasWidth - img.getScaledWidth()) / 2,
                top: (canvasHeight - img.getScaledHeight()) / 2,
                selectable: false,
                evented: false
            });
            
            // إضافة الصورة كخلفية
            canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
            
        } else {
            // فشل التحميل، جرب الصورة التالية
            console.warn(`⚠️ فشل في تحميل الصورة: ${imagePath}`);
            loadImageWithFallback(imagePaths, index + 1);
        }
    }, {
        // خيارات تحميل الصورة
        crossOrigin: 'anonymous'
    });
}

/**
 * رسم مخطط سيارة افتراضي في حالة عدم توفر الصورة
 */
function drawDefaultVehicleOutline() {
    console.log('🚗 رسم مخطط السيارة الافتراضي');
    
    // رسم شكل سيارة بسيط
    const rect = new fabric.Rect({
        left: 50,
        top: 80,
        width: 300,
        height: 140,
        fill: 'transparent',
        stroke: '#333',
        strokeWidth: 3,
        rx: 15,
        ry: 15,
        selectable: false,
        evented: false
    });
    
    // إضافة عجلات
    const wheel1 = new fabric.Circle({
        left: 80,
        top: 200,
        radius: 20,
        fill: 'transparent',
        stroke: '#333',
        strokeWidth: 2,
        selectable: false,
        evented: false
    });
    
    const wheel2 = new fabric.Circle({
        left: 280,
        top: 200,
        radius: 20,
        fill: 'transparent',
        stroke: '#333',
        strokeWidth: 2,
        selectable: false,
        evented: false
    });
    
    canvas.add(rect);
    canvas.add(wheel1);
    canvas.add(wheel2);
    
    // إضافة نص توضيحي
    const text = new fabric.Text('مخطط السيارة', {
        left: 160,
        top: 140,
        fontSize: 16,
        fill: '#666',
        selectable: false,
        evented: false
    });
    
    canvas.add(text);
}

/**
 * إضافة مستمعي الأحداث للـ canvas
 */
function addCanvasEventListeners() {
    // عند النقر على الـ canvas لإضافة علامة ضرر
    canvas.on('mouse:down', function(e) {
        if (!isDrawingEnabled || !e.pointer) return;
        
        addDamageMarker(e.pointer.x, e.pointer.y, currentDrawingMode);
    });
    
    // عند تحديد عنصر (للحذف أو التعديل)
    canvas.on('selection:created', function(e) {
        if (e.selected && e.selected.length > 0) {
            const selectedObject = e.selected[0];
            if (selectedObject.damageType) {
                showDamageDetails(selectedObject);
            }
        }
    });
}

/**
 * إضافة علامة ضرر في الموقع المحدد
 */
function addDamageMarker(x, y, damageType) {
    const color = damageColors[damageType] || damageColors.damage;
    const icon = damageIcons[damageType] || damageIcons.damage;
    
    // إنشاء دائرة لعلامة الضرر
    const marker = new fabric.Circle({
        left: x - 10,
        top: y - 10,
        radius: 8,
        fill: color,
        stroke: '#fff',
        strokeWidth: 2,
        damageType: damageType,
        damageId: Date.now(),
        hasControls: true,
        hasBorders: true
    });
    
    // إضافة نص لنوع الضرر
    const label = new fabric.Text(icon, {
        left: x - 8,
        top: y - 12,
        fontSize: 12,
        fill: '#fff',
        selectable: false,
        evented: false
    });
    
    // إنشاء مجموعة من العلامة والنص
    const damageGroup = new fabric.Group([marker, label], {
        left: x - 10,
        top: y - 10,
        damageType: damageType,
        damageId: Date.now(),
        hasControls: true,
        hasBorders: true
    });
    
    canvas.add(damageGroup);
    canvas.renderAll();
    
    console.log(`🔧 تمت إضافة علامة ${damageType} في الموقع (${x}, ${y})`);
    
    // تحديث قائمة الأضرار
    updateDamageList();
}

/**
 * تعيين نمط الرسم الحالي
 */
function setDrawingMode(mode) {
    currentDrawingMode = mode;
    
    // تحديث أزرار نمط الرسم
    document.querySelectorAll('[id$="-btn"]').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeButton = document.getElementById(mode + '-btn');
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    console.log(`🎨 تم تعيين نمط الرسم: ${mode}`);
}

/**
 * مسح جميع علامات الضرر
 */
function clearCanvas() {
    if (confirm('هل تريد مسح جميع علامات الضرر؟')) {
        const objects = canvas.getObjects();
        
        // حذف جميع العناصر ما عدا الخلفية
        objects.forEach(obj => {
            if (obj.damageType) {
                canvas.remove(obj);
            }
        });
        
        canvas.renderAll();
        updateDamageList();
        
        console.log('🧹 تم مسح جميع علامات الضرر');
    }
}

/**
 * تحديث قائمة الأضرار
 */
function updateDamageList() {
    const damages = canvas.getObjects().filter(obj => obj.damageType);
    
    // تحديث حقل مخفي بقائمة الأضرار (لإرسالها مع النموذج)
    const damageData = damages.map(damage => ({
        type: damage.damageType,
        x: damage.left + 10,
        y: damage.top + 10,
        id: damage.damageId
    }));
    
    // إنشاء حقل مخفي إذا لم يكن موجوداً
    let damageInput = document.getElementById('damage_markers');
    if (!damageInput) {
        damageInput = document.createElement('input');
        damageInput.type = 'hidden';
        damageInput.id = 'damage_markers';
        damageInput.name = 'damage_markers';
        document.querySelector('form').appendChild(damageInput);
    }
    
    damageInput.value = JSON.stringify(damageData);
    
    console.log(`📋 تم تحديث قائمة الأضرار: ${damages.length} عنصر`);
}

/**
 * عرض تفاصيل علامة الضرر
 */
function showDamageDetails(damageObject) {
    const damageType = damageObject.damageType;
    const typeText = {
        damage: 'ضرر',
        scratch: 'خدش', 
        dent: 'انبعاج'
    }[damageType] || damageType;
    
    // إمكانية حذف العلامة
    if (confirm(`نوع الضرر: ${typeText}\nهل تريد حذف هذه العلامة؟`)) {
        canvas.remove(damageObject);
        canvas.renderAll();
        updateDamageList();
    }
}

/**
 * إخفاء مؤشر التحميل
 */
function hideLoadingIndicator() {
    const loadingDiv = document.getElementById('canvas-loading');
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

/**
 * عرض خطأ في الـ canvas
 */
function showCanvasError(message) {
    const loadingDiv = document.getElementById('canvas-loading');
    if (loadingDiv) {
        loadingDiv.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle mb-2"></i>
                <small class="d-block">${message}</small>
            </div>
        `;
    }
}

/**
 * تهيئة النظام عند تحميل الصفحة
 */
document.addEventListener('DOMContentLoaded', function() {
    // التأكد من وجود Fabric.js
    if (typeof fabric === 'undefined') {
        console.error('❌ مكتبة Fabric.js غير محملة');
        showCanvasError('مكتبة الرسم غير محملة');
        return;
    }
    
    // التأكد من وجود عنصر canvas
    const canvasElement = document.getElementById('damage-canvas');
    if (!canvasElement) {
        console.warn('⚠️ عنصر canvas غير موجود في الصفحة');
        return;
    }
    
    // تهيئة النظام بعد فترة قصيرة للتأكد من تحميل جميع العناصر
    setTimeout(initializeDamageMap, 500);
});

// تصدير الدوال للاستخدام الخارجي
window.setDrawingMode = setDrawingMode;
window.clearCanvas = clearCanvas;