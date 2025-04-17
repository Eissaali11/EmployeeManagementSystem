/**
 * نظام احتساب الرسوم الحكومية
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('صفحة احتساب الرسوم الحكومية محملة');
    
    // الدوال المساعدة
    function formatCurrency(amount) {
        return amount.toLocaleString('ar-SA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    
    // تحميل مكتبة SheetJS للتصدير بصيغة إكسل
    function loadXLSXScript() {
        console.log('جاري تحميل مكتبة SheetJS...');
        if (!document.getElementById('sheetjs-script')) {
            const script = document.createElement('script');
            script.id = 'sheetjs-script';
            script.src = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
            script.onload = function() {
                console.log('تم تحميل مكتبة SheetJS بنجاح');
            };
            document.head.appendChild(script);
        } else {
            console.log('مكتبة SheetJS محملة مسبقًا');
        }
    }
    
    // إنشاء ملف إكسل
    function generateExcelFile(data) {
        if (!window.XLSX) {
            alert('جاري تحميل مكتبة الإكسل، يرجى المحاولة مرة أخرى بعد قليل');
            loadXLSXScript();
            return;
        }
        
        console.log('بدء إنشاء ملف الإكسل', data);
        
        // إنشاء مصفوفة للبيانات
        const rows = [
            ['بيانات احتساب الرسوم الحكومية', '', '', '', ''],
            ['', '', '', '', ''],
            ['اسم الموظف:', data.employeeName, '', 'الرقم الوظيفي:', data.employeeId],
            ['نوع العقد:', data.contractType, '', 'التوازن الوطني:', data.hasNationalBalance ? 'نعم' : 'لا'],
            ['الراتب الأساسي:', data.basicSalary.toLocaleString('ar-SA') + ' ريال', '', 'تاريخ الاحتساب:', data.calculationDate],
            ['الرسوم المحتسبة:', data.amount.toLocaleString('ar-SA') + ' ريال', '', 'الفترة:', data.periodName],
            ['', '', '', '', ''],
            ['تفاصيل الرسوم:', '', '', '', '']
        ];
        
        // إضافة أنواع الرسوم
        data.feeTypes.forEach(feeDesc => {
            rows.push(['- ' + feeDesc, '', '', '', '']);
        });
        
        // إضافة ملاحظات
        rows.push(['', '', '', '', '']);
        rows.push(['ملاحظات:', '', '', '', '']);
        rows.push(['- تم احتساب الرسوم بناءً على بيانات الموظف والخيارات المحددة.', '', '', '', '']);
        
        // إنشاء ورقة عمل
        const ws = XLSX.utils.aoa_to_sheet(rows);
        
        // تنسيق الخلايا
        ws['!cols'] = [
            { wch: 30 }, // العمود الأول
            { wch: 20 }, // العمود الثاني
            { wch: 10 }, // العمود الثالث
            { wch: 20 }, // العمود الرابع
            { wch: 20 }, // العمود الخامس
        ];
        
        // إنشاء مصنف عمل
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'الرسوم الحكومية');
        
        // حفظ الملف
        const fileName = `الرسوم_الحكومية_${data.employeeName.replace(/\s+/g, '_')}_${data.calculationDate}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        console.log('تم إنشاء ملف الإكسل بنجاح', fileName);
    }
    
    // الحصول على قائمة الموظفين
    async function loadEmployees() {
        console.log('جاري تحميل بيانات الموظفين...');
        try {
            const response = await fetch('/api/employees');
            const data = await response.json();
            console.log(`تم تحميل ${data.length} موظف`);
            
            const employeeSelect = document.getElementById('employee_id');
            if (!employeeSelect) {
                console.error('لم يتم العثور على حقل اختيار الموظف (employee_id)');
                return;
            }
            
            employeeSelect.innerHTML = '<option value="" selected disabled>اختر الموظف</option>';
            
            data.forEach(employee => {
                const option = document.createElement('option');
                option.value = employee.id;
                option.textContent = `${employee.name} (${employee.employee_id})`;
                option.dataset.contract_type = employee.contract_type || 'foreign';
                option.dataset.nationality = employee.nationality || 'غير محدد';
                option.dataset.basic_salary = employee.basic_salary || 0;
                option.dataset.national_balance = employee.has_national_balance ? 'نعم' : 'لا';
                employeeSelect.appendChild(option);
            });
            
            // معالجة تغيير الموظف
            employeeSelect.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                
                if (selectedOption.value) {
                    console.log(`تم اختيار الموظف: ${selectedOption.textContent}`);
                    const employeeInfo = document.getElementById('employee_info');
                    employeeInfo.innerHTML = `
                        <strong>نوع العقد:</strong> ${selectedOption.dataset.contract_type === 'saudi' ? 'سعودي' : 'وافد'}<br>
                        <strong>الجنسية:</strong> ${selectedOption.dataset.nationality}<br>
                        <strong>الراتب الأساسي:</strong> ${formatCurrency(parseFloat(selectedOption.dataset.basic_salary))} ريال<br>
                        <strong>التوازن الوطني:</strong> ${selectedOption.dataset.national_balance}
                    `;
                    
                    // تحديث حالة التوازن الوطني تلقائيًا
                    const hasNationalBalance = selectedOption.dataset.national_balance === 'نعم';
                    const balanceCheckbox = document.getElementById('has_national_balance');
                    if (balanceCheckbox) {
                        balanceCheckbox.checked = hasNationalBalance;
                    }
                }
            });
            
        } catch (error) {
            console.error('خطأ في تحميل بيانات الموظفين:', error);
            // تهيئة بعض البيانات الافتراضية للعرض
            const employeeSelect = document.getElementById('employee_id');
            if (!employeeSelect) {
                console.error('لم يتم العثور على حقل اختيار الموظف (employee_id)');
                return;
            }
            
            employeeSelect.innerHTML = `
                <option value="" selected disabled>اختر الموظف</option>
                <option value="1" data-contract_type="foreign" data-nationality="مصري" data-basic_salary="5000" data-national_balance="لا">أحمد محمد (EMP001)</option>
                <option value="2" data-contract_type="saudi" data-nationality="سعودي" data-basic_salary="7500" data-national_balance="نعم">محمد العتيبي (EMP002)</option>
                <option value="3" data-contract_type="foreign" data-nationality="هندي" data-basic_salary="4500" data-national_balance="لا">راجيش كومار (EMP003)</option>
            `;
            
            // إضافة معالج الحدث
            employeeSelect.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                
                if (selectedOption.value) {
                    console.log(`تم اختيار الموظف: ${selectedOption.textContent}`);
                    const employeeInfo = document.getElementById('employee_info');
                    employeeInfo.innerHTML = `
                        <strong>نوع العقد:</strong> ${selectedOption.dataset.contract_type === 'saudi' ? 'سعودي' : 'وافد'}<br>
                        <strong>الجنسية:</strong> ${selectedOption.dataset.nationality}<br>
                        <strong>الراتب الأساسي:</strong> ${formatCurrency(parseFloat(selectedOption.dataset.basic_salary))} ريال<br>
                        <strong>التوازن الوطني:</strong> ${selectedOption.dataset.national_balance}
                    `;
                    
                    // تحديث حالة التوازن الوطني تلقائيًا
                    const hasNationalBalance = selectedOption.dataset.national_balance === 'نعم';
                    const balanceCheckbox = document.getElementById('has_national_balance');
                    if (balanceCheckbox) {
                        balanceCheckbox.checked = hasNationalBalance;
                    }
                }
            });
        }
    }
    
    // تهيئة معالجات الأحداث للعناصر في الصفحة
    function initializeEvents() {
        // معالجة الرسوم الأخرى
        const includeOtherCheckbox = document.getElementById('include_other');
        const otherFeeInputs = document.querySelector('.other-fee-inputs');
        
        if (includeOtherCheckbox && otherFeeInputs) {
            includeOtherCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    otherFeeInputs.classList.remove('d-none');
                } else {
                    otherFeeInputs.classList.add('d-none');
                }
            });
        }
        
        // معالجة تغيير حالة السداد
        const paymentStatusSelect = document.getElementById('payment_status');
        const paymentDetailsElements = document.querySelectorAll('.payment-details');
        
        if (paymentStatusSelect && paymentDetailsElements.length > 0) {
            paymentStatusSelect.addEventListener('change', function() {
                if (this.value === 'paid') {
                    paymentDetailsElements.forEach(element => {
                        element.classList.remove('d-none');
                    });
                    
                    // تعيين تاريخ السداد بتاريخ اليوم
                    const today = new Date().toISOString().split('T')[0];
                    const paymentDateField = document.getElementById('payment_date');
                    if (paymentDateField) {
                        paymentDateField.value = today;
                    }
                } else {
                    paymentDetailsElements.forEach(element => {
                        element.classList.add('d-none');
                    });
                }
            });
        }
        
        // تعيين سلوك للنموذج
        const form = document.getElementById('government-fee-form');
        if (form) {
            form.addEventListener('submit', function(event) {
                if (!document.getElementById('amount').value || parseFloat(document.getElementById('amount').value) <= 0) {
                    event.preventDefault();
                    alert('يرجى احتساب الرسوم أولاً قبل الحفظ');
                }
            });
        }
        
        // معالجة تنزيل ملف الإكسل
        const downloadExcelButton = document.getElementById('download-excel-button');
        if (downloadExcelButton) {
            downloadExcelButton.addEventListener('click', function() {
                if (!window.calculatedFeeData) {
                    alert('يرجى احتساب الرسوم أولاً قبل تنزيل البيانات');
                    return;
                }
                
                // إنشاء ملف إكسل باستخدام SheetJS
                generateExcelFile(window.calculatedFeeData);
            });
        }
        
        // معالجة احتساب الرسوم
        const calculateButton = document.getElementById('calculate-button');
        if (calculateButton) {
            calculateButton.addEventListener('click', calculateFees);
            console.log('تم تسجيل معالج النقر على زر احتساب الرسوم');
        } else {
            console.error('لم يتم العثور على زر احتساب الرسوم');
        }
    }
    
    // دالة احتساب الرسوم
    function calculateFees() {
        console.log('تم استدعاء دالة احتساب الرسوم');
        
        const employeeSelect = document.getElementById('employee_id');
        if (!employeeSelect) {
            console.error('لم يتم العثور على حقل اختيار الموظف');
            alert('حدث خطأ في تحميل بيانات الموظفين');
            return;
        }
        
        const calculationPeriod = document.getElementById('calculation_period').value;
        console.log('فترة الاحتساب:', calculationPeriod);
        
        // التحقق من اختيار الموظف
        if (!employeeSelect.value) {
            alert('يرجى اختيار الموظف أولاً');
            return;
        }
        
        // الحصول على بيانات الموظف المحددة
        const selectedOption = employeeSelect.options[employeeSelect.selectedIndex];
        const contractType = selectedOption.dataset.contract_type;
        const basicSalary = parseFloat(selectedOption.dataset.basic_salary) || 0;
        const hasNationalBalance = document.getElementById('has_national_balance').checked;
        
        console.log('بيانات الموظف المختار:', {
            id: employeeSelect.value,
            name: selectedOption.textContent,
            contractType: contractType,
            basicSalary: basicSalary,
            hasNationalBalance: hasNationalBalance
        });
        
        // تعريف معاملات التحويل للفترات المختلفة
        const periodMultipliers = {
            'monthly': 1,
            'quarterly': 3,
            'semiannual': 6,
            'annual': 12
        };
        
        // للتأكد من أن المستخدم اختار خدمة واحدة على الأقل
        const feeCheckboxes = document.querySelectorAll('.fee-option-checkbox:checked');
        if (feeCheckboxes.length === 0) {
            alert('يرجى اختيار نوع رسوم واحد على الأقل');
            return;
        }
        
        // إجمالي المبلغ
        let totalAmount = 0;
        let feeTypeDisplay = '';
        let feeDescriptions = [];
        
        // 1. مكتب العمل (المقابل المالي)
        if (document.getElementById('include_labor_office').checked) {
            if (contractType === 'saudi') {
                // لا توجد رسوم مكتب عمل للسعوديين
                feeDescriptions.push('مكتب العمل: لا ينطبق على الموظفين السعوديين');
            } else {
                const monthlyFee = hasNationalBalance ? 700 : 800;
                const laborFee = monthlyFee * periodMultipliers[calculationPeriod];
                totalAmount += laborFee;
                
                feeDescriptions.push(
                    `مكتب العمل: ${formatCurrency(laborFee)} ريال (${hasNationalBalance ? 'مع التوازن الوطني' : 'بدون التوازن الوطني'})`
                );
            }
        }
        
        // 2. الجوازات (الإقامة)
        if (document.getElementById('include_passport').checked) {
            if (contractType === 'saudi') {
                // لا توجد رسوم جوازات للسعوديين
                feeDescriptions.push('الجوازات: لا ينطبق على الموظفين السعوديين');
            } else {
                // رسوم الإقامة سنوية (650 ريال)
                const passportFee = (650 / 12) * periodMultipliers[calculationPeriod];
                totalAmount += passportFee;
                
                feeDescriptions.push(`الجوازات (الإقامة): ${formatCurrency(passportFee)} ريال`);
            }
        }
        
        // 3. التأمين الطبي
        if (document.getElementById('include_insurance').checked) {
            if (contractType === 'saudi') {
                feeDescriptions.push('التأمين الطبي: قد يختلف للموظفين السعوديين');
            } else {
                const insuranceLevel = document.querySelector('input[name="insurance_level"]:checked').value;
                let annualFee = 0;
                let insuranceType = '';
                
                switch (insuranceLevel) {
                    case 'basic':
                        annualFee = 400;
                        insuranceType = 'أساسي';
                        break;
                    case 'medium':
                        annualFee = 900;
                        insuranceType = 'متوسط';
                        break;
                    case 'high':
                        annualFee = 1500;
                        insuranceType = 'متميز';
                        break;
                }
                
                // التأمين سنوي
                const insuranceFee = (annualFee / 12) * periodMultipliers[calculationPeriod];
                totalAmount += insuranceFee;
                
                feeDescriptions.push(`التأمين الطبي (${insuranceType}): ${formatCurrency(insuranceFee)} ريال`);
            }
        }
        
        // 4. التأمينات الاجتماعية
        if (document.getElementById('include_social_insurance').checked) {
            let socialInsuranceFee = 0;
            
            if (contractType === 'saudi') {
                // 22% من الراتب الأساسي (12% على صاحب العمل و 10% على الموظف)
                socialInsuranceFee = (0.22 * basicSalary) * periodMultipliers[calculationPeriod];
                feeDescriptions.push(`التأمينات الاجتماعية: ${formatCurrency(socialInsuranceFee)} ريال (22% من الراتب الأساسي)`);
            } else {
                // 2% من الراتب الأساسي للوافدين
                socialInsuranceFee = (0.02 * basicSalary) * periodMultipliers[calculationPeriod];
                feeDescriptions.push(`التأمينات الاجتماعية: ${formatCurrency(socialInsuranceFee)} ريال (2% من الراتب الأساسي)`);
            }
            
            totalAmount += socialInsuranceFee;
        }
        
        // 5. رسوم أخرى (إذا تم اختيارها)
        if (document.getElementById('include_other').checked) {
            const otherFeeAmount = parseFloat(document.getElementById('other_fee_amount').value) || 0;
            const otherFeeDesc = document.getElementById('other_fee_description').value || 'رسوم أخرى';
            
            if (otherFeeAmount > 0) {
                totalAmount += otherFeeAmount;
                feeDescriptions.push(`${otherFeeDesc}: ${formatCurrency(otherFeeAmount)} ريال`);
            } else {
                alert('يرجى إدخال مبلغ الرسوم الأخرى');
                return;
            }
        }
        
        // تحديد نوع الرسوم المحدد للحقل المخفي
        let primaryFeeType = '';
        if (document.getElementById('include_labor_office').checked) {
            primaryFeeType = 'labor_office';
            feeTypeDisplay = 'مكتب العمل (المقابل المالي)';
        } else if (document.getElementById('include_passport').checked) {
            primaryFeeType = 'passport';
            feeTypeDisplay = 'الجوازات (الإقامة)';
        } else if (document.getElementById('include_insurance').checked) {
            primaryFeeType = 'insurance';
            feeTypeDisplay = 'التأمين الطبي';
        } else if (document.getElementById('include_social_insurance').checked) {
            primaryFeeType = 'social_insurance';
            feeTypeDisplay = 'التأمينات الاجتماعية';
        } else if (document.getElementById('include_other').checked) {
            primaryFeeType = 'other';
            feeTypeDisplay = 'رسوم أخرى';
        }
        
        // تعيين نوع الرسوم في الحقل المخفي
        document.getElementById('fee_type').value = primaryFeeType;
        
        // تحديث نتيجة الحساب
        const calculationResult = document.getElementById('calculation-result');
        const feeDetailsSection = document.getElementById('fee-details-section');
        
        document.getElementById('result-amount').textContent = formatCurrency(totalAmount) + ' ريال';
        document.getElementById('result-fee-type').textContent = feeDescriptions.length > 1 ? 'رسوم متعددة' : feeTypeDisplay;
        document.getElementById('result-employee').textContent = selectedOption.textContent;
        
        let periodText = '';
        switch (calculationPeriod) {
            case 'monthly': periodText = 'شهري'; break;
            case 'quarterly': periodText = 'ربع سنوي'; break;
            case 'semiannual': periodText = 'نصف سنوي'; break;
            case 'annual': periodText = 'سنوي'; break;
        }
        document.getElementById('result-period').textContent = periodText;
        
        // عرض/إخفاء حقل التوازن الوطني
        const detailNationalBalance = document.getElementById('detail-national-balance');
        if (detailNationalBalance) {
            if (document.getElementById('include_labor_office').checked && contractType !== 'saudi') {
                detailNationalBalance.style.display = 'flex';
                document.getElementById('result-national-balance').textContent = hasNationalBalance ? 'نعم' : 'لا';
            } else {
                detailNationalBalance.style.display = 'none';
            }
        }
        
        // تحديث حقل المبلغ المخفي
        document.getElementById('amount').value = totalAmount;
        
        // إظهار نتيجة الحساب وقسم تفاصيل الرسوم
        if (calculationResult) calculationResult.classList.remove('d-none');
        if (feeDetailsSection) feeDetailsSection.classList.remove('d-none');
        
        // إظهار زر تنزيل ملف الإكسل
        const downloadExcelRow = document.getElementById('download-excel-row');
        if (downloadExcelRow) downloadExcelRow.classList.remove('d-none');
        
        // تعيين تواريخ افتراضية
        const today = new Date();
        const dueDate = new Date();
        dueDate.setDate(today.getDate() + 30); // استحقاق بعد 30 يوم
        
        const feeDateField = document.getElementById('fee_date');
        const dueDateField = document.getElementById('due_date');
        
        if (feeDateField) feeDateField.value = today.toISOString().split('T')[0];
        if (dueDateField) dueDateField.value = dueDate.toISOString().split('T')[0];
        
        // حفظ البيانات المحسوبة في المتغيرات العامة لاستخدامها في تصدير ملف الإكسل
        window.calculatedFeeData = {
            employeeName: selectedOption.textContent,
            employeeId: selectedOption.value,
            contractType: contractType === 'saudi' ? 'سعودي' : 'وافد',
            feeTypes: feeDescriptions,
            feeTypeDisplay: feeTypeDisplay,
            feeTypeValue: primaryFeeType,
            periodName: periodText,
            periodValue: calculationPeriod,
            basicSalary: basicSalary,
            amount: totalAmount,
            hasNationalBalance: hasNationalBalance,
            calculationDate: new Date().toISOString().split('T')[0]
        };
        
        console.log('تم احتساب الرسوم بنجاح', {
            totalAmount: totalAmount,
            feeDescriptions: feeDescriptions
        });
    }
    
    // تهيئة الصفحة
    loadEmployees();
    loadXLSXScript();
    initializeEvents();
});