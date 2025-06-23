# products/services.py
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from products.models.models import Notification, Order, Review, AvailabilityTimeSlot, PickupAppointment
from django.db.models import Avg, Count, F

logger = logging.getLogger(__name__)

class NotificationService:
    """Service pour la gestion et l'envoi des notifications"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type='email', order=None):
        """Crée une nouvelle notification en base de données"""
        try:
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                order=order,
                status='pending'
            )
            logger.info(f"Notification créée : {notification}")
            return notification
        except Exception as e:
            logger.error(f"Erreur lors de la création de la notification : {str(e)}")
            return None
    
    @staticmethod
    def send_email_notification(notification):
        """Envoie une notification par email"""
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False,
            )
            notification.mark_as_sent()
            logger.info(f"Email envoyé à {notification.user.email}")
            return True
        except Exception as e:
            notification.mark_as_failed()
            logger.error(f"Erreur lors de l'envoi de l'email : {str(e)}")
            return False
    
    @staticmethod
    def send_sms_notification(notification):
        """Envoie une notification par SMS (à implémenter avec un service comme Twilio)"""
        # Simuler l'envoi de SMS car l'intégration réelle nécessiterait un service externe
        try:
            # Ici, vous intégreriez un service comme Twilio
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=notification.message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=notification.user.profile.phone_number
            # )
            
            # Simuler un succès pour le moment
            logger.info(f"SMS simulé envoyé à {notification.user.username}")
            notification.mark_as_sent()
            return True
        except Exception as e:
            notification.mark_as_failed()
            logger.error(f"Erreur lors de l'envoi du SMS : {str(e)}")
            return False
    
    @staticmethod
    def process_pending_notifications():
        """Traite toutes les notifications en attente"""
        pending_notifications = Notification.objects.filter(status='pending')
        
        for notification in pending_notifications:
            if notification.notification_type == 'email':
                NotificationService.send_email_notification(notification)
            elif notification.notification_type == 'sms':
                NotificationService.send_sms_notification(notification)
            elif notification.notification_type == 'both':
                NotificationService.send_email_notification(notification)
                NotificationService.send_sms_notification(notification)
    
    @classmethod
    def notify_order_status_change(cls, order, previous_status):
        """Envoie une notification quand le statut d'une commande change"""
        
        if order.status == previous_status:
            return  # Pas de changement de statut, pas de notification
        
        notifications = {
            'confirmed': {
                'title': f"Votre commande #{order.id} a été confirmée",
                'message': f"""Bonjour {order.customer.username},
                
Votre commande #{order.id} a été confirmée par le fermier.
Elle est en cours de préparation et sera prête pour être récupérée le {order.pickup_date.strftime('%d/%m/%Y')} dans le créneau {order.pickup_time_slot}.

Merci de votre confiance,
L'équipe Farmer Market"""
            },
            'ready': {
                'title': f"Votre commande #{order.id} est prête à être récupérée",
                'message': f"""Bonjour {order.customer.username},
                
Bonne nouvelle ! Votre commande #{order.id} est maintenant prête à être récupérée.
N'oubliez pas d'apporter vos propres sacs ou contenants pour récupérer vos produits.

Date de retrait : {order.pickup_date.strftime('%d/%m/%Y')}
Créneau horaire : {order.pickup_time_slot}
Adresse : {order.customer.profile.address if hasattr(order.customer, 'profile') and hasattr(order.customer.profile, 'address') else "Voir les détails sur le site"}

Merci et à bientôt,
L'équipe Farmer Market"""
            },
            'completed': {
                'title': f"Merci pour votre achat - Commande #{order.id} terminée",
                'message': f"""Bonjour {order.customer.username},
                
Merci d'avoir récupéré votre commande #{order.id}.
Nous espérons que vos produits vous satisferont pleinement. N'hésitez pas à laisser un avis sur les produits que vous avez achetés.

À très bientôt sur Farmer Market !"""
            },
            'cancelled': {
                'title': f"Commande #{order.id} annulée",
                'message': f"""Bonjour {order.customer.username},
                
Votre commande #{order.id} a été annulée.
Si cette annulation ne vient pas de vous, veuillez nous contacter pour plus d'informations.

Cordialement,
L'équipe Farmer Market"""
            }
        }
        
        if order.status in notifications:
            notification_data = notifications[order.status]
            notification = cls.create_notification(
                user=order.customer,
                title=notification_data['title'],
                message=notification_data['message'],
                order=order
            )
            
            # Envoyer immédiatement la notification
            cls.send_email_notification(notification)
            return notification
        
        return None

class OrderService:
    """Service pour la gestion des commandes"""
    
    @staticmethod
    def update_order_status(order, status):
        """Met à jour le statut d'une commande et envoie les notifications appropriées"""
        previous_status = order.status
        
        # Vérifier que le nouveau statut est valide
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['ready', 'cancelled'],
            'ready': ['completed', 'cancelled'],
            'completed': [],  # Statut final, pas de transition possible
            'cancelled': []   # Statut final, pas de transition possible
        }
        
        if status not in valid_transitions.get(previous_status, []):
            logger.warning(f"Transition de statut invalide : {previous_status} -> {status}")
            return False
        
        # Mettre à jour le statut
        order.status = status
        order.save()
        
        # Envoyer une notification
        NotificationService.notify_order_status_change(order, previous_status)
        
        return True
    
    @staticmethod
    def check_pending_orders(time_threshold):
        """Vérifie les commandes en attente depuis trop longtemps"""
        from products.models.models import Order
        
        pending_orders = Order.objects.filter(
            status='pending',
            created_at__lt=time_threshold
        )
        
        for order in pending_orders:
            # Notification au client
            NotificationService.create_notification(
                user=order.customer,
                title=f"Votre commande #{order.id} est toujours en attente",
                message=f"""Bonjour {order.customer.username},
                
Votre commande #{order.id} est toujours en attente de confirmation par le(s) fermier(s).
Nous faisons notre possible pour accélérer le processus. Si vous préférez annuler votre commande,
vous pouvez le faire depuis votre espace personnel.

Merci pour votre patience,
L'équipe Farmer Market""",
                order=order
            )
            
            # Notification aux fermiers concernés
            from accounts.models import User
            for item in order.items.all():
                farmer = item.product.farmer
                NotificationService.create_notification(
                    user=farmer,
                    title=f"Action requise : Commande #{order.id} en attente depuis {(timezone.now() - order.created_at).days} jours",
                    message=f"""Bonjour {farmer.username},
                    
Une commande #{order.id} contenant votre produit "{item.product.name}" est en attente de confirmation.
Veuillez la traiter rapidement pour assurer la satisfaction client.

L'équipe Farmer Market""",
                    order=order
                )
        
        return len(pending_orders)
    
    @staticmethod
    def check_pickup_dates():
        """Vérifie les commandes dont la date de retrait est passée"""
        from products.models.models import Order
        from django.utils import timezone
        
        # Commandes confirmées dont la date de retrait est passée
        overdue_orders = Order.objects.filter(
            status='confirmed',
            pickup_date__lt=timezone.now()
        )
        
        for order in overdue_orders:
            # Mettre à jour le statut
            OrderService.update_order_status(order, 'ready')
        
        # Commandes prêtes non récupérées depuis plus de 3 jours
        uncollected_threshold = timezone.now() - timezone.timedelta(days=3)
        uncollected_orders = Order.objects.filter(
            status='ready',
            pickup_date__lt=uncollected_threshold
        )
        
        for order in uncollected_orders:
            NotificationService.create_notification(
                user=order.customer,
                title=f"Rappel : Votre commande #{order.id} vous attend",
                message=f"""Bonjour {order.customer.username},
                
Nous vous rappelons que votre commande #{order.id} est prête à être récupérée depuis le {order.pickup_date.strftime('%d/%m/%Y')}.
Si vous ne pouvez pas venir la chercher, merci de nous contacter.

Cordialement,
L'équipe Farmer Market""",
                order=order
            )
        
        return len(overdue_orders) + len(uncollected_orders)

class ReviewService:
    """Service pour la gestion des avis et des notations"""
    
    @staticmethod
    def add_review(user, product, rating, title, comment):
        """Ajoute un nouvel avis ou met à jour un avis existant"""
        try:
            # Vérifier si l'utilisateur a déjà laissé un avis pour ce produit
            existing_review = Review.objects.filter(user=user, product=product).first()
            
            if existing_review:
                # Mettre à jour l'avis existant
                existing_review.rating = rating
                existing_review.title = title
                existing_review.comment = comment
                existing_review.save()
                logger.info(f"Avis mis à jour par {user.username} pour {product.name}")
                return existing_review
            else:
                # Créer un nouvel avis
                review = Review.objects.create(
                    user=user,
                    product=product,
                    rating=rating,
                    title=title,
                    comment=comment
                )
                logger.info(f"Nouvel avis ajouté par {user.username} pour {product.name}")
                
                # Notifier le fermier du nouvel avis
                NotificationService.create_notification(
                    user=product.farmer,
                    title=f"Nouvel avis sur votre produit {product.name}",
                    message=f"""Bonjour {product.farmer.username},
                    
Un client vient de laisser un avis sur votre produit "{product.name}".
Note : {rating}/5
Titre : {title}
Commentaire : {comment}

Bonne journée,
L'équipe Farmer Market"""
                )
                
                return review
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout/mise à jour de l'avis : {str(e)}")
            return None
    
    @staticmethod
    def can_review_product(user, product):
        """Vérifie si l'utilisateur peut laisser un avis sur ce produit"""
        # Vérifier si l'utilisateur n'est pas le fermier du produit
        if user == product.farmer:
            return False
        
        # Vérifier si l'utilisateur n'a pas déjà laissé un avis pour ce produit
        review_count = Review.objects.filter(user=user, product=product).count()
        
        return review_count < 1  # Un seul avis par utilisateur et par produit
    
    @staticmethod
    def get_product_average_rating(product):
        """Calcule la note moyenne d'un produit"""
        avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))
        return avg_rating['rating__avg'] or 0
    
    @staticmethod
    def get_farmer_average_rating(farmer):
        """Calcule la note moyenne d'un fermier (moyenne des notes de ses produits)"""
        avg_rating = Review.objects.filter(product__farmer=farmer).aggregate(Avg('rating'))
        return avg_rating['rating__avg'] or 0
    
    @staticmethod
    def get_top_rated_products(limit=5, min_reviews=3):
        """Récupère les produits les mieux notés avec un minimum d'avis"""
        from django.db.models import Count
        return product.Product.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gte=min_reviews).order_by('-avg_rating')[:limit]

class PickupService:
    """Service pour la gestion des créneaux horaires et des rendez-vous de retrait"""
    
    @staticmethod
    def create_time_slot(farmer, weekday, start_time, end_time, max_orders=5, location='', active=True):
        """Crée un nouveau créneau horaire pour un fermier"""
        try:
            time_slot = AvailabilityTimeSlot.objects.create(
                farmer=farmer,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                max_orders=max_orders,
                location=location or getattr(farmer.profile, 'address', 'À confirmer'),
                active=active
            )
            logger.info(f"Nouveau créneau horaire créé: {time_slot}")
            return time_slot
        except Exception as e:
            logger.error(f"Erreur lors de la création du créneau horaire: {str(e)}")
            return None
    
    @staticmethod
    def get_available_slots_for_farmer(farmer, active_only=True):
        """Récupère tous les créneaux horaires d'un fermier"""
        query = AvailabilityTimeSlot.objects.filter(farmer=farmer)
        if active_only:
            query = query.filter(active=True)
        return query.order_by('weekday', 'start_time')
    
    @staticmethod
    def get_available_slots_for_order(order):
        """Récupère les créneaux disponibles pour une commande"""
        # Récupérer les fermiers concernés par la commande
        farmers_ids = order.items.values_list('product__farmer', flat=True).distinct()
        
        # Récupérer les créneaux actifs pour ces fermiers
        slots = AvailabilityTimeSlot.objects.filter(
            farmer__in=farmers_ids,
            active=True
        ).annotate(
            appointments_count=Count('appointments')
        ).filter(
            appointments_count__lt=F('max_orders')
        ).order_by('weekday', 'start_time')
        
        return slots
    
    @staticmethod
    def schedule_pickup(order, availability_slot, pickup_date):
        """Planifie un rendez-vous de retrait pour une commande"""
        try:
            # Vérifier que le créneau est disponible pour cette date
            if not availability_slot.is_available_for_date(pickup_date):
                logger.warning(f"Le créneau n'est pas disponible pour la date {pickup_date}")
                return None
            
            # Vérifier si la commande a déjà un rendez-vous
            existing_appointment = PickupAppointment.objects.filter(order=order).first()
            if existing_appointment:
                # Mettre à jour le rendez-vous existant
                existing_appointment.availability_slot = availability_slot
                existing_appointment.pickup_date = pickup_date
                existing_appointment.save()
                appointment = existing_appointment
                logger.info(f"Rendez-vous mis à jour: {appointment}")
            else:
                # Créer un nouveau rendez-vous
                appointment = PickupAppointment.objects.create(
                    order=order,
                    availability_slot=availability_slot,
                    pickup_date=pickup_date
                )
                logger.info(f"Nouveau rendez-vous créé: {appointment}")
            
            # Notifier le client
            NotificationService.create_notification(
                user=order.customer,
                title=f"Rendez-vous de retrait confirmé pour la commande #{order.id}",
                message=f"""Bonjour {order.customer.username},
                
Votre rendez-vous de retrait a été confirmé pour la commande #{order.id}.

Date: {pickup_date.strftime('%d/%m/%Y')}
Horaire: {availability_slot.start_time.strftime('%H:%M')} - {availability_slot.end_time.strftime('%H:%M')}
Lieu: {availability_slot.location}

À bientôt,
L'équipe Farmer Market""",
                order=order
            )
            
            return appointment
            
        except Exception as e:
            logger.error(f"Erreur lors de la planification du rendez-vous: {str(e)}")
            return None

class ReportService:
    """Service pour la génération et l'envoi de rapports"""
    
    @staticmethod
    def generate_sales_report(farmer, start_date, end_date):
        """Génère un rapport de ventes pour un fermier sur une période donnée"""
        from products.models.models import OrderItem
        from django.db.models import Sum, Count
        
        # Récupérer toutes les ventes du fermier sur la période
        sales = OrderItem.objects.filter(
            product__farmer=farmer,
            order__status__in=['completed', 'ready'],
            order__created_at__gte=start_date,
            order__created_at__lte=end_date
        ).select_related('product', 'order')
        
        # Statistiques globales
        total_revenue = sales.aggregate(Sum('price'))['price__sum'] or 0
        total_orders = sales.values('order').distinct().count()
        total_products_sold = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        # Produits les plus vendus
        top_products = sales.values('product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum('price')
        ).order_by('-total_sold')[:5]
        
        # Tendance des ventes par jour
        daily_sales = sales.extra(
            select={'day': "date(created_at)"}
        ).values('day').annotate(
            revenue=Sum('price'),
            quantity=Sum('quantity')
        ).order_by('day')
        
        # Créer le rapport
        report = {
            'farmer': farmer,
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_products_sold': total_products_sold,
            'top_products': list(top_products),
            'daily_sales': list(daily_sales)
        }
        
        return report
    
    @staticmethod
    def generate_pdf_report(report_data):
        """Génère un fichier PDF à partir des données du rapport"""
        import tempfile
        from django.template.loader import render_to_string
        from datetime import datetime
        import pdfkit
        
        # Créer un fichier temporaire pour le PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Générer le contenu HTML du rapport
            html_content = render_to_string('reports/sales_report.html', {
                'report': report_data,
                'generation_date': datetime.now()
            })
            
            # Convertir le HTML en PDF
            pdfkit.from_string(
                html_content, 
                temp_file.name, 
                options={
                    'page-size': 'A4',
                    'encoding': 'UTF-8',
                    'margin-top': '1cm',
                    'margin-right': '1cm',
                    'margin-bottom': '1cm',
                    'margin-left': '1cm',
                }
            )
            
            return temp_file.name
    
    @staticmethod
    def generate_weekly_sales_reports(start_date, end_date):
        """Génère et envoie les rapports hebdomadaires pour tous les fermiers"""
        from accounts.models import User
        
        # Récupérer tous les utilisateurs qui sont des fermiers
        farmers = User.objects.filter(profile__is_farmer=True)
        report_count = 0
        
        for farmer in farmers:
            # Générer le rapport
            report_data = ReportService.generate_sales_report(farmer, start_date, end_date)
            
            # Si le fermier a des ventes sur cette période
            if report_data['total_orders'] > 0:
                # Générer le PDF
                pdf_path = ReportService.generate_pdf_report(report_data)
                
                # Créer une notification pour le fermier
                notification = NotificationService.create_notification(
                    user=farmer,
                    title=f"Votre rapport de ventes du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
                    message=f"""Bonjour {farmer.username},
                    
Votre rapport hebdomadaire de ventes est disponible. Vous y trouverez un résumé de vos ventes pour la semaine du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}.

Résumé:
- Nombre de commandes: {report_data['total_orders']}
- Produits vendus: {report_data['total_products_sold']}
- Chiffre d'affaires: {report_data['total_revenue']}€

Vous pouvez consulter le rapport complet en pièce jointe ou sur votre tableau de bord.

L'équipe Farmer Market"""
                )
                
                # Envoyer l'email avec le PDF en pièce jointe
                from django.core.mail import EmailMessage
                from django.conf import settings
                import os
                
                email = EmailMessage(
                    subject=f"Rapport de ventes Farmer Market - Semaine du {start_date.strftime('%d/%m/%Y')}",
                    body=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[farmer.email]
                )
                
                # Ajouter la pièce jointe
                with open(pdf_path, 'rb') as f:
                    email.attach(
                        f"rapport_ventes_{start_date.strftime('%Y%m%d')}_au_{end_date.strftime('%Y%m%d')}.pdf",
                        f.read(),
                        'application/pdf'
                    )
                
                # Envoyer l'email
                email.send()
                
                # Supprimer le fichier temporaire
                os.unlink(pdf_path)
                
                report_count += 1
        
        return report_count

class PaymentService:
    """Service pour la gestion des paiements"""
    
    @staticmethod
    def process_payment(order, payment_method, payment_details):
        """Traite un paiement pour une commande"""
        import stripe
        from django.conf import settings
        
        # Configurer Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            if payment_method == 'card':
                # Créer une session de paiement Stripe
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': f'Commande #{order.id}',
                            },
                            'unit_amount': int(order.total_amount * 100),  # Stripe utilise des centimes
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f'https://votre-site.com/checkout/success?order_id={order.id}',
                    cancel_url=f'https://votre-site.com/checkout/cancel?order_id={order.id}',
                )
                
                # Mettre à jour la commande avec l'ID de session Stripe
                order.payment_status = 'processing'
                order.metadata = {'stripe_session_id': session.id}
                order.save()
                
                return {
                    'success': True,
                    'redirect_url': session.url
                }
            
            elif payment_method == 'transfer':
                # Générer les informations de virement
                order.payment_status = 'processing'
                order.payment_method = 'transfer'
                order.save()
                
                # Envoyer les informations de virement par email
                NotificationService.create_notification(
                    user=order.customer,
                    title=f"Instructions de paiement pour votre commande #{order.id}",
                    message=f"""Bonjour {order.customer.username},
                    
Pour finaliser votre commande #{order.id}, veuillez effectuer un virement bancaire avec les informations suivantes:

Montant: {order.total_amount}€
Référence: FM-{order.id}
IBAN: FR7630001007941234567890185
BIC: BDFEFRPPXXX
Bénéficiaire: Farmer Market

Une fois le virement effectué, votre commande sera confirmée dès réception du paiement.

L'équipe Farmer Market""",
                    order=order
                )
                
                return {
                    'success': True,
                    'message': 'Instructions de paiement envoyées par email'
                }
            
            else:
                return {
                    'success': False,
                    'error': 'Méthode de paiement non supportée'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du paiement: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def confirm_payment(order_id, payment_details=None):
        """Confirme le paiement d'une commande"""
        from products.models.models import Order
        
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = 'paid'
            order.payment_date = timezone.now()
            order.save()
            
            # Si la commande est toujours en attente, la confirmer
            if order.status == 'pending':
                OrderService.update_order_status(order, 'confirmed')
            
            # Envoyer une notification de confirmation
            NotificationService.create_notification(
                user=order.customer,
                title=f"Paiement confirmé pour votre commande #{order.id}",
                message=f"""Bonjour {order.customer.username},
                
Nous avons bien reçu votre paiement pour la commande #{order.id}. 
Vous recevrez une notification dès que votre commande sera prête à être récupérée.

Merci pour votre achat,
L'équipe Farmer Market""",
                order=order
            )
            
            return True
        except Order.DoesNotExist:
            logger.error(f"Commande introuvable lors de la confirmation du paiement: {order_id}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la confirmation du paiement: {str(e)}")
            return False
    
    @staticmethod
    def generate_invoice(order):
        """Génère une facture au format PDF pour une commande"""
        import tempfile
        from django.template.loader import render_to_string
        import pdfkit
        from django.conf import settings
        import os
        
        # Créer un fichier temporaire pour le PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Générer le contenu HTML de la facture
            html_content = render_to_string('invoices/invoice.html', {
                'order': order,
                'company': {
                    'name': 'Farmer Market',
                    'address': '123 Rue des Fermiers, 75000 Paris',
                    'phone': '+33 1 23 45 67 89',
                    'email': 'contact@farmermarket.com',
                    'website': 'www.farmermarket.com',
                    'vat_number': 'FR12345678901'
                }
            })
            
            # Convertir le HTML en PDF
            pdfkit.from_string(
                html_content, 
                temp_file.name, 
                options={
                    'page-size': 'A4',
                    'encoding': 'UTF-8',
                }
            )
            
            # Créer le dossier des factures s'il n'existe pas
            invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
            os.makedirs(invoice_dir, exist_ok=True)
            
            # Déplacer le fichier temporaire vers le dossier de destination
            invoice_path = os.path.join(invoice_dir, f"facture_{order.reference_number}.pdf")
            os.rename(temp_file.name, invoice_path)
            
            # Mettre à jour l'ordre avec le chemin de la facture
            relative_path = os.path.join('invoices', f"facture_{order.reference_number}.pdf")
            order.invoice = relative_path
            order.save()
            
            return relative_path 