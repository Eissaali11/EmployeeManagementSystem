// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // عناصر واجهة المستخدم
    const installationProgress = document.getElementById('installation-progress');
    const checkSystemBtn = document.getElementById('check-system');
    const setupDatabaseBtn = document.getElementById('setup-database');
    const adminForm = document.getElementById('admin-form');
    
    // المهام التي يجب فحصها
    const installationTasks = [
        { id: 'python', name: 'التحقق من إصدار Python', status: null },
        { id: 'packages', name: 'التحقق من تثبيت الحزم المطلوبة', status: null },
        { id: 'database', name: 'التحقق من الاتصال بقاعدة البيانات', status: null },
        { id: 'env', name: 'التحقق من المتغيرات البيئية', status: null },
        { id: 'files', name: 'التحقق من الملفات والأذونات', status: null }
    ];
    
    // عرض حالة المهام
    function renderTasks() {
        installationProgress.innerHTML = '';
        
        installationTasks.forEach(task => {
            const statusClass = task.status === true ? 'success' : 
                               task.status === false ? 'error' : 
                               task.status === 'warning' ? 'warning' : '';
            
            const statusIcon = task.status === true ? '<i class="bi bi-check-circle-fill"></i>' : 
                              task.status === false ? '<i class="bi bi-x-circle-fill"></i>' : 
                              task.status === 'warning' ? '<i class="bi bi-exclamation-triangle-fill"></i>' : 
                              '<i class="bi bi-hourglass-split"></i>';
            
            const taskElement = document.createElement('div');
            taskElement.className = `progress-item ${statusClass}`;
            taskElement.innerHTML = `
                ${statusIcon}
                <div class="task-name">${task.name}</div>
            `;
            
            installationProgress.appendChild(taskElement);
        });
    }
    
    // محاكاة فحص النظام
    function simulateSystemCheck() {
        installationTasks.forEach(task => task.status = null);
        renderTasks();
        
        const checkSequence = async () => {
            for (let i = 0; i < installationTasks.length; i++) {
                // محاكاة وقت المعالجة
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // تعيين نتيجة عشوائية للعرض التوضيحي
                // في التطبيق الحقيقي، هذا سيكون نتيجة فحص فعلي
                const randomResult = Math.random();
                if (randomResult > 0.8) {
                    installationTasks[i].status = false;
                } else if (randomResult > 0.6) {
                    installationTasks[i].status = 'warning';
                } else {
                    installationTasks[i].status = true;
                }
                
                renderTasks();
            }
            
            // عرض النتيجة النهائية
            const allSuccess = installationTasks.every(task => task.status === true);
            if (allSuccess) {
                showMessage('تم فحص النظام بنجاح!', 'success');
            } else {
                showMessage('هناك بعض المشاكل التي تحتاج إلى معالجة.', 'warning');
            }
        };
        
        checkSequence();
    }
    
    // محاكاة إعداد قاعدة البيانات
    function simulateDatabaseSetup() {
        showMessage('جاري إعداد قاعدة البيانات...', 'info');
        
        // محاكاة وقت المعالجة
        setTimeout(() => {
            const success = Math.random() > 0.3; // 70% فرصة للنجاح
            
            if (success) {
                showMessage('تم إعداد قاعدة البيانات بنجاح!', 'success');
            } else {
                showMessage('حدث خطأ أثناء إعداد قاعدة البيانات. يرجى التحقق من إعدادات الاتصال.', 'danger');
            }
        }, 2000);
    }
    
    // عرض رسائل للمستخدم
    function showMessage(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="إغلاق"></button>
        `;
        
        installationProgress.appendChild(alertDiv);
    }
    
    // أحداث النقر على الأزرار
    checkSystemBtn.addEventListener('click', simulateSystemCheck);
    setupDatabaseBtn.addEventListener('click', simulateDatabaseSetup);
    
    // التحقق من صحة نموذج إنشاء المسؤول
    adminForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const email = document.getElementById('admin-email').value;
        const password = document.getElementById('admin-password').value;
        const confirmPassword = document.getElementById('admin-password-confirm').value;
        
        // التحقق من صحة البريد الإلكتروني
        if (!email || !email.includes('@')) {
            showMessage('يرجى إدخال بريد إلكتروني صحيح.', 'danger');
            return;
        }
        
        // التحقق من صحة كلمة المرور
        if (!password || password.length < 8) {
            showMessage('يجب أن تتكون كلمة المرور من 8 أحرف على الأقل.', 'danger');
            return;
        }
        
        // التحقق من تطابق كلمات المرور
        if (password !== confirmPassword) {
            showMessage('كلمات المرور غير متطابقة.', 'danger');
            return;
        }
        
        // محاكاة إنشاء الحساب
        showMessage('جاري إنشاء حساب المسؤول...', 'info');
        
        setTimeout(() => {
            showMessage('تم إنشاء حساب المسؤول بنجاح!', 'success');
        }, 1500);
    });
    
    // تهيئة المهام عند بدء التشغيل
    renderTasks();
});