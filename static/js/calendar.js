/**
 * Calendar script for handling Hijri/Gregorian date conversion
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers with Hijri calendar support
    initializeDatePickers();
    
    // Set up calendar type toggle
    const calendarToggle = document.getElementById('calendarToggle');
    if (calendarToggle) {
        calendarToggle.addEventListener('change', toggleCalendarType);
    }
});

/**
 * Initialize date picker fields with dual calendar support
 */
function initializeDatePickers() {
    // Elements with date-picker class will have the dual calendar functionality
    const dateInputs = document.querySelectorAll('.date-picker');
    
    dateInputs.forEach(input => {
        // Create container for the dual date display
        const container = document.createElement('div');
        container.className = 'date-display mt-2';
        
        // Create elements to display dates in both calendars
        const gregorianDate = document.createElement('span');
        gregorianDate.className = 'gregorian-date';
        
        const hijriDate = document.createElement('span');
        hijriDate.className = 'hijri-date';
        hijriDate.style.display = 'none'; // Hide Hijri date initially
        
        // Add to container
        container.appendChild(gregorianDate);
        container.appendChild(hijriDate);
        
        // Insert after input
        input.parentNode.insertBefore(container, input.nextSibling);
        
        // Add event listener to update displays when date changes
        input.addEventListener('change', function() {
            updateDualDateDisplay(input, gregorianDate, hijriDate);
        });
        
        // Initialize with current value if any
        if (input.value) {
            updateDualDateDisplay(input, gregorianDate, hijriDate);
        }
    });
}

/**
 * Update the dual date display for a given input
 */
function updateDualDateDisplay(input, gregorianDisplay, hijriDisplay) {
    const dateValue = input.value;
    
    if (!dateValue) {
        gregorianDisplay.textContent = '';
        hijriDisplay.textContent = '';
        return;
    }
    
    try {
        // Format Gregorian date display
        const date = new Date(dateValue);
        const formattedGregorian = formatDate(date);
        gregorianDisplay.textContent = `ميلادي: ${formattedGregorian}`;
        
        // Convert to Hijri and format display
        const hijriDate = gregorianToHijri(date);
        hijriDisplay.textContent = `هجري: ${hijriDate.day}/${hijriDate.month}/${hijriDate.year} هـ`;
    } catch (e) {
        console.error('Error updating date display:', e);
    }
}

/**
 * Format date as DD/MM/YYYY
 */
function formatDate(date) {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}/${month}/${year}`;
}

/**
 * Toggle between Hijri and Gregorian calendar displays
 */
function toggleCalendarType() {
    const isHijri = this.checked;
    
    // Toggle visibility of date displays - استثناء عناصر جدول الحضور
    const hijriElements = document.querySelectorAll('.hijri-date:not(table .hijri-date)');
    const gregorianElements = document.querySelectorAll('.gregorian-date:not(table .gregorian-date)');
    
    hijriElements.forEach(el => {
        el.style.display = isHijri ? 'inline-block' : 'none';
    });
    
    gregorianElements.forEach(el => {
        el.style.display = isHijri ? 'none' : 'inline-block';
    });
    
    // Update calendar picker UI if using a calendar library
    updateCalendarPickerType(isHijri);
    
    // Store preference
    localStorage.setItem('calendarType', isHijri ? 'hijri' : 'gregorian');
}

/**
 * Update calendar picker type based on user preference
 * Note: Implementation depends on the specific calendar library being used
 */
function updateCalendarPickerType(isHijri) {
    // This is a placeholder - actual implementation depends on the calendar library
    console.log(`Calendar type set to ${isHijri ? 'Hijri' : 'Gregorian'}`);
}

/**
 * Convert Gregorian date to Hijri date
 * This is a simplified conversion for client-side display
 */
function gregorianToHijri(gregorianDate) {
    // This is a simplified conversion method
    // For production, use a library like hijri-converter on the server side
    // and return the values to the client
    
    const year = gregorianDate.getFullYear();
    const month = gregorianDate.getMonth() + 1;
    const day = gregorianDate.getDate();
    
    // Calculate Hijri date (approximate)
    // For proper implementation, use a proper Hijri conversion library
    const hijriYear = Math.floor((year - 622) * 32 / 33);
    const hijriMonth = ((month + 1) % 12) + 1;
    const hijriDay = day;
    
    return {
        year: hijriYear,
        month: hijriMonth,
        day: hijriDay
    };
}

/**
 * Convert Hijri date to Gregorian date
 * This is a simplified conversion for client-side display
 */
function hijriToGregorian(hijriYear, hijriMonth, hijriDay) {
    // This is a simplified conversion method
    // For production, use a library like hijri-converter on the server side
    
    // Calculate Gregorian date (approximate)
    // For proper implementation, use a proper Hijri conversion library
    const gregorianYear = Math.floor(hijriYear * 33 / 32) + 622;
    const gregorianMonth = ((hijriMonth - 1) % 12) + 1;
    const gregorianDay = hijriDay;
    
    return new Date(gregorianYear, gregorianMonth - 1, gregorianDay);
}

/**
 * Load user calendar preference from local storage
 */
function loadCalendarPreference() {
    const preference = localStorage.getItem('calendarType') || 'gregorian';
    const calendarToggle = document.getElementById('calendarToggle');
    
    if (calendarToggle) {
        calendarToggle.checked = preference === 'hijri';
        toggleCalendarType.call(calendarToggle);
    }
}
