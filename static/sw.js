/**
 * Service Worker pour Farmer Market
 * Gestion du cache, notifications push et fonctionnalités offline
 */

const CACHE_NAME = 'farmer-market-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';

// Fichiers à mettre en cache statique
const STATIC_FILES = [
    '/',
    '/static/css/modern-styles.css',
    '/static/css/navbar-enhanced.css',
    '/static/css/components.css',
    '/static/css/home.css',
    '/static/css/styles.css',
    '/static/js/main.js',
    '/static/js/navbar.js',
    '/static/images/logo.png',
    '/static/images/hero-bg.jpg',
    '/static/images/placeholder.jpg',
    '/static/site.webmanifest',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
];

// Routes à mettre en cache dynamique
const DYNAMIC_ROUTES = [
    '/products/',
    '/cart/',
    '/orders/',
    '/farmer/dashboard/'
];

// Installation du service worker
self.addEventListener('install', event => {
    console.log('Service Worker: Installation');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Service Worker: Mise en cache des fichiers statiques');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Service Worker: Installation terminée');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Service Worker: Erreur lors de l\'installation', error);
            })
    );
});

// Activation du service worker
self.addEventListener('activate', event => {
    console.log('Service Worker: Activation');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Suppression de l\'ancien cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activation terminée');
                return self.clients.claim();
            })
    );
});

// Interception des requêtes
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Ignorer les requêtes non-GET
    if (request.method !== 'GET') {
        return;
    }
    
    // Ignorer les requêtes vers l'API
    if (url.pathname.startsWith('/admin/') || 
        url.pathname.startsWith('/api/') ||
        url.pathname.startsWith('/static/admin/')) {
        return;
    }
    
    // Stratégie de cache pour les fichiers statiques
    if (isStaticFile(url.pathname)) {
        event.respondWith(cacheFirst(request, STATIC_CACHE));
        return;
    }
    
    // Stratégie de cache pour les pages
    if (isPageRequest(request)) {
        event.respondWith(networkFirst(request, DYNAMIC_CACHE));
        return;
    }
    
    // Stratégie par défaut
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
});

// Stratégie Cache First
async function cacheFirst(request, cacheName) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('Cache First Error:', error);
        return new Response('Erreur de connexion', { status: 503 });
    }
}

// Stratégie Network First
async function networkFirst(request, cacheName) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Network First: Utilisation du cache', error);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Page d'erreur offline
        if (request.destination === 'document') {
            return caches.match('/offline.html');
        }
        
        return new Response('Contenu non disponible hors ligne', { status: 503 });
    }
}

// Vérifier si c'est un fichier statique
function isStaticFile(pathname) {
    return pathname.startsWith('/static/') ||
           pathname.startsWith('/media/') ||
           pathname.includes('.css') ||
           pathname.includes('.js') ||
           pathname.includes('.png') ||
           pathname.includes('.jpg') ||
           pathname.includes('.jpeg') ||
           pathname.includes('.gif') ||
           pathname.includes('.svg') ||
           pathname.includes('.woff') ||
           pathname.includes('.woff2') ||
           pathname.includes('.ttf') ||
           pathname.includes('.eot');
}

// Vérifier si c'est une requête de page
function isPageRequest(request) {
    return request.destination === 'document' ||
           request.headers.get('accept').includes('text/html');
}

// Gestion des messages
self.addEventListener('message', event => {
    const { data } = event;
    
    switch (data.type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({ version: CACHE_NAME });
            break;
            
        case 'CLEAR_CACHE':
            clearAllCaches();
            break;
            
        default:
            console.log('Service Worker: Message non reconnu', data);
    }
});

// Nettoyer tous les caches
async function clearAllCaches() {
    try {
        const cacheNames = await caches.keys();
        await Promise.all(
            cacheNames.map(cacheName => caches.delete(cacheName))
        );
        console.log('Service Worker: Tous les caches ont été supprimés');
    } catch (error) {
        console.error('Service Worker: Erreur lors du nettoyage des caches', error);
    }
}

// Gestion des notifications push
self.addEventListener('push', event => {
    console.log('Service Worker: Notification push reçue');
    
    const options = {
        body: event.data ? event.data.text() : 'Nouvelle notification de Farmer Market',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Voir les produits',
                icon: '/static/images/action-explore.png'
            },
            {
                action: 'close',
                title: 'Fermer',
                icon: '/static/images/action-close.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Farmer Market', options)
    );
});

// Gestion des clics sur les notifications
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: Clic sur notification');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/products/')
        );
    } else if (event.action === 'close') {
        // Ne rien faire, la notification est déjà fermée
    } else {
        // Action par défaut
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Gestion de la fermeture des notifications
self.addEventListener('notificationclose', event => {
    console.log('Service Worker: Notification fermée');
    
    // Envoyer des analytics si nécessaire
    if (event.notification.data) {
        console.log('Notification fermée:', event.notification.data);
    }
});

// Gestion des erreurs
self.addEventListener('error', event => {
    console.error('Service Worker Error:', event.error);
});

// Gestion des rejets de promesses non gérés
self.addEventListener('unhandledrejection', event => {
    console.error('Service Worker Unhandled Rejection:', event.reason);
});

// Fonction utilitaire pour mettre à jour le cache
async function updateCache(cacheName, urls) {
    try {
        const cache = await caches.open(cacheName);
        await Promise.all(
            urls.map(url => cache.add(url))
        );
        console.log(`Cache ${cacheName} mis à jour`);
    } catch (error) {
        console.error(`Erreur lors de la mise à jour du cache ${cacheName}:`, error);
    }
}

// Fonction utilitaire pour nettoyer le cache
async function cleanupCache(cacheName, maxAge = 7 * 24 * 60 * 60 * 1000) { // 7 jours par défaut
    try {
        const cache = await caches.open(cacheName);
        const requests = await cache.keys();
        const now = Date.now();
        
        for (const request of requests) {
            const response = await cache.match(request);
            if (response) {
                const date = response.headers.get('date');
                if (date && (now - new Date(date).getTime()) > maxAge) {
                    await cache.delete(request);
                }
            }
        }
        
        console.log(`Cache ${cacheName} nettoyé`);
    } catch (error) {
        console.error(`Erreur lors du nettoyage du cache ${cacheName}:`, error);
    }
}

// Nettoyage périodique du cache (tous les 7 jours)
setInterval(() => {
    cleanupCache(DYNAMIC_CACHE);
}, 7 * 24 * 60 * 60 * 1000);

// Fonction pour précharger des ressources importantes
async function preloadResources() {
    const resources = [
        '/products/',
        '/cart/',
        '/static/images/hero-bg.jpg'
    ];
    
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        await Promise.all(
            resources.map(url => cache.add(url))
        );
        console.log('Ressources préchargées');
    } catch (error) {
        console.error('Erreur lors du préchargement:', error);
    }
}

// Précharger les ressources au démarrage
self.addEventListener('activate', event => {
    event.waitUntil(preloadResources());
}); 