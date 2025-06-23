/**
 * Navbar Enhanced JavaScript - Hyper Professionnel
 * Optimisé pour les performances et l'expérience utilisateur
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        animationDuration: 300,
        cartUpdateInterval: 30000,
        languageChangeUrl: '/ajax-set-language/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
    };

    // Cache des éléments DOM
    const elements = {
        navbar: null,
        cartCount: null,
        languageSelector: null,
        searchForm: null,
        mobileMenu: null
    };

    // État de l'application
    const state = {
        cartCount: 0,
        currentLanguage: document.documentElement.lang || 'fr',
        isMobileMenuOpen: false,
        lastCartUpdate: 0
    };

    /**
     * Initialisation de la navbar
     */
    function init() {
        cacheElements();
        setupEventListeners();
        initializeCart();
        setupLanguageSelector();
        setupMobileMenu();
        setupPerformanceOptimizations();
    }

    /**
     * Cache les éléments DOM fréquemment utilisés
     */
    function cacheElements() {
        elements.navbar = document.querySelector('.navbar');
        elements.cartCount = document.getElementById('cart-count');
        elements.languageSelector = document.querySelector('.language-selector');
        elements.searchForm = document.querySelector('.search-form');
        elements.mobileMenu = document.querySelector('.navbar-collapse');
    }

    /**
     * Configuration des écouteurs d'événements
     */
    function setupEventListeners() {
        // Gestion du scroll pour la navbar
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(handleScroll, 10);
        }, { passive: true });

        // Gestion de la recherche
        if (elements.searchForm) {
            elements.searchForm.addEventListener('submit', handleSearch);
        }

        // Gestion des clics sur les liens de navigation
        document.addEventListener('click', handleNavigationClick);

        // Gestion de la visibilité de la page
        document.addEventListener('visibilitychange', handleVisibilityChange);
    }

    /**
     * Gestion du scroll pour optimiser les performances
     */
    function handleScroll() {
        const scrolled = window.scrollY > 50;
        elements.navbar?.classList.toggle('navbar-scrolled', scrolled);
    }

    /**
     * Gestion de la recherche avec debounce
     */
    function handleSearch(event) {
        const input = event.target.querySelector('input[name="q"]');
        if (input && input.value.trim().length < 2) {
            event.preventDefault();
            showNotification('Veuillez saisir au moins 2 caractères', 'warning');
        }
    }

    /**
     * Gestion des clics sur la navigation
     */
    function handleNavigationClick(event) {
        const link = event.target.closest('a');
        if (!link) return;

        // Ajout d'un effet de clic
        if (link.classList.contains('nav-link')) {
            addClickEffect(link);
        }

        // Gestion des liens externes
        if (link.hostname !== window.location.hostname) {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        }
    }

    /**
     * Effet de clic sur les liens
     */
    function addClickEffect(element) {
        element.style.transform = 'scale(0.95)';
        setTimeout(() => {
            element.style.transform = '';
        }, 150);
    }

    /**
     * Initialisation du panier
     */
    function initializeCart() {
        if (!elements.cartCount) return;

        updateCartCount();
        setupCartInterval();
    }

    /**
     * Mise à jour du compteur de panier
     */
    async function updateCartCount() {
        try {
            const response = await fetch('/cart/count/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Cache-Control': 'no-cache'
                }
            });

            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            const newCount = data.count || 0;

            if (newCount !== state.cartCount) {
                state.cartCount = newCount;
                updateCartDisplay(newCount);
            }
        } catch (error) {
            console.warn('Erreur mise à jour panier:', error);
        }
    }

    /**
     * Mise à jour de l'affichage du panier
     */
    function updateCartDisplay(count) {
        if (!elements.cartCount) return;

        elements.cartCount.textContent = count;
        
        if (count > 0) {
            elements.cartCount.style.display = 'flex';
            elements.cartCount.classList.add('animate__animated', 'animate__pulse');
            setTimeout(() => {
                elements.cartCount.classList.remove('animate__animated', 'animate__pulse');
            }, 1000);
        } else {
            elements.cartCount.style.display = 'none';
        }
    }

    /**
     * Configuration de l'intervalle de mise à jour du panier
     */
    function setupCartInterval() {
        let interval = setInterval(updateCartCount, CONFIG.cartUpdateInterval);

        // Pause quand la page n'est pas visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                clearInterval(interval);
            } else {
                updateCartCount();
                interval = setInterval(updateCartCount, CONFIG.cartUpdateInterval);
            }
        });
    }

    /**
     * Configuration du sélecteur de langue
     */
    function setupLanguageSelector() {
        if (!elements.languageSelector) return;

        const languageLinks = elements.languageSelector.querySelectorAll('.dropdown-item');
        languageLinks.forEach(link => {
            link.addEventListener('click', handleLanguageChange);
        });
    }

    /**
     * Gestion du changement de langue
     */
    async function handleLanguageChange(event) {
        event.preventDefault();
        
        const link = event.currentTarget;
        const langCode = link.getAttribute('href').match(/lang=([^&]+)/)?.[1];
        
        if (!langCode) return;

        // Effet visuel immédiat
        link.classList.add('loading');
        
        try {
            const response = await fetch(CONFIG.languageChangeUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': CONFIG.csrfToken
                },
                body: JSON.stringify({
                    language: langCode,
                    current_url: window.location.pathname
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Mise à jour de l'interface
                updateLanguageDisplay(langCode);
                
                // Rechargement de la page pour appliquer les traductions
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            } else {
                showNotification('Erreur lors du changement de langue', 'error');
            }
        } catch (error) {
            console.error('Erreur changement langue:', error);
            showNotification('Erreur lors du changement de langue', 'error');
        } finally {
            link.classList.remove('loading');
        }
    }

    /**
     * Mise à jour de l'affichage de la langue
     */
    function updateLanguageDisplay(langCode) {
        const currentLangElement = document.querySelector('.current-lang');
        if (currentLangElement) {
            currentLangElement.textContent = langCode.toUpperCase();
        }
        
        // Mise à jour des icônes de sélection
        document.querySelectorAll('.language-selector .fas.fa-check').forEach(icon => {
            icon.style.display = 'none';
        });
        
        const selectedLink = document.querySelector(`[href*="lang=${langCode}"]`);
        if (selectedLink) {
            const checkIcon = selectedLink.querySelector('.fas.fa-check');
            if (checkIcon) {
                checkIcon.style.display = 'inline-block';
            }
        }
    }

    /**
     * Configuration du menu mobile
     */
    function setupMobileMenu() {
        if (!elements.mobileMenu) return;

        const toggleButton = document.querySelector('.navbar-toggler');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => {
                state.isMobileMenuOpen = !state.isMobileMenuOpen;
                toggleButton.setAttribute('aria-expanded', state.isMobileMenuOpen);
            });
        }

        // Fermer le menu mobile lors du clic sur un lien
        elements.mobileMenu.addEventListener('click', (event) => {
            if (event.target.tagName === 'A' && window.innerWidth < 992) {
                const bsCollapse = new bootstrap.Collapse(elements.mobileMenu);
                bsCollapse.hide();
                state.isMobileMenuOpen = false;
            }
        });
    }

    /**
     * Gestion du changement de visibilité
     */
    function handleVisibilityChange() {
        if (!document.hidden) {
            // Mise à jour immédiate quand la page redevient visible
            updateCartCount();
        }
    }

    /**
     * Optimisations de performance
     */
    function setupPerformanceOptimizations() {
        // Lazy loading des images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }

        // Préchargement des ressources critiques
        preloadCriticalResources();
    }

    /**
     * Préchargement des ressources critiques
     */
    function preloadCriticalResources() {
        const criticalResources = [
            '/static/css/components.css',
            '/static/css/home.css'
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = 'style';
            document.head.appendChild(link);
        });
    }

    /**
     * Affichage des notifications
     */
    function showNotification(message, type = 'info') {
        // Création d'une notification toast
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-notification-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Animation d'entrée
        setTimeout(() => toast.classList.add('show'), 10);

        // Suppression automatique
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
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
     * Utilitaires pour les animations
     */
    const animations = {
        fadeIn: (element, duration = 300) => {
            element.style.opacity = '0';
            element.style.display = 'block';
            
            let start = performance.now();
            
            function animate(currentTime) {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                element.style.opacity = progress;
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            }
            
            requestAnimationFrame(animate);
        },

        slideDown: (element, duration = 300) => {
            element.style.height = '0';
            element.style.overflow = 'hidden';
            element.style.display = 'block';
            
            const targetHeight = element.scrollHeight;
            
            let start = performance.now();
            
            function animate(currentTime) {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                element.style.height = `${targetHeight * progress}px`;
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.height = 'auto';
                    element.style.overflow = 'visible';
                }
            }
            
            requestAnimationFrame(animate);
        }
    };

    // Export des fonctions publiques
    window.NavbarManager = {
        updateCartCount,
        showNotification,
        animations,
        state
    };

    // Initialisation quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})(); 