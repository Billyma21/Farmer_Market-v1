import logging
from django.utils.deprecation import MiddlewareMixin

class UserFilter(logging.Filter):
    """Filtre pour ajouter des informations utilisateur aux logs d'audit"""
    
    def filter(self, record):
        # Ajouter des informations par défaut
        record.user = getattr(record, 'user', 'anonymous')
        record.ip = getattr(record, 'ip', 'unknown')
        record.action = getattr(record, 'action', 'unknown')
        record.details = getattr(record, 'details', '')
        return True

class AuditMiddleware(MiddlewareMixin):
    """Middleware pour capturer les informations d'audit"""
    
    def process_request(self, request):
        # Ajouter des informations à la requête pour l'audit
        request.audit_info = {
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
        }
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

def log_audit_event(user, action, details, ip=None, level='INFO'):
    """Fonction utilitaire pour logger les événements d'audit"""
    logger = logging.getLogger('audit')
    
    # Préparer les informations d'audit
    audit_record = logging.LogRecord(
        name='audit',
        level=getattr(logging, level.upper()),
        pathname='',
        lineno=0,
        msg='',
        args=(),
        exc_info=None
    )
    
    # Ajouter les informations personnalisées
    audit_record.user = user.username if hasattr(user, 'username') else str(user)
    audit_record.ip = ip or 'unknown'
    audit_record.action = action
    audit_record.details = details
    
    logger.handle(audit_record)

def log_security_event(user, action, details, ip=None, level='WARNING'):
    """Fonction utilitaire pour logger les événements de sécurité"""
    logger = logging.getLogger('security')
    
    # Préparer les informations de sécurité
    security_record = logging.LogRecord(
        name='security',
        level=getattr(logging, level.upper()),
        pathname='',
        lineno=0,
        msg=f'Security event: {action} - {details}',
        args=(),
        exc_info=None
    )
    
    # Ajouter les informations personnalisées
    security_record.user = user.username if hasattr(user, 'username') else str(user)
    security_record.ip = ip or 'unknown'
    security_record.action = action
    security_record.details = details
    
    logger.handle(security_record)

def log_payment_event(user, action, details, ip=None, level='INFO'):
    """Fonction utilitaire pour logger les événements de paiement"""
    logger = logging.getLogger('payment')
    
    # Préparer les informations de paiement
    payment_record = logging.LogRecord(
        name='payment',
        level=getattr(logging, level.upper()),
        pathname='',
        lineno=0,
        msg=f'Payment event: {action} - {details}',
        args=(),
        exc_info=None
    )
    
    # Ajouter les informations personnalisées
    payment_record.user = user.username if hasattr(user, 'username') else str(user)
    payment_record.ip = ip or 'unknown'
    payment_record.action = action
    payment_record.details = details
    
    logger.handle(payment_record)

def log_order_event(user, action, details, ip=None, level='INFO'):
    """Fonction utilitaire pour logger les événements de commande"""
    logger = logging.getLogger('order')
    
    # Préparer les informations de commande
    order_record = logging.LogRecord(
        name='order',
        level=getattr(logging, level.upper()),
        pathname='',
        lineno=0,
        msg=f'Order event: {action} - {details}',
        args=(),
        exc_info=None
    )
    
    # Ajouter les informations personnalisées
    order_record.user = user.username if hasattr(user, 'username') else str(user)
    order_record.ip = ip or 'unknown'
    order_record.action = action
    order_record.details = details
    
    logger.handle(order_record) 