// Utility Functions
function formatNumber(number, decimals = 1) {
    return Number(number).toFixed(decimals);
}

function formatDateTime(dateString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Alert Management
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const mainContent = document.querySelector('main');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertDiv);
        alert.close();
    }, 5000);
}

// Form Validation
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            
            // Create or update feedback message
            let feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
            feedback.textContent = `${field.getAttribute('placeholder') || 'This field'} is required`;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Dynamic Chart Colors
function getChartColors(count) {
    const colors = [
        'rgba(54, 162, 235, 0.5)',   // blue
        'rgba(255, 99, 132, 0.5)',   // red
        'rgba(75, 192, 192, 0.5)',   // green
        'rgba(255, 159, 64, 0.5)',   // orange
        'rgba(153, 102, 255, 0.5)',  // purple
        'rgba(255, 205, 86, 0.5)',   // yellow
        'rgba(201, 203, 207, 0.5)'   // grey
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

// Chart Utilities
function createBarChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: getChartColors(data.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                ...options
            }
        }
    });
}

// Data Table Utilities
function initializeDataTable(tableId, options = {}) {
    return new DataTable(`#${tableId}`, {
        pageLength: 10,
        responsive: true,
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf'],
        ...options
    });
}

// Event Handlers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Initialize popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
    
    // Clean up invalid state on input
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const feedback = this.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.remove();
            }
        });
    });
});

// Export utilities for use in other scripts
window.utils = {
    formatNumber,
    formatDateTime,
    showAlert,
    validateForm,
    getChartColors,
    createBarChart,
    initializeDataTable
}; 