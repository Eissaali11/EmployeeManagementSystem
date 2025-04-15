/**
 * Main JavaScript for Arabic Employee Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize DataTables if they exist
    if (typeof $.fn.DataTable !== 'undefined') {
        initializeDataTables();
    }

    // Initialize counter animations for dashboard
    animateCounters();

    // Initialize department charts if they exist
    initializeDepartmentCharts();

    // Add event listeners for document expiry date validation
    setupExpiryDateValidation();

    // Set up confirmation dialogs for delete actions
    setupDeleteConfirmations();

    // Initialize calendar toggling between Hijri and Gregorian
    setupCalendarToggle();
});

/**
 * Initialize DataTables with common configurations
 */
function initializeDataTables() {
    $('.datatable').each(function() {
        $(this).DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/ar.json'
            },
            responsive: true,
            dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>' +
                 '<"row"<"col-sm-12"tr>>' +
                 '<"row"<"col-sm-5"i><"col-sm-7"p>>',
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "الكل"]],
            order: []  // Disable initial sorting
        });
    });

    // Special configuration for employee table
    $('#employeesTable').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/ar.json'
        },
        responsive: true,
        columnDefs: [
            { orderable: false, targets: -1 } // Disable sorting on action column
        ],
        dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>' +
             '<"row"<"col-sm-12"tr>>' +
             '<"row"<"col-sm-5"i><"col-sm-7"p>>',
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "الكل"]],
    });
}

/**
 * Animate counter elements on dashboard
 */
function animateCounters() {
    const counters = document.querySelectorAll('.counter-value');
    const speed = 200;  // The lower the faster

    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        const increment = target / speed;
        
        let count = 0;
        const updateCount = () => {
            count += increment;
            
            if (count < target) {
                counter.innerText = Math.ceil(count);
                setTimeout(updateCount, 1);
            } else {
                counter.innerText = target;
            }
        };
        
        updateCount();
    });
}

/**
 * Initialize Charts.js charts for departments visualization
 */
function initializeDepartmentCharts() {
    // Department distribution chart
    const deptChartElement = document.getElementById('departmentChart');
    if (deptChartElement) {
        const labels = JSON.parse(deptChartElement.getAttribute('data-labels') || '[]');
        const data = JSON.parse(deptChartElement.getAttribute('data-values') || '[]');
        
        new Chart(deptChartElement, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(201, 203, 207, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'توزيع الموظفين حسب الأقسام',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }

    // Salary distribution chart
    const salaryChartElement = document.getElementById('salaryChart');
    if (salaryChartElement) {
        const labels = JSON.parse(salaryChartElement.getAttribute('data-labels') || '[]');
        const data = JSON.parse(salaryChartElement.getAttribute('data-values') || '[]');
        
        new Chart(salaryChartElement, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'إجمالي الرواتب',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'إجمالي الرواتب الشهرية',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
}

/**
 * Setup validation for document expiry dates
 */
function setupExpiryDateValidation() {
    const issueDateInput = document.getElementById('issue_date');
    const expiryDateInput = document.getElementById('expiry_date');
    
    if (issueDateInput && expiryDateInput) {
        expiryDateInput.addEventListener('change', function() {
            const issueDate = new Date(issueDateInput.value);
            const expiryDate = new Date(expiryDateInput.value);
            
            if (expiryDate <= issueDate) {
                alert('تاريخ الانتهاء يجب أن يكون بعد تاريخ الإصدار');
                expiryDateInput.value = '';
            }
        });
    }
}

/**
 * Setup confirmation dialogs for delete actions
 */
function setupDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('هل أنت متأكد من حذف هذا العنصر؟ لا يمكن التراجع عن هذا الإجراء.')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Handle toggle between Hijri and Gregorian calendar views
 */
function setupCalendarToggle() {
    const calendarToggle = document.getElementById('calendarToggle');
    
    if (calendarToggle) {
        calendarToggle.addEventListener('change', function() {
            const hijriElements = document.querySelectorAll('.hijri-date');
            const gregorianElements = document.querySelectorAll('.gregorian-date');
            
            if (this.checked) {
                // Show Hijri dates
                hijriElements.forEach(el => el.style.display = 'inline-block');
                gregorianElements.forEach(el => el.style.display = 'none');
            } else {
                // Show Gregorian dates
                hijriElements.forEach(el => el.style.display = 'none');
                gregorianElements.forEach(el => el.style.display = 'inline-block');
            }
        });
    }
}

/**
 * Calculate net salary based on form inputs
 */
function calculateNetSalary() {
    const basicSalary = parseFloat(document.getElementById('basic_salary').value) || 0;
    const allowances = parseFloat(document.getElementById('allowances').value) || 0;
    const deductions = parseFloat(document.getElementById('deductions').value) || 0;
    const bonus = parseFloat(document.getElementById('bonus').value) || 0;
    
    const netSalary = basicSalary + allowances + bonus - deductions;
    
    // Display the calculated net salary
    const netSalaryDisplay = document.getElementById('net_salary_display');
    if (netSalaryDisplay) {
        netSalaryDisplay.textContent = netSalary.toFixed(2);
    }
}

/**
 * Filter employees by department 
 */
function filterEmployeesByDepartment(departmentId) {
    const employeeSelect = document.getElementById('employee_id');
    
    if (employeeSelect) {
        // Get all employees
        const allEmployees = JSON.parse(employeeSelect.getAttribute('data-employees') || '[]');
        
        // Clear current options
        employeeSelect.innerHTML = '<option value="">اختر الموظف</option>';
        
        // Filter and add options
        const filteredEmployees = departmentId ? 
            allEmployees.filter(emp => emp.department_id === parseInt(departmentId)) :
            allEmployees;
        
        filteredEmployees.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = emp.name;
            employeeSelect.appendChild(option);
        });
    }
}

/**
 * Set attendance status for all employees in a department
 */
function setDepartmentAttendance(status) {
    const statusInput = document.getElementById('status');
    if (statusInput) {
        statusInput.value = status;
    }
    
    // Update UI to show selected status
    document.querySelectorAll('.attendance-status-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`.attendance-status-btn[data-status="${status}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

/**
 * Export data table to Excel format
 */
function exportTableToExcel(tableId, filename = '') {
    const table = document.getElementById(tableId);
    const wb = XLSX.utils.table_to_book(table, {sheet: "Sheet1"});
    
    XLSX.writeFile(wb, filename + '.xlsx');
}

/**
 * Handle file input validation for Excel imports
 */
function validateExcelFile(inputElement) {
    const fileInput = document.getElementById(inputElement);
    const filePath = fileInput.value;
    const allowedExtensions = /(\.xlsx|\.xls)$/i;
    
    if (!allowedExtensions.exec(filePath)) {
        alert('الرجاء اختيار ملف Excel صالح (.xlsx, .xls)');
        fileInput.value = '';
        return false;
    }
    
    return true;
}
