
class PayrollCalculator {
    constructor() {
        this.init();
    }

    init() {
        this.cacheElements();
        this.bindEvents();
        this.initializeBenefits();
        this.initializeAnimations();
    }

    cacheElements() {
        this.elements = {
            form: document.getElementById('employeeForm'),
            benefitsContainer: document.getElementById('benefits-container'),
            benefitsData: document.getElementById('benefits-data'),
            addBenefitBtn: document.getElementById('add-benefit'),
            loadingOverlay: document.getElementById('loading-overlay'),
            messages: document.querySelector('.message-container'),
            submitBtn: document.querySelector('button[type="submit"]')
        };
    }

    bindEvents() {
        // Form events
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', this.handleSubmit.bind(this));
            this.elements.form.addEventListener('reset', this.handleReset.bind(this));
        }

        // Benefits events
        if (this.elements.addBenefitBtn) {
            this.elements.addBenefitBtn.addEventListener('click', this.addBenefitRow.bind(this));
        }

        // Message close events
        this.bindMessageEvents();

        // Input events
        this.bindInputEvents();

        // Table row events
        this.bindTableEvents();
    }

    bindMessageEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.message-close')) {
                const message = e.target.closest('.message');
                message.style.transition = 'opacity 0.3s ease';
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            }
        });
    }

    bindInputEvents() {
        // Real-time validation
        document.addEventListener('input', (e) => {
            if (e.target.matches('.form-input')) {
                this.validateField(e.target);
            }
        });

        // KRA PIN real-time validation
        const kraPinInput = document.getElementById('kra_pin');
        if (kraPinInput) {
            kraPinInput.addEventListener('input', (e) => {
                const value = e.target.value.toUpperCase().trim();
                e.target.value = value;
                this.validateKraPin(value);
            });
        }

        // Number formatting
        document.addEventListener('blur', (e) => {
            if (e.target.matches('input[type="number"]')) {
                this.formatNumberInput(e.target);
            }
        }, true);
    }

    bindTableEvents() {
        const tableRows = document.querySelectorAll('.data-table tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.transform = 'translateY(-1px)';
            });
            row.addEventListener('mouseleave', () => {
                row.style.transform = 'translateY(0)';
            });
        });
    }

    initializeBenefits() {
        // Add event listeners to existing benefit rows
        document.querySelectorAll('.benefit-row').forEach((row, index) => {
            this.initializeBenefitRow(row, index);
        });

        // Update benefits summary
        this.updateBenefitsSummary();
    }

    initializeBenefitRow(row, index) {
        const nameInput = row.querySelector('.benefit-name');
        const amountInput = row.querySelector('.benefit-amount');
        const removeBtn = row.querySelector('.btn--remove');

        if (nameInput) {
            nameInput.addEventListener('input', () => this.updateBenefitsSummary());
        }

        if (amountInput) {
            amountInput.addEventListener('input', () => this.updateBenefitsSummary());
            amountInput.addEventListener('blur', () => this.formatNumberInput(amountInput));
        }

        if (removeBtn) {
            removeBtn.addEventListener('click', () => this.removeBenefitRow(row));
        }
    }

    addBenefitRow() {
        const index = document.querySelectorAll('.benefit-row').length;
        const newRow = this.createBenefitRow(index);
        this.elements.benefitsContainer.appendChild(newRow);
        this.initializeBenefitRow(newRow, index);
        
        // Scroll to new row
        newRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Animate addition
        newRow.style.opacity = '0';
        newRow.style.transform = 'translateY(10px)';
        requestAnimationFrame(() => {
            newRow.style.transition = 'all 0.3s ease';
            newRow.style.opacity = '1';
            newRow.style.transform = 'translateY(0)';
        });
    }

    createBenefitRow(index) {
        const row = document.createElement('div');
        row.className = 'benefit-row';
        row.dataset.index = index;
        row.innerHTML = `
            <div class="benefit-inputs">
                <input 
                    type="text" 
                    class="benefit-name form-input" 
                    placeholder="Benefit name (e.g., Housing Allowance)"
                    maxlength="50"
                >
                <div class="input-group">
                    <span class="input-prefix">KSh</span>
                    <input 
                        type="number" 
                        class="benefit-amount form-input" 
                        placeholder="0.00"
                        step="0.01" 
                        min="0"
                        autocomplete="off"
                    >
                </div>
            </div>
            <button type="button" class="btn btn--ghost btn--remove" title="Remove benefit">
                <i class="fas fa-times"></i>
            </button>
        `;
        return row;
    }

    removeBenefitRow(row) {
        const rows = document.querySelectorAll('.benefit-row');
        if (rows.length > 1) {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '0';
            row.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                row.remove();
                this.updateBenefitsSummary();
            }, 300);
        } else {
            // Clear the single row instead of removing
            row.querySelector('.benefit-name').value = '';
            row.querySelector('.benefit-amount').value = '';
            this.updateBenefitsSummary();
        }
    }

    updateBenefitsSummary() {
        const benefits = this.getBenefitsData();
        const total = benefits.reduce((sum, benefit) => sum + benefit.amount, 0);
        
        const summaryElement = document.getElementById('benefits-summary');
        const totalElement = document.getElementById('total-benefits');
        
        if (totalElement) {
            totalElement.textContent = `KSh ${total.toLocaleString('en-KE', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            })}`;
        }

        // Update hidden field
        if (this.elements.benefitsData) {
            this.elements.benefitsData.value = JSON.stringify(benefits);
        }

        // Visual feedback
        const container = document.querySelector('.benefits-container');
        if (benefits.length > 0) {
            container.classList.add('has-benefits');
        } else {
            container.classList.remove('has-benefits');
        }
    }

    getBenefitsData() {
        const benefits = [];
        document.querySelectorAll('.benefit-row').forEach(row => {
            const name = row.querySelector('.benefit-name')?.value.trim();
            const amount = parseFloat(row.querySelector('.benefit-amount')?.value) || 0;
            
            if (name && amount > 0) {
                benefits.push({ name, amount });
            }
        });
        return benefits;
    }

    validateField(input) {
        const value = input.value.trim();
        const isRequired = input.hasAttribute('required');
        
        if (isRequired && !value) {
            this.setFieldState(input, 'invalid', 'This field is required');
            return false;
        }

        if (value) {
            // Specific validations
            if (input.id === 'kra_pin') {
                return this.validateKraPin(value);
            }
            
            if (input.id === 'basic_salary') {
                return this.validateSalary(value);
            }
        }

        this.setFieldState(input, 'valid');
        return true;
    }

    validateKraPin(value) {
        const pin = value.toUpperCase().trim();
        const regex = /^[A][0-9]{9}[A-Z]$/;
        const isValid = regex.test(pin) && pin.length === 11;
        
        if (isValid) {
            this.setFieldState(document.getElementById('kra_pin'), 'valid');
            return true;
        } else if (value) {
            this.setFieldState(document.getElementById('kra_pin'), 'invalid', 
                'KRA PIN must be AXXXXXXXXY format (e.g., A123456789B)'
            );
            return false;
        }
        
        return true;
    }

    validateSalary(value) {
        const salary = parseFloat(value);
        if (salary < 10000 || salary > 1000000) {
            this.setFieldState(document.getElementById('basic_salary'), 'invalid',
                'Salary must be between KSh 10,000 and KSh 1,000,000'
            );
            return false;
        }
        
        this.setFieldState(document.getElementById('basic_salary'), 'valid');
        return true;
    }

    setFieldState(input, state, message = '') {
        input.classList.remove('is-valid', 'is-invalid');
        
        if (state === 'valid') {
            input.classList.add('is-valid');
        } else if (state === 'invalid') {
            input.classList.add('is-invalid');
        }

        // Update error message if needed
        const errorElement = input.parentNode.querySelector('.error-message');
        if (errorElement) {
            if (message) {
                errorElement.textContent = message;
                errorElement.style.display = 'block';
            } else {
                errorElement.style.display = 'none';
            }
        }
    }

    formatNumberInput(input) {
        const value = parseFloat(input.value);
        if (!isNaN(value) && value >= 0) {
            input.value = Math.round(value * 100) / 100; // 2 decimal places
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        
        // Validate all fields
        const requiredFields = ['employee_id', 'kra_pin', 'first_name', 'last_name', 'basic_salary'];
        let isValid = true;
        let firstInvalidField = null;

        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!field.value.trim()) {
                this.setFieldState(field, 'invalid', 'This field is required');
                isValid = false;
                if (!firstInvalidField) firstInvalidField = field;
            } else {
                this.validateField(field);
            }
        });

        // Validate benefits
        const benefits = this.getBenefitsData();
        this.elements.benefitsData.value = JSON.stringify(benefits);

        if (!isValid) {
            // Scroll to first invalid field
            if (firstInvalidField) {
                firstInvalidField.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
                firstInvalidField.focus();
            }
            
            // Show validation summary
            this.showValidationError();
            return false;
        }

        // Show loading state
        this.showLoading();
        
        // Submit form
        setTimeout(() => {
            this.elements.form.submit();
        }, 500);
    }

    handleReset(e) {
        e.preventDefault();
        
        // Clear all fields
        document.querySelectorAll('.form-input').forEach(input => {
            input.value = '';
            input.classList.remove('is-valid', 'is-invalid');
        });
        
        // Remove all benefit rows except first
        const benefitRows = document.querySelectorAll('.benefit-row');
        if (benefitRows.length > 1) {
            Array.from(benefitRows).slice(1).forEach(row => row.remove());
        } else {
            // Clear first row
            benefitRows[0].querySelector('.benefit-name').value = '';
            benefitRows[0].querySelector('.benefit-amount').value = '';
        }
        
        this.updateBenefitsSummary();
        
        // Hide loading and show success
        this.hideLoading();
        this.showResetMessage();
    }

    showLoading() {
        this.elements.loadingOverlay.classList.add('show');
        this.elements.submitBtn.disabled = true;
        this.elements.submitBtn.querySelector('.btn-text').style.display = 'none';
        this.elements.submitBtn.querySelector('.btn-loader').style.display = 'inline-flex';
    }

    hideLoading() {
        this.elements.loadingOverlay.classList.remove('show');
        this.elements.submitBtn.disabled = false;
        this.elements.submitBtn.querySelector('.btn-text').style.display = 'inline';
        this.elements.submitBtn.querySelector('.btn-loader').style.display = 'none';
    }

    showValidationError() {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message message--error';
        errorDiv.innerHTML = `
            <div class="message-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="message-content">
                <div class="message-text">Please fix the highlighted fields before submitting</div>
            </div>
            <button class="message-close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.querySelector('.message-container') || 
                         document.querySelector('.form-section');
        container.insertBefore(errorDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    showResetMessage() {
        const successDiv = document.createElement('div');
        successDiv.className = 'message message--success';
        successDiv.innerHTML = `
            <div class="message-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="message-content">
                <div class="message-text">Form has been reset. Ready for new entry.</div>
            </div>
            <button class="message-close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.querySelector('.message-container') || 
                         document.querySelector('.form-section');
        container.insertBefore(successDiv, container.firstChild);
        
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.remove();
            }
        }, 3000);
    }

    initializeAnimations() {
        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.form-section, .table-section, .empty-state').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PayrollCalculator();
});

// Service Worker Registration (Progressive Web App)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}