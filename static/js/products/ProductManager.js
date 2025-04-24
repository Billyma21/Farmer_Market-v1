import { FormManager, NotificationManager } from '../utils/FormManager.js';
import { APP_CONFIG, DOM_SELECTORS, VALIDATION_RULES } from '../config.js';

export class ProductManager extends FormManager {
    constructor(formSelector = DOM_SELECTORS.FORMS.PRODUCT) {
        super(formSelector, VALIDATION_RULES.PRODUCT);
        this.setupPriceFormatting();
        this.setupQuantityControls();
        this.setupImagePreview();
    }

    setupPriceFormatting() {
        const priceInputs = this.form.querySelectorAll(DOM_SELECTORS.INPUTS.PRICE);
        priceInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/[^\d.,]/g, '');
                value = value.replace(',', '.');
                const number = parseFloat(value);
                if (!isNaN(number)) {
                    e.target.value = number.toFixed(2);
                }
            });
        });
    }

    setupQuantityControls() {
        const quantityInputs = this.form.querySelectorAll(DOM_SELECTORS.INPUTS.QUANTITY);
        quantityInputs.forEach(input => {
            const container = document.createElement('div');
            container.classList.add('quantity-control');
            
            const decrementBtn = document.createElement('button');
            decrementBtn.textContent = '-';
            decrementBtn.type = 'button';
            decrementBtn.addEventListener('click', () => this.updateQuantity(input, -1));
            
            const incrementBtn = document.createElement('button');
            incrementBtn.textContent = '+';
            incrementBtn.type = 'button';
            incrementBtn.addEventListener('click', () => this.updateQuantity(input, 1));
            
            input.parentNode.insertBefore(container, input);
            container.appendChild(decrementBtn);
            container.appendChild(input);
            container.appendChild(incrementBtn);
        });
    }

    updateQuantity(input, delta) {
        const currentValue = parseInt(input.value) || 0;
        const newValue = Math.max(0, currentValue + delta);
        input.value = newValue;
        input.dispatchEvent(new Event('input'));
    }

    setupImagePreview() {
        const imageInput = this.form.querySelector('input[type="file"]');
        if (!imageInput) return;

        const previewContainer = document.createElement('div');
        previewContainer.classList.add('image-preview-container');
        imageInput.parentNode.insertBefore(previewContainer, imageInput.nextSibling);

        imageInput.addEventListener('change', (e) => {
            if (this.handleFileUpload(e)) {
                this.displayImagePreviews(e.target.files, previewContainer);
            }
        });
    }

    displayImagePreviews(files, container) {
        container.innerHTML = '';
        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.createElement('div');
                preview.classList.add('image-preview');
                preview.innerHTML = `
                    <img src="${e.target.result}" alt="Aperçu">
                    <button type="button" class="remove-image">&times;</button>
                `;
                
                preview.querySelector('.remove-image').addEventListener('click', () => {
                    preview.remove();
                    if (container.children.length === 0) {
                        this.form.querySelector('input[type="file"]').value = '';
                    }
                });
                
                container.appendChild(preview);
            };
            reader.readAsDataURL(file);
        });
    }

    async handleSuccess(data) {
        NotificationManager.success('Produit enregistré avec succès');
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    }
} 