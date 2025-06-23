from django.shortcuts import redirect
from django.utils import translation
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_POST
def set_language(request):
    """Vue personnalisée pour le changement de langue"""
    try:
        # Gérer les données JSON et POST
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        language = data.get('language')
        next_url = data.get('next', '/')
        
        # Valider la langue
        available_languages = [lang[0] for lang in settings.LANGUAGES]
        if not language or language not in available_languages:
            return JsonResponse({
                'success': False,
                'error': f'Langue non supportée. Langues disponibles: {available_languages}'
            }, status=400)
        
        # Activer la langue
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        
        # Sauvegarder la session
        request.session.modified = True
        
        # Réponse pour les requêtes AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'language': language,
                'redirect_url': next_url,
                'message': f'Langue changée vers {language}'
            })
        
        # Redirection pour les requêtes normales
        return redirect(next_url)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données JSON invalides'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def get_current_language(request):
    """Obtenir la langue actuelle"""
    current_lang = translation.get_language()
    return JsonResponse({
        'language': current_lang,
        'available_languages': [lang[0] for lang in settings.LANGUAGES]
    })

@csrf_exempt
@require_POST
def ajax_set_language(request):
    """Vue AJAX pour changer la langue sans rechargement"""
    try:
        data = json.loads(request.body)
        lang_code = data.get('language')
        current_url = data.get('current_url', '/')
        
        if lang_code and lang_code in [lang[0] for lang in settings.LANGUAGES]:
            # Activer la langue
            translation.activate(lang_code)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
            
            return JsonResponse({
                'success': True,
                'language': lang_code,
                'message': 'Langue changée avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Langue non supportée'
            })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données invalides'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }) 