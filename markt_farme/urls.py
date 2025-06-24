# farmers_market/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from products.views.language_views import set_language

# URLs qui ne changent pas selon la langue
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('products.api.urls')),  # API RESTful
]

# URLs avec support multilingue
urlpatterns += i18n_patterns(
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/set-language/', set_language, name='set_language'),  # Changement de langue
    prefix_default_language=False,  # Permet /fr/, /en/, /nl/ mais pas /fr/ pour la langue par défaut
)

# Ajouter la gestion des fichiers médias pour le développement local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
