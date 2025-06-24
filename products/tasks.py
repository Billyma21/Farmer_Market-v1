# products/tasks.py
import logging
from products.services import NotificationService, ReportService, OrderService
from django.utils import timezone
from datetime import timedelta
from products.models.models import Order

logger = logging.getLogger(__name__)

def process_pending_notifications():
    """Tâche planifiée pour traiter toutes les notifications en attente"""
    logger.info("Lancement du traitement des notifications en attente")
    try:
        NotificationService.process_pending_notifications()
        logger.info("Traitement des notifications terminé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du traitement des notifications : {str(e)}")

def check_orders_status():
    """Tâche planifiée pour vérifier et mettre à jour le statut des commandes"""
    logger.info("Vérification du statut des commandes")
    try:
        # Vérifier les commandes en attente depuis plus de 48h
        time_threshold = timezone.now() - timedelta(hours=48)
        OrderService.check_pending_orders(time_threshold)
        
        # Vérifier les commandes confirmées dont la date de retrait est passée
        OrderService.check_pickup_dates()
        
        logger.info("Vérification des commandes terminée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des commandes : {str(e)}")

def generate_weekly_reports():
    """Tâche planifiée pour générer les rapports hebdomadaires de ventes"""
    logger.info("Génération des rapports hebdomadaires")
    try:
        # Définir la période du rapport (semaine précédente)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Générer et envoyer les rapports pour tous les fermiers
        report_count = ReportService.generate_weekly_sales_reports(start_date, end_date)
        
        logger.info(f"Génération de {report_count} rapports hebdomadaires terminée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la génération des rapports hebdomadaires : {str(e)}") 