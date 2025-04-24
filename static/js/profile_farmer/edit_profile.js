// Configuration globale
const CONFIG = {
    MAP: {
        DEFAULT_LAT: 50.8503,
        DEFAULT_LON: 4.3517,
        ZOOM_LEVEL: 13,
        MAX_ZOOM: 19,
        TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    },
    NOMINATIM: {
        BASE_URL: 'https://nominatim.openstreetmap.org/search',
        RESULTS_LIMIT: 5,
        MIN_QUERY_LENGTH: 3,
        DEBOUNCE_DELAY: 300
    },
    SELECTORS: {
        MAP: '#map',
        ADDRESS_INPUT: '#address-input',
        ADDRESS_SUGGESTIONS: '#address-suggestions',
        LAT_INPUT: '#id_latitude',
        LON_INPUT: '#id_longitude',
        PREVIEW_BUTTON: '#preview-button',
        OPENING_HOURS_FORM: '#openingHoursForm',
        OPENING_HOURS_MODAL: '#openingHoursModal'
    }
};

class FarmerProfileManager {
    constructor() {
        this.map = null;
        this.marker = null;
        this.debounceTimer = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initMap();
            this.initAddressAutocomplete();
            this.initOpeningHours();
            this.initFormSubmission();
            this.initPreviewForm();
            this.initImagePreview();
        });
    }

    // Initialisation de la carte
    initMap() {
        try {
            const mapElement = document.querySelector(CONFIG.SELECTORS.MAP);
            if (!mapElement) return;

            const startCoords = this.getInitialCoordinates();
            
            this.map = L.map(mapElement).setView([startCoords.lat, startCoords.lon], CONFIG.MAP.ZOOM_LEVEL);
            
            L.tileLayer(CONFIG.MAP.TILE_LAYER, {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: CONFIG.MAP.MAX_ZOOM
            }).addTo(this.map);

            if (startCoords.isValid) {
                this.marker = L.marker([startCoords.lat, startCoords.lon]).addTo(this.map);
            }

            // Rendre la carte responsive
            this.makeMapResponsive();
        } catch (error) {
            console.error('Erreur lors de l\'initialisation de la carte:', error);
            this.showError('Impossible de charger la carte. Veuillez rafraîchir la page.');
        }
    }

    getInitialCoordinates() {
        const latInput = document.querySelector(CONFIG.SELECTORS.LAT_INPUT);
        const lonInput = document.querySelector(CONFIG.SELECTORS.LON_INPUT);
        
        const lat = latInput?.value ? parseFloat(latInput.value) : CONFIG.MAP.DEFAULT_LAT;
        const lon = lonInput?.value ? parseFloat(lonInput.value) : CONFIG.MAP.DEFAULT_LON;
        
        return {
            lat,
            lon,
            isValid: !isNaN(lat) && !isNaN(lon)
        };
    }

    makeMapResponsive() {
        window.addEventListener('resize', () => {
            if (this.map) {
                this.map.invalidateSize();
            }
        });

        // Force une mise à jour initiale
        setTimeout(() => this.map?.invalidateSize(), 100);
    }

    // Gestion de l'autocomplétion d'adresse
    initAddressAutocomplete() {
        const addressInput = document.querySelector(CONFIG.SELECTORS.ADDRESS_INPUT);
        const suggestionsContainer = document.querySelector(CONFIG.SELECTORS.ADDRESS_SUGGESTIONS);
        
        if (!addressInput || !suggestionsContainer) return;

        addressInput.addEventListener('input', this.handleAddressInput.bind(this));
        document.addEventListener('click', this.handleClickOutside.bind(this));
    }

    handleAddressInput(event) {
        clearTimeout(this.debounceTimer);
        const query = event.target.value.trim();

        if (query.length < CONFIG.NOMINATIM.MIN_QUERY_LENGTH) {
            this.clearSuggestions();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.fetchAddressSuggestions(query);
        }, CONFIG.NOMINATIM.DEBOUNCE_DELAY);
    }

    async fetchAddressSuggestions(query) {
        try {
            const url = new URL(CONFIG.NOMINATIM.BASE_URL);
            url.searchParams.append('format', 'json');
            url.searchParams.append('q', query);
            url.searchParams.append('limit', CONFIG.NOMINATIM.RESULTS_LIMIT);
            url.searchParams.append('addressdetails', '1');

            const response = await fetch(url, {
                headers: {
                    'Accept-Language': 'fr',
                    'User-Agent': 'FarmersMarket/1.0'
                }
            });

            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            this.displayAddressSuggestions(data);
        } catch (error) {
            console.error('Erreur lors de la recherche d\'adresse:', error);
            this.showError('La recherche d\'adresse est temporairement indisponible.');
        }
    }

    displayAddressSuggestions(results) {
        const suggestionsContainer = document.querySelector(CONFIG.SELECTORS.ADDRESS_SUGGESTIONS);
        suggestionsContainer.innerHTML = '';

        if (results.length === 0) {
            suggestionsContainer.classList.remove('active');
            return;
        }

        results.forEach(result => {
            const suggestion = this.createSuggestionElement(result);
            suggestionsContainer.appendChild(suggestion);
        });

        suggestionsContainer.classList.add('active');
    }

    createSuggestionElement(result) {
        const div = document.createElement('div');
        div.classList.add('address-suggestion-item');
        div.textContent = result.display_name;
        
        div.addEventListener('click', () => {
            this.selectAddress(result);
        });

        return div;
    }

    selectAddress(result) {
        const addressInput = document.querySelector(CONFIG.SELECTORS.ADDRESS_INPUT);
        const latInput = document.querySelector(CONFIG.SELECTORS.LAT_INPUT);
        const lonInput = document.querySelector(CONFIG.SELECTORS.LON_INPUT);

        addressInput.value = result.display_name;
        latInput.value = result.lat;
        lonInput.value = result.lon;

        this.updateMapLocation(result.lat, result.lon);
        this.clearSuggestions();
    }

    updateMapLocation(lat, lon) {
        const coords = [parseFloat(lat), parseFloat(lon)];
        
        if (coords.some(isNaN)) return;

        this.map.setView(coords, CONFIG.MAP.ZOOM_LEVEL);

        if (this.marker) {
            this.marker.setLatLng(coords);
        } else {
            this.marker = L.marker(coords).addTo(this.map);
        }
    }

    // Gestion des horaires d'ouverture
    initOpeningHours() {
        document.querySelectorAll('input[type="checkbox"][name$="_closed"]').forEach(checkbox => {
            const day = checkbox.name.replace('_closed', '');
            this.toggleTimeInputs(day);
            checkbox.addEventListener('change', () => this.toggleTimeInputs(day));
        });
    }

    toggleTimeInputs(day) {
        const checkbox = document.querySelector(`input[name="${day}_closed"]`);
        const timeInputs = document.querySelectorAll(`#row_${day} input[type="time"]`);
        const isChecked = checkbox?.checked || false;

        timeInputs.forEach(input => {
            input.disabled = isChecked;
            input.closest('tr')?.classList.toggle('closed-day', isChecked);
        });
    }

    // Gestion du formulaire
    initFormSubmission() {
        const form = document.querySelector(CONFIG.SELECTORS.OPENING_HOURS_FORM);
        if (!form) return;

        form.addEventListener('submit', this.handleFormSubmit.bind(this));
    }

    async handleFormSubmit(event) {
        event.preventDefault();

        try {
            const formData = new FormData(event.target);
            const response = await fetch(event.target.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === "success") {
                this.showSuccess('Horaires enregistrés avec succès!');
                this.closeModal();
            } else {
                throw new Error(data.message || 'Erreur lors de l\'enregistrement');
            }
        } catch (error) {
            console.error('Erreur lors de la soumission:', error);
            this.showError('Une erreur est survenue lors de l\'enregistrement.');
        }
    }

    // Prévisualisation
    initPreviewForm() {
        const previewButton = document.querySelector(CONFIG.SELECTORS.PREVIEW_BUTTON);
        if (!previewButton) return;

        previewButton.addEventListener('click', this.handlePreview.bind(this));
    }

    handlePreview() {
        const farmerId = this.getFarmerId();
        
        if (!farmerId) {
            this.showError('Veuillez d\'abord enregistrer votre profil.');
            return;
        }

        window.location.href = `/farmer/preview/${farmerId}/`;
    }

    // Prévisualisation d'image
    initImagePreview() {
        const imageInput = document.getElementById('farm_images');
        const previewContainer = document.getElementById('image-preview-container');

        if (!imageInput || !previewContainer) return;

        imageInput.addEventListener('change', (event) => {
            this.handleImagePreview(event, previewContainer);
        });
    }

    handleImagePreview(event, container) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            container.innerHTML = `
                <img src="${e.target.result}" alt="Aperçu" class="img-preview">
                <button type="button" class="remove-image">×</button>
            `;

            container.querySelector('.remove-image').addEventListener('click', () => {
                event.target.value = '';
                container.innerHTML = '';
            });
        };
        reader.readAsDataURL(file);
    }

    // Utilitaires
    getFarmerId() {
        const previewButton = document.querySelector(CONFIG.SELECTORS.PREVIEW_BUTTON);
        return previewButton?.dataset.farmerId || 0;
    }

    closeModal() {
        const modal = document.querySelector(CONFIG.SELECTORS.OPENING_HOURS_MODAL);
        if (modal && window.bootstrap?.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal?.hide();
        }
    }

    showSuccess(message) {
        // Implémenter votre système de notification ici
        alert(message); // Version basique
    }

    showError(message) {
        // Implémenter votre système de notification ici
        alert(message); // Version basique
    }

    clearSuggestions() {
        const suggestionsContainer = document.querySelector(CONFIG.SELECTORS.ADDRESS_SUGGESTIONS);
        if (suggestionsContainer) {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.classList.remove('active');
        }
    }

    handleClickOutside(event) {
        const addressInput = document.querySelector(CONFIG.SELECTORS.ADDRESS_INPUT);
        const suggestionsContainer = document.querySelector(CONFIG.SELECTORS.ADDRESS_SUGGESTIONS);

        if (!addressInput?.contains(event.target) && !suggestionsContainer?.contains(event.target)) {
            this.clearSuggestions();
        }
    }
}

// Initialisation
const farmerProfile = new FarmerProfileManager();