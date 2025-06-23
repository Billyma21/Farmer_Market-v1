from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class IsFarmer(permissions.BasePermission):
    """
    Autorisation personnalisée pour n'autoriser que les fermiers à accéder à certaines vues.
    """
    message = "Seuls les utilisateurs avec le rôle 'fermier' peuvent accéder à cette fonctionnalité."

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_farmer

class IsProductOwner(permissions.BasePermission):
    """
    Autorisation personnalisée pour n'autoriser que le propriétaire d'un produit à le modifier.
    """
    message = "Vous devez être le propriétaire de ce produit pour effectuer cette action."

    def has_object_permission(self, request, view, obj):
        # Si la méthode est sûre (GET, HEAD, OPTIONS), autoriser
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Vérifier que l'utilisateur est le propriétaire du produit
        return obj.farmer == request.user

class IsOrderCustomer(permissions.BasePermission):
    """
    Autorisation personnalisée pour n'autoriser que le client ayant passé la commande à y accéder.
    """
    message = "Vous devez être le client ayant passé cette commande pour effectuer cette action."

    def has_object_permission(self, request, view, obj):
        # Vérifier que l'utilisateur est le client de la commande
        return obj.customer == request.user

def farmer_required(view_func):
    """
    Décorateur pour les vues basées sur les fonctions qui vérifie que l'utilisateur est un fermier.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
            
        if not hasattr(request.user, 'profile') or not request.user.profile.is_farmer:
            raise PermissionDenied("Vous devez être un fermier pour accéder à cette page.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def customer_required(view_func):
    """
    Décorateur pour les vues basées sur les fonctions qui vérifie que l'utilisateur est un client.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
            
        if hasattr(request.user, 'profile') and request.user.profile.is_farmer:
            raise PermissionDenied("Cette page est réservée aux clients.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view 