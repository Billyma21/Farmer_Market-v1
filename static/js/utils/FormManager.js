import { APP_CONFIG, MESSAGES, VALIDATION_RULES } from '../config.js';


export class FormManager {
    constructor(formSelector, validationRules = {}) {
        this.form = document.querySelector(formSelector);
        this.validationRules = validationRules;
        this.init();
    }

    init() {
        if (!this.form) return;
        this.setupValidation();
        this.setupFileUploads();
        this.setupFormSubmission();
    }

    setupValidation() {
        this.form.addEventListener('input', (e) => {
            if (e.target.name in this.validationRules) {
                this.validateField(e.target);
            }
        });
    }

    validateField(field) {
        const rules = this.validationRules[field.name];
        const errors = [];

        if (rules.required && !field.value.trim()) {
            errors.push('Ce champ est requis');
        }

        if (rules.minLength && field.value.length < rules.minLength) {
            errors.push(`Minimum ${rules.minLength} caractères`);
        }

        if (rules.maxLength && field.value.length > rules.maxLength) {
            errors.push(`Maximum ${rules.maxLength} caractères`);
        }

        if (rules.pattern && !rules.pattern.test(field.value)) {
            errors.push('Format invalide');
        }

        if (rules.min && Number(field.value) < rules.min) {
            errors.push(`Minimum ${rules.min}`);
        }

        if (rules.max && Number(field.value) > rules.max) {
            errors.push(`Maximum ${rules.max}`);
        }

        this.displayFieldErrors(field, errors);
        return errors.length === 0;
    }

    displayFieldErrors(field, errors) {
        let errorContainer = field.nextElementSibling;
        if (!errorContainer || !errorContainer.classList.contains('error-message')) {
            errorContainer = document.createElement('div');
            errorContainer.classList.add('error-message');
            field.parentNode.insertBefore(errorContainer, field.nextSibling);
        }

        errorContainer.textContent = errors.join(', ');
        field.classList.toggle('is-invalid', errors.length > 0);
    }

    setupFileUploads() {
        const fileInputs = this.form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => this.handleFileUpload(e));
        });
    }

    handleFileUpload(event) {
        const files = Array.from(event.target.files);
        const errors = [];

        files.forEach(file => {
            if (file.size > APP_CONFIG.UPLOAD.MAX_FILE_SIZE) {
                errors.push(`${file.name} dépasse la taille maximale autorisée`);
            }
            if (!APP_CONFIG.UPLOAD.ALLOWED_TYPES.includes(file.type)) {
                errors.push(`${file.name} : type de fichier non autorisé`);
            }
        });

        if (errors.length > 0) {
            this.showError(errors.join('\n'));
            event.target.value = '';
            return false;
        }

        return true;
    }

    setupFormSubmission() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (this.validateForm()) {
                await this.submitForm();
            }
        });
    }

    validateForm() {
        let isValid = true;
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        return isValid;
    }

    async submitForm() {
        try {
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action, {
                method: this.form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error(MESSAGES.ERROR.NETWORK);

            const data = await response.json();
            if (data.status === 'success') {
                this.showSuccess(MESSAGES.SUCCESS.SAVE);
                this.handleSuccess(data);
            } else {
                throw new Error(data.message || MESSAGES.ERROR.VALIDATION);
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    showSuccess(message) {
        // Implémenter votre système de notification
        console.log('Success:', message);
    }

    showError(message) {
        // Implémenter votre système de notification
        console.error('Error:', message);
    }

    handleSuccess(data) {
        // À surcharger dans les classes enfants
    }
}

// Classe utilitaire pour la gestion des notifications
export class NotificationManager {
    static show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.classList.add('toast', `toast-${type}`);
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, APP_CONFIG.UI.TOAST_TIMEOUT);
        }, 100);
    }

    static success(message) {
        this.show(message, 'success');
    }

    static error(message) {
        this.show(message, 'error');
    }

    static info(message) {
        this.show(message, 'info');
    }
} 