import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware(MiddlewareMixin):
    """Middleware pour optimiser les performances"""
    
    def process_request(self, request):
        # Ajouter un timestamp pour mesurer le temps de réponse
        request.start_time = time.time()
        
        # Cache des requêtes fréquentes
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
            
        # Optimisation pour les requêtes AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            request.is_ajax = True
        
        return None
    
    def process_response(self, request, response):
        # Ajouter des headers de performance
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Mesurer le temps de réponse
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Response-Time'] = f'{duration:.3f}s'
            
            # Log des requêtes lentes
            if duration > 1.0:
                logger.warning(f'Slow request: {request.path} took {duration:.3f}s')
        
        return response

class LanguageMiddleware(MiddlewareMixin):
    """Middleware pour gérer le changement de langue"""
    
    def process_request(self, request):
        # Détecter la langue préférée du navigateur
        if not request.session.get('django_language'):
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if accept_language:
                # Extraire la première langue préférée
                preferred_lang = accept_language.split(',')[0].split(';')[0].lower()
                
                # Mapper les codes de langue
                lang_mapping = {
                    'fr': 'fr',
                    'en': 'en',
                    'nl': 'nl',
                    'en-us': 'en',
                    'en-gb': 'en',
                    'fr-fr': 'fr',
                    'fr-be': 'fr',
                    'nl-nl': 'nl',
                    'nl-be': 'nl',
                }
                
                detected_lang = lang_mapping.get(preferred_lang, 'fr')
                request.session['django_language'] = detected_lang
        
        return None

class CacheMiddleware(MiddlewareMixin):
    """Middleware pour la gestion du cache"""
    
    def process_request(self, request):
        # Ne pas mettre en cache les requêtes POST ou authentifiées
        if request.method == 'POST' or request.user.is_authenticated:
            return None
        
        # Cache pour les pages publiques
        if request.path in ['/', '/products/']:
            cache_key = f'page_cache_{request.path}_{request.session.get("django_language", "fr")}'
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
        
        return None
    
    def process_response(self, request, response):
        # Mettre en cache les réponses réussies pour les pages publiques
        if (request.method == 'GET' and 
            response.status_code == 200 and 
            not request.user.is_authenticated and
            request.path in ['/', '/products/']):
            
            cache_key = f'page_cache_{request.path}_{request.session.get("django_language", "fr")}'
            cache.set(cache_key, response, 300)  # Cache de 5 minutes
        
        return response 