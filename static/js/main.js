// Main JavaScript for Smart Task Management System

$(document).ready(function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Handle task status change via AJAX
    $('.status-select').on('change', function() {
        const taskId = $(this).data('task-id');
        const newStatus = $(this).val();
        const selectElement = $(this);
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Show loading state
        selectElement.prop('disabled', true);
        
        $.ajax({
            url: `/tasks/${taskId}/toggle-status/`,
            type: 'POST',
            data: {
                'status': newStatus,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                if (response.success) {
                    // Show success message
                    showNotification('Task status updated successfully!', 'success');
                    
                    // Update the row styling based on status
                    const row = selectElement.closest('tr');
                    row.addClass('table-success');
                    setTimeout(function() {
                        row.removeClass('table-success');
                    }, 2000);
                } else {
                    showNotification('Failed to update task status.', 'danger');
                    // Revert the select to previous value
                    selectElement.val(selectElement.data('previous-value'));
                }
            },
            error: function() {
                showNotification('An error occurred. Please try again.', 'danger');
                // Revert the select to previous value
                selectElement.val(selectElement.data('previous-value'));
            },
            complete: function() {
                selectElement.prop('disabled', false);
            }
        });
        
        // Store the current value as previous value
        selectElement.data('previous-value', newStatus);
    });
    
    // Store initial values for status selects
    $('.status-select').each(function() {
        $(this).data('previous-value', $(this).val());
    });
    
    // Confirm delete actions
    $('a[href*="delete"]').on('click', function(e) {
        if (!$(this).closest('form').length && !confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
    
    // Add tooltips to buttons
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Filter form auto-submit on change (optional)
    $('.auto-submit').on('change', function() {
        $(this).closest('form').submit();
    });
});

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to show notification
function showNotification(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
             role="alert" style="z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('body').append(alertHtml);
    
    // Auto-hide after 3 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 3000);
}

// Function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Function to check if task is overdue
function isOverdue(deadline) {
    return new Date(deadline) < new Date();
}

// Add active class to current nav item
$(document).ready(function() {
    const currentPath = window.location.pathname;
    $('.navbar-nav .nav-link').each(function() {
        const href = $(this).attr('href');
        if (currentPath.startsWith(href) && href !== '/') {
            $(this).addClass('active');
        }
    });
});

