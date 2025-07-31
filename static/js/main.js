// Max Electric - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initializeAnimations();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize smooth scrolling
    initializeSmoothScrolling();
    
    // Initialize loading states
    initializeLoadingStates();
});

// Initialize animations
function initializeAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all service cards and quick action cards
    document.querySelectorAll('.service-card, .quick-action-card, .summary-card').forEach(card => {
        observer.observe(card);
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize smooth scrolling
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize loading states
function initializeLoadingStates() {
    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds (fallback)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Energy meter animation
function animateEnergyMeter() {
    const energyBars = document.querySelectorAll('.energy-bar');
    energyBars.forEach(bar => {
        bar.style.animation = 'none';
        setTimeout(() => {
            bar.style.animation = 'energyFlow 3s ease-in-out infinite';
        }, 100);
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Validate form fields
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });
    
    return isValid;
}

// Handle AJAX requests
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Add loading overlay
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    overlay.style.cssText = 'background: rgba(255, 255, 255, 0.9); z-index: 9999;';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted">Loading...</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Initialize page-specific functionality
function initializePageSpecific() {
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('dashboard')) {
        initializeDashboard();
    } else if (currentPage.includes('login')) {
        initializeLogin();
    }
}

// Dashboard specific initialization
function initializeDashboard() {
    // Auto-refresh balance every 30 seconds
    setInterval(() => {
        const refreshBtn = document.querySelector('button[onclick="refreshBalance()"]');
        if (refreshBtn && !refreshBtn.disabled) {
            refreshBalance();
        }
    }, 30000);
    
    // Initialize chart animations
    setTimeout(() => {
        animateEnergyMeter();
    }, 1000);
}

// Login specific initialization
function initializeLogin() {
    // Focus on first input
    const firstInput = document.querySelector('input[type="text"]');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Handle demo account buttons
    document.querySelectorAll('.demo-fill').forEach(button => {
        button.addEventListener('click', function() {
            showNotification('Demo account information filled!', 'success');
        });
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

// Initialize page-specific functionality when DOM is ready
document.addEventListener('DOMContentLoaded', initializePageSpecific);

// Export functions for use in other scripts
window.MaxElectric = {
    showNotification,
    formatCurrency,
    validateForm,
    makeRequest,
    showLoadingOverlay,
    hideLoadingOverlay
}; 