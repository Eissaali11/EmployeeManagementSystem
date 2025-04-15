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
                url: 'https://cdn.datatables.net/plug-ins/1.10.25/i18n/ar.json'
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
    var employeeTable = $('#employeesTable');
    if (employeeTable.length > 0) {
        employeeTable.DataTable({
            language: {
                search: "بحث:",
                lengthMenu: "عرض _MENU_ سجلات",
                info: "عرض _START_ إلى _END_ من _TOTAL_ سجل",
                paginate: {
                    first: "الأول",
                    previous: "السابق",
                    next: "التالي",
                    last: "الأخير"
                }
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
    // Check if the department chart element exists
    const departmentChartEl = document.getElementById('departmentEmployeeChart');
    if (departmentChartEl) {
        try {
            // Get departments data from the data attribute
            const departmentsDataStr = departmentChartEl.getAttribute('data-departments') || '[]';
            const departmentsData = JSON.parse(departmentsDataStr);
            
            // Prepare chart data
            const labels = departmentsData.map(dept => dept.name);
            const employeeCounts = departmentsData.map(dept => dept.employee_count);
            
            // Create chart
            new Chart(departmentChartEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'عدد الموظفين',
                        data: employeeCounts,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            precision: 0
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'توزيع الموظفين حسب الأقسام'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing department chart:', error);
        }
    }
    
    // Department distribution chart
    const deptChartElement = document.getElementById('departmentChart');
    if (deptChartElement) {
        let labels = [];
        let data = [];
        
        try {
            // Safely parse JSON or use empty array as fallback
            const labelsAttr = deptChartElement.getAttribute('data-labels') || '[]';
            const dataAttr = deptChartElement.getAttribute('data-values') || '[]';
            
            labels = JSON.parse(labelsAttr);
            data = JSON.parse(dataAttr);
        } catch (error) {
            console.error('Error parsing chart data:', error);
            // Keep default empty arrays
        }
        
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
        let labels = [];
        let data = [];
        
        try {
            // Safely parse JSON or use empty array as fallback
            const labelsAttr = salaryChartElement.getAttribute('data-labels') || '[]';
            const dataAttr = salaryChartElement.getAttribute('data-values') || '[]';
            
            labels = JSON.parse(labelsAttr);
            data = JSON.parse(dataAttr);
        } catch (error) {
            console.error('Error parsing salary chart data:', error);
            // Keep default empty arrays
        }
        
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
        let allEmployees = [];
        try {
            const employeesData = employeeSelect.getAttribute('data-employees') || '[]';
            allEmployees = JSON.parse(employeesData);
        } catch (error) {
            console.error('Error parsing employee data:', error);
            // Keep default empty array
        }
        
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