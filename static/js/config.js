// Configuration globale de l'application
const APP_CONFIG = {
    API: {
        BASE_URL: '/api/v1',
        ENDPOINTS: {
            PRODUCTS: '/products',
            FARMERS: '/farmers',
            ORDERS: '/orders'
        }
    },
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
    UPLOAD: {
        MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
        ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
        MAX_FILES: 5
    },
    UI: {
        ANIMATION_DURATION: 300,
        TOAST_TIMEOUT: 3000,
        DEBOUNCE_DELAY: 300
    }
};

// Sélecteurs DOM communs
const DOM_SELECTORS = {
    FORMS: {
        PRODUCT: '#product-form',
        FARMER: '#farmer-profile-form',
        SEARCH: '#search-form'
    },
    INPUTS: {
        ADDRESS: '#address-input',
        SEARCH: '#search-input',
        PRICE: '.price-input',
        QUANTITY: '.quantity-input',
        LAT: '#lat-input',
        LON: '#lon-input'
    },
    CONTAINERS: {
        PRODUCTS: '#products-container',
        CART: '#cart-container',
        MAP: '#map',
        SUGGESTIONS: '#address-suggestions'
    },
    BUTTONS: {
        SUBMIT: '.submit-btn',
        CANCEL: '.cancel-btn',
        ADD_TO_CART: '.add-to-cart-btn'
    },
    MODALS: {
        OPENING_HOURS: '#opening-hours-modal',
        CONFIRM: '#confirm-modal',
        PREVIEW: '#preview-modal'
    }
};

// Messages d'erreur et de succès
const MESSAGES = {
    SUCCESS: {
        SAVE: 'Enregistrement réussi',
        UPDATE: 'Mise à jour effectuée',
        DELETE: 'Suppression effectuée'
    },
    ERROR: {
        NETWORK: 'Erreur de connexion au serveur',
        VALIDATION: 'Veuillez vérifier les champs du formulaire',
        UPLOAD: 'Erreur lors du téléchargement du fichier',
        MAP: 'Impossible de charger la carte'
    }
};

// Validation des formulaires
const VALIDATION_RULES = {
    PRODUCT: {
        name: {
            required: true,
            minLength: 3,
            maxLength: 100
        },
        price: {
            required: true,
            min: 0,
            max: 9999.99
        },
        quantity: {
            required: true,
            min: 0
        }
    },
    FARMER: {
        farm_name: {
            required: true,
            minLength: 3,
            maxLength: 100
        },
        phone: {
            pattern: /^(\+\d{1,3}[-.]?)?\d{10}$/
        },
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        }
    }
};

export { APP_CONFIG, DOM_SELECTORS, MESSAGES, VALIDATION_RULES };
