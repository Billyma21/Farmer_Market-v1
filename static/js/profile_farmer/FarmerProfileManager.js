// static/js/profile_farmer/FarmerProfileManager.js

import { FormManager, NotificationManager } from '../utils/FormManager.js';
import { APP_CONFIG, DOM_SELECTORS, VALIDATION_RULES } from '../config.js';


export class FarmerProfileManager extends FormManager {
    constructor(formSelector = DOM_SELECTORS.FORMS.FARMER) {
        super(formSelector, VALIDATION_RULES.FARMER);
        this.map = null;
        this.marker = null;
        this.debounceTimer = null;
        
        this.initMap();
        this.initAddressAutocomplete();
        this.initOpeningHours();
    }

    initMap() {
        const mapElement = document.querySelector(DOM_SELECTORS.CONTAINERS.MAP);
        if (!mapElement) return;

        try {
            const startCoords = this.getInitialCoordinates();
            
            this.map = L.map(mapElement).setView(startCoords, APP_CONFIG.MAP.ZOOM_LEVEL);
            
            L.tileLayer(APP_CONFIG.MAP.TILE_LAYER, {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: APP_CONFIG.MAP.MAX_ZOOM
            }).addTo(this.map);

            if (startCoords.isValid) {
                this.marker = L.marker(startCoords).addTo(this.map);
            }

            this.makeMapResponsive();
        } catch (error) {
            NotificationManager.error(MESSAGES.ERROR.MAP);
            console.error('Erreur carte:', error);
        }
    }

    getInitialCoordinates() {
        const latInput = document.querySelector(DOM_SELECTORS.INPUTS.LAT);
        const lonInput = document.querySelector(DOM_SELECTORS.INPUTS.LON);
        
        const lat = latInput?.value ? parseFloat(latInput.value) : APP_CONFIG.MAP.DEFAULT_LAT;
        const lon = lonInput?.value ? parseFloat(lonInput.value) : APP_CONFIG.MAP.DEFAULT_LON;
        
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

        setTimeout(() => this.map?.invalidateSize(), APP_CONFIG.UI.ANIMATION_DURATION);
    }

    initAddressAutocomplete() {
        const addressInput = document.querySelector(DOM_SELECTORS.INPUTS.ADDRESS);
        if (!addressInput) return;

        addressInput.addEventListener('input', this.handleAddressInput.bind(this));
        document.addEventListener('click', this.handleClickOutside.bind(this));
    }

    handleAddressInput(event) {
        clearTimeout(this.debounceTimer);
        const query = event.target.value.trim();

        if (query.length < APP_CONFIG.NOMINATIM.MIN_QUERY_LENGTH) {
            this.clearSuggestions();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.fetchAddressSuggestions(query);
        }, APP_CONFIG.NOMINATIM.DEBOUNCE_DELAY);
    }

    async fetchAddressSuggestions(query) {
        try {
            const url = new URL(APP_CONFIG.NOMINATIM.BASE_URL);
            url.searchParams.append('format', 'json');
            url.searchParams.append('q', query);
            url.searchParams.append('limit', APP_CONFIG.NOMINATIM.RESULTS_LIMIT);
            url.searchParams.append('addressdetails', '1');

            const response = await fetch(url, {
                headers: {
                    'Accept-Language': 'fr'
                }
            });

            if (!response.ok) throw new Error(MESSAGES.ERROR.NETWORK);

            const data = await response.json();
            this.displayAddressSuggestions(data);
        } catch (error) {
            NotificationManager.error(MESSAGES.ERROR.NETWORK);
        }
    }

    displayAddressSuggestions(results) {
        const container = document.querySelector(DOM_SELECTORS.CONTAINERS.SUGGESTIONS);
        if (!container) return;

        container.innerHTML = '';
        container.classList.toggle('active', results.length > 0);

        results.forEach(result => {
            const suggestion = document.createElement('div');
            suggestion.classList.add('address-suggestion');
            suggestion.textContent = result.display_name;
            suggestion.addEventListener('click', () => this.selectAddress(result));
            container.appendChild(suggestion);
        });
    }

    selectAddress(result) {
        const addressInput = document.querySelector(DOM_SELECTORS.INPUTS.ADDRESS);
        const latInput = document.querySelector(DOM_SELECTORS.INPUTS.LAT);
        const lonInput = document.querySelector(DOM_SELECTORS.INPUTS.LON);

        if (addressInput) addressInput.value = result.display_name;
        if (latInput) latInput.value = result.lat;
        if (lonInput) lonInput.value = result.lon;

        this.updateMapLocation(result.lat, result.lon);
        this.clearSuggestions();
    }

    updateMapLocation(lat, lon) {
        const coords = [parseFloat(lat), parseFloat(lon)];
        if (coords.some(isNaN)) return;

        this.map?.setView(coords, APP_CONFIG.MAP.ZOOM_LEVEL);

        if (this.marker) {
            this.marker.setLatLng(coords);
        } else {
            this.marker = L.marker(coords).addTo(this.map);
        }
    }

    initOpeningHours() {
        const modal = document.querySelector(DOM_SELECTORS.MODALS.OPENING_HOURS);
        if (!modal) return;

        document.querySelectorAll('input[type="checkbox"][name$="_closed"]').forEach(checkbox => {
            const day = checkbox.name.replace('_closed', '');
            this.toggleTimeInputs(day);
            checkbox.addEventListener('change', () => this.toggleTimeInputs(day));
        });

        const form = modal.querySelector('form');
        if (form) {
            form.addEventListener('submit', this.handleOpeningHoursSubmit.bind(this));
        }
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

    async handleOpeningHoursSubmit(event) {
        event.preventDefault();
        const form = event.target;
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error(MESSAGES.ERROR.NETWORK);

            const data = await response.json();
            if (data.status === 'success') {
                NotificationManager.success(MESSAGES.SUCCESS.UPDATE);
                this.closeModal(DOM_SELECTORS.MODALS.OPENING_HOURS);
            } else {
                throw new Error(data.message || MESSAGES.ERROR.VALIDATION);
            }
        } catch (error) {
            NotificationManager.error(error.message);
        }
    }

    closeModal(selector) {
        const modal = document.querySelector(selector);
        if (modal && window.bootstrap?.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal?.hide();
        }
    }

    clearSuggestions() {
        const container = document.querySelector(DOM_SELECTORS.CONTAINERS.SUGGESTIONS);
        if (container) {
            container.innerHTML = '';
            container.classList.remove('active');
        }
    }

    handleClickOutside(event) {
        const addressInput = document.querySelector(DOM_SELECTORS.INPUTS.ADDRESS);
        const suggestionsContainer = document.querySelector(DOM_SELECTORS.CONTAINERS.SUGGESTIONS);

        if (!addressInput?.contains(event.target) && !suggestionsContainer?.contains(event.target)) {
            this.clearSuggestions();
        }
    }

    async handleSuccess(data) {
        NotificationManager.success(MESSAGES.SUCCESS.SAVE);
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    }
}
