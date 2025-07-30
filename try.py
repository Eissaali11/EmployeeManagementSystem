{% extends 'layout.html' %}

{% block title %}
    {% if force_mode == 'return' %}
        نموذج استلام مركبة - {{ vehicle.plate_number }}
    {% else %}
        نموذج تسليم مركبة - {{ vehicle.plate_number }}
    {% endif %}
{% endblock %}

{% block styles %}
    {{ super() }}
   

<style>

        .signature-pad-container { border: 1px dashed #ced4da; cursor: crosshair; background-color: #f8f9fa; height: 150px; width: 100%; border-radius: .375rem; }
        .signature-pad-container canvas { display: block; }
        @media (min-width: 1200px){ .container, .container-lg, .container-md, .container-sm, .container-xl { max-width: 1400px; }}
        .form-check { padding-right: 2.5em; }
        .form-check .form-check-input { float: right; margin-right: -2.5em; }
        .form-switch.form-check { padding-right: 3.5em; }
        .form-switch.form-check .form-check-input { margin-right: -3.5em; }

        /* ===== ستايل جديد لجعل الحقول المعطلة أكثر وضوحاً ===== */
        .form-control:disabled, .form-select:disabled {
            background-color: #e9ecef;
            opacity: 1;
            cursor: not-allowed;
        }
    </style>
{% endblock %}

{% block content %}
<div class="container-fluid mt-4 mb-5">
    <div class="card shadow-sm">
        <div class="card-header d-flex justify-content-between align-items-center py-3">
            <h3 class="mb-0" id="form-main-title">
                <i class="fas fa-file-alt me-2 text-primary"></i>
                {% if force_mode == 'return' %}
                    نموذج استلام: <span class="text-dark">{{ vehicle.plate_number }}</span>
                {% else %}
                    نموذج تسليم: <span class="text-dark">{{ vehicle.plate_number }}</span>
                {% endif %}
            </h3>
            <div>
                <a href="{{ url_for('vehicles.view', id=vehicle.id) }}" class="btn btn-outline-primary btn-sm"><i class="fas fa-car me-1"></i> عرض السيارة</a>
                <a href="{{ url_for('vehicles.index') }}" class="btn btn-outline-secondary btn-sm"><i class="fas fa-arrow-left me-1"></i> العودة للقائمة</a>
            </div>
        </div>

        <div class="card-body p-lg-4">
            <form method="post" action="{{ url_for('vehicles.create_handover', id=vehicle.id) }}" enctype="multipart/form-data" id="main-handover-form">

                {# ================ تعديل 1: عرض الرسالة التوجيهية ================ #}
                {% if info_message %}
                <div class="alert alert-info border-0 shadow-sm" role="alert">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-info-circle fa-2x me-3"></i>
                        <div>
                            <h5 class="alert-heading mb-1">ملاحظة هامة!</h5>
                            {{ info_message }}
                        </div>
                    </div>
                </div>
                {% endif %}

                <div class="row">
                    <!-- عمود معلومات السيارة (يبقى كما هو) -->
                    <div class="col-lg-4 mb-4">
                        <div class="card sticky-top" style="top: 20px;">
                           <!-- ... نفس كود معلومات السيارة ... -->
                           <div class="card-header"><h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>معلومات السيارة</h5></div>
                           <ul class="list-group list-group-flush">
                               <li class="list-group-item d-flex justify-content-between"><strong>رقم اللوحة:</strong> <span>{{ vehicle.plate_number }}</span></li>
                               <li class="list-group-item d-flex justify-content-between"><strong>النوع:</strong> <span>{{ vehicle.make }} {{ vehicle.model }}</span></li>
                               <li class="list-group-item d-flex justify-content-between"><strong>السنة:</strong> <span>{{ vehicle.year }}</span></li>
                               <li class="list-group-item d-flex justify-content-between"><strong>الحالة:</strong>
                                   <span>
                                       {% if vehicle.status == 'available' %} <span class="badge bg-success">متاحة</span>
                                       {% elif vehicle.status == 'in_project' %} <span class="badge bg-info">في المشروع</span>
                                       {% elif vehicle.status == 'in_workshop' %} <span class="badge bg-warning text-dark">في الورشة</span>
                                       {% else %} <span class="badge bg-secondary">{{ vehicle.status }}</span> {% endif %}
                                   </span>
                               </li>
                           </ul>
                        </div>
                    </div>

                    <!-- عمود النموذج الرئيسي -->
                    <div class="col-lg-8">

                        <!-- القسم 1: المعلومات الأساسية -->
                        <h4 class="mb-3 border-bottom pb-1">المعلومات الأساسية</h4>

                        <div class="row g-3 pb-3">
                            {# ================ تعديل 2: جعل "نوع العملية" ديناميكياً ================ #}
                            <div class="col-md-4">
                                <label for="handover_type" class="form-label required">نوع العملية</label>
                                <select class="form-select" id="handover_type" name="handover_type" required {% if force_mode %}disabled{% endif %}>
                                    <option value="delivery" {% if force_mode == 'delivery' %}selected{% endif %}>تسليم سيارة لسائق</option>
                                    <option value="return" {% if force_mode == 'return' %}selected{% endif %}>استلام سيارة من سائق</option>
                                </select>
                                {% if force_mode %}
                                    {# حقل مخفي لإرسال القيمة لأن الحقول المعطلة لا تُرسل #}
                                    <input type="hidden" name="handover_type" value="{{ force_mode }}" />
                                {% endif %}
                            </div>

                            <!-- باقي الحقول في قسم المعلومات الأساسية تبقى كما هي -->
                            <div class="col-md-4">
                                <label for="handover_date" class="form-label required">التاريخ</label>
                                <input type="date" class="form-control" id="handover_date" name="handover_date" required>
                            </div>
                            <div class="col-md-4">
                                <label for="handover_time" class="form-label">الوقت (اختياري)</label>
                                <input type="time" class="form-control" id="handover_time" name="handover_time">
                            </div>
                             <!-- ... (باقي حقول المعلومات الأساسية مثل المشروع والعداد، إلخ) ... -->
                            <div class="col-md-6">
                                <label for="project_name" class="form-label">المشروع</label>
                                <input type="text" class="form-control" id="project_name" name="project_name" value="{{ vehicle.project or '' }}" placeholder="المشروع المرتبط بالعملية">
                            </div>
                            <div class="col-md-6">
                                <label for="city" class="form-label">المدينة</label>
                                <input type="text" class="form-control" id="city" name="city" value="" placeholder="المدينة التي تتم فيها العملية">
                            </div>
                            <div class="col-md-6">
                                <label for="mileage" class="form-label required">قراءة العداد (كم)</label>
                                <input type="number" class="form-control" id="mileage" name="mileage" min="0" required>
                            </div>
                            <div class="col-md-6">
                                <label for="fuel_level" class="form-label required">مستوى الوقود</label>
                                <select class="form-select" id="fuel_level" name="fuel_level" required>
                                    <option value="" disabled selected>-- اختر --</option>
                                    <option value="ممتلئ">ممتلئ (Full)</option>
                                    <option value="3/4">ثلاثة أرباع (3/4)</option>
                                    <option value="1/2">نصف (1/2)</option>
                                    <option value="1/4">ربع (1/4)</option>
                                    <option value="منخفض">فارغ (Empty)</option>
                                </select>
                            </div>

                        </div>

                        {# ================ تعديل 3: جعل قسم "السائق" ديناميكياً ================ #}
                        <div class="card border mb-4">
                            <div class="card-header "><h5 class="mb-0">السائق</h5></div>
                            <div class="card-body">
                                {% if force_mode == 'return' and current_driver_info %}
                                    <!-- **الحالة أ: عرض بيانات السائق الحالي (في وضع الاستلام)** -->
                                    <div class="mb-3">
                                        <label class="form-label">الاسم</label>
                                        <input type="text" class="form-control" value="{{ current_driver_info.person_name }}" readonly disabled>
                                        <div class="form-text text-primary">
                                            يتم استلام السيارة من السائق الحالي. لا يمكن تغيير هذه البيانات.
                                        </div>
                                        {# حقول مخفية مهمة لإرسال بيانات السائق الصحيحة مع النموذج #}
                                        <input type="hidden" id="person_name" name="person_name" value="{{ current_driver_info.person_name }}">
                                        <input type="hidden" id="employee_id" name="employee_id" value="{{ current_driver_info.employee_id or '' }}">
                                    </div>
                                {% else %}
                                    <!-- **الحالة ب: عرض نموذج البحث العادي (في وضع التسليم)** -->
                                    <div class="mb-3">
                                        <label for="person_name" class="form-label required">الاسم</label>
                                        <input type="text" class="form-control" id="person_name" name="person_name" required autocomplete="off" placeholder="اكتب الاسم أو اختر موظف من القائمة أدناه">
                                        <input type="hidden" id="employee_id" name="employee_id">
                                    </div>
                                    <div class="accordion" id="employeeSearchAccordion">
                                        <!-- ... كل كود الأكورديون وجدول البحث يبقى كما هو ... -->
                                        <div class="accordion-item">
                                            <h2 class="accordion-header"><button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#collapseEmployeeSearch">بحث عن السائق</button></h2>
                                            <div id="collapseEmployeeSearch" class="accordion-collapse collapse" data-bs-parent="#employeeSearchAccordion">
                                                <div class="accordion-body">
                                                     <!-- ... أدوات البحث والجدول ... -->
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                {% endif %}
                            </div>
                        </div>

                        <!-- قسم بيانات المشرف يبقى كما هو -->
                        <div class="card border mb-4">
                           <!-- ... نفس كود قسم المشرف ... -->
                        </div>

                        <!-- كل الأقسام الأخرى (فحص السيارة، الهيكل، التوثيق، التواقيع) تبقى كما هي -->
                        <!-- ... -->

                        <!-- زر الحفظ النهائي (يبقى كما هو) -->
                        <div class="d-grid gap-2 pt-4 mt-4 border-top">
                            <button type="submit" class="btn btn-primary btn-lg"><i class="fas fa-save me-2"></i>حفظ وإنشاء التقرير</button>
                        </div>

                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
    {{ super() }}
    <!-- كل ملفات الجافا سكربت والسكربتات الداخلية تبقى كما هي -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            // كود تهيئة لوحة الرسم... (يبقى كما هو)
            // كود التواقيع... (يبقى كما هو)

            // ===== تعديل بسيط على الجافا سكربت لضبط التاريخ والوقت الحاليين =====
            const dateInput = document.getElementById('handover_date');
            if (dateInput && !dateInput.value) { // لا يغير القيمة إذا كانت موجودة
                dateInput.value = new Date().toISOString().split('T')[0];
            }
            const timeInput = document.getElementById('handover_time');
            if (timeInput && !timeInput.value) {
                timeInput.value = new Date().toTimeString().split(' ')[0].substring(0, 5);
            }
        });

        // كود البحث عن الموظفين... (يبقى كما هو)
        // كود إدارة رفع الملفات... (يبقى كما هو)
    </script>
{% endblock %}