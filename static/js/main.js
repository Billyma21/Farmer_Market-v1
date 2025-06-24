/**
 * Main JavaScript pour Farmer Market
 * Gestion des fonctionnalités principales
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialisation des composants
    initializeComponents();
    initializeEventListeners();
    initializeAnimations();
    
    // Gestion des performances
    initializePerformanceMonitoring();
    
    // Gestion de l'accessibilité
    initializeAccessibility();
    
    // Gestion du cache
    initializeCacheManagement();
});

/**
 * Initialisation des composants principaux
 */
function initializeComponents() {
    // Initialiser les tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialiser les popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialiser les modals Bootstrap
    var modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.forEach(function (modalTriggerEl) {
        modalTriggerEl.addEventListener('click', function(e) {
            e.preventDefault();
            var targetModal = document.querySelector(this.getAttribute('data-bs-target'));
            if (targetModal) {
                var modal = new bootstrap.Modal(targetModal);
                modal.show();
            }
        });
    });
}

/**
 * Initialisation des écouteurs d'événements
 */
function initializeEventListeners() {
    
    // Gestion des formulaires
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Gestion des boutons d'ajout au panier
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });
    
    // Gestion des quantités
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', handleQuantityChange);
    });
    
    // Gestion des filtres
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', handleFilterChange);
    });
    
    // Gestion de la recherche
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Gestion des images lazy loading
    const images = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
}

/**
 * Gestion de la soumission des formulaires
 */
function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Traitement...';
    }
    
    // Validation côté client
    if (!validateForm(form)) {
        event.preventDefault();
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = submitButton.dataset.originalText || 'Soumettre';
        }
        return false;
    }
}

/**
 * Validation des formulaires
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Ce champ est requis');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validation email
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Email invalide');
            isValid = false;
        }
    });
    
    // Validation des mots de passe
    const passwordFields = form.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        if (field.value && field.value.length < 8) {
            showFieldError(field, 'Le mot de passe doit contenir au moins 8 caractères');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Gestion de l'ajout au panier
 */
function handleAddToCart(event) {
    event.preventDefault();
    
    const button = event.target;
    const productId = button.dataset.productId;
    const quantity = button.closest('.product-actions').querySelector('.quantity-input')?.value || 1;
    
    // Désactiver le bouton
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Ajout...';
    
    // Envoyer la requête AJAX
    fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
                    },
        body: JSON.stringify({
            product_id: productId,
            quantity: parseInt(quantity)
        })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
            // Mettre à jour le compteur du panier
            updateCartCount();
            
            // Afficher un message de succès
            showNotification('Produit ajouté au panier !', 'success');
            
            // Animation du bouton
            button.innerHTML = '<i class="fas fa-check me-1"></i>Ajouté';
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-cart-plus me-1"></i>Ajouter au panier';
            }, 2000);
        } else {
            throw new Error(data.message || 'Erreur lors de l\'ajout au panier');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors de l\'ajout au panier', 'error');
        
        // Réactiver le bouton
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-cart-plus me-1"></i>Ajouter au panier';
    });
}

/**
 * Gestion du changement de quantité
 */
function handleQuantityChange(event) {
    const input = event.target;
    const value = parseInt(input.value);
    const min = parseInt(input.min) || 1;
    const max = parseInt(input.max) || 999;
    
    if (value < min) {
        input.value = min;
    } else if (value > max) {
        input.value = max;
    }
    
    // Mettre à jour le prix total si nécessaire
    updateTotalPrice(input);
}

/**
 * Gestion des filtres
 */
function handleFilterChange(event) {
    const select = event.target;
    const form = select.closest('form');
    
    if (form) {
        form.submit();
    }
}

/**
 * Gestion de la recherche
 */
function handleSearch(event) {
    const input = event.target;
    const query = input.value.trim();
    
    if (query.length >= 2) {
        // Ici vous pouvez implémenter une recherche AJAX en temps réel
        console.log('Recherche pour:', query);
    }
}

/**
 * Mise à jour du compteur du panier
 */
function updateCartCount() {
    fetch('/cart/count/')
        .then(response => response.json())
        .then(data => {
            const cartCountElement = document.getElementById('cart-count');
            if (cartCountElement) {
                cartCountElement.textContent = data.count;
                
                if (data.count > 0) {
                    cartCountElement.style.display = 'flex';
                    cartCountElement.classList.add('has-items');
                    } else {
                    cartCountElement.style.display = 'none';
                    cartCountElement.classList.remove('has-items');
                }
                    }
                })
                .catch(error => {
            console.error('Erreur lors de la mise à jour du panier:', error);
        });
}

/**
 * Mise à jour du prix total
 */
function updateTotalPrice(quantityInput) {
    const productCard = quantityInput.closest('.product-card, .cart-item');
    const priceElement = productCard.querySelector('.price');
    const totalElement = productCard.querySelector('.total-price');
    
    if (priceElement && totalElement) {
        const price = parseFloat(priceElement.dataset.price || priceElement.textContent.replace('€', '').trim());
        const quantity = parseInt(quantityInput.value);
        const total = price * quantity;
        
        totalElement.textContent = total.toFixed(2) + ' €';
    }
}

/**
 * Affichage des erreurs de champ
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Suppression des erreurs de champ
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Validation d'email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Récupération du token CSRF
 */
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

/**
 * Fonction debounce
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Initialisation des animations
 */
function initializeAnimations() {
    // Animation des éléments au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observer les éléments avec la classe 'animate-on-scroll'
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Initialisation du monitoring des performances
 */
function initializePerformanceMonitoring() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            
            if (loadTime > 3000) {
                console.warn('Temps de chargement élevé:', loadTime + 'ms');
            }
            
            // Envoyer les métriques à votre service d'analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', 'timing_complete', {
                    name: 'load',
                    value: Math.round(loadTime)
                });
            }
        });
    }
}

/**
 * Initialisation de l'accessibilité
 */
function initializeAccessibility() {
    // Gestion du focus pour les modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                modal.hide();
                    }
                }
            });
    
    // Amélioration de la navigation au clavier
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });
}

/**
 * Initialisation de la gestion du cache
 */
function initializeCacheManagement() {
    if ('serviceWorker' in navigator) {
        // Vérifier les mises à jour du service worker
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            showNotification('Nouvelle version disponible. Rechargez la page pour l\'appliquer.', 'info');
        });
    }
    
    // Gestion du cache des images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', () => {
            img.src = '/static/images/placeholder.jpg';
        });
    });
}

/**
 * Système de notifications
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
            ${message}
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-suppression
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Animation d'entrée
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);
}

/**
 * Icône pour les notifications
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Gestion des erreurs globales
 */
window.addEventListener('error', (event) => {
    console.error('Erreur JavaScript:', event.error);
    
    // Envoyer l'erreur à votre service de monitoring
    if (typeof gtag !== 'undefined') {
        gtag('event', 'exception', {
            description: event.error.message,
            fatal: false
        });
    }
});

/**
 * Gestion des promesses rejetées
 */
window.addEventListener('unhandledrejection', (event) => {
    console.error('Promesse rejetée:', event.reason);
    
    // Envoyer l'erreur à votre service de monitoring
    if (typeof gtag !== 'undefined') {
        gtag('event', 'exception', {
            description: event.reason.toString(),
            fatal: false
        });
    }
});

// Export des fonctions pour utilisation globale
window.FarmerMarket = {
    showNotification,
    updateCartCount,
    validateForm,
    debounce
}; 