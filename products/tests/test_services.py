from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import timedelta

from products.models.product import Product, Category
from products.models.models import Order, OrderItem, Review, Notification
from products.services import NotificationService, OrderService, ReviewService, ReportService

User = get_user_model()

class NotificationServiceTests(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username="client",
            email="client@gmail.com",
            password="password123"
        )
        
        # Créer un fermier
        self.farmer = User.objects.create_user(
            username="fermier",
            email="fermier@gmail.com",
            password="password123"
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name="Légumes",
            slug="legumes",
            description="Légumes frais"
        )
        
        # Créer un produit
        self.product = Product.objects.create(
            name="Carottes",
            description="Carottes fraîches",
            price=2.50,
            category=self.category,
            farmer=self.farmer,
            stock=10
        )
        
        # Créer une commande
        self.order = Order.objects.create(
            customer=self.user,
            status='pending',
            pickup_date=timezone.now() + timezone.timedelta(days=1),
            pickup_time_slot="14:00 - 16:00"
        )
        
        # Ajouter un article à la commande
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    def test_create_notification(self):
        """Test de la création d'une notification"""
        notification = NotificationService.create_notification(
            user=self.user,
            title="Test de notification",
            message="Ceci est un test de notification.",
            notification_type='email',
            order=self.order
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, "Test de notification")
        self.assertEqual(notification.notification_type, 'email')
        self.assertEqual(notification.status, 'pending')
        self.assertEqual(notification.order, self.order)
    
    @patch('products.services.send_mail')
    def test_send_email_notification(self, mock_send_mail):
        """Test de l'envoi d'une notification par email"""
        # Créer une notification
        notification = NotificationService.create_notification(
            user=self.user,
            title="Test de notification",
            message="Ceci est un test de notification.",
            notification_type='email'
        )
        
        # Configurer le mock
        mock_send_mail.return_value = 1
        
        # Appeler la méthode à tester
        result = NotificationService.send_email_notification(notification)
        
        # Vérifier que la méthode send_mail a été appelée avec les bons paramètres
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertEqual(kwargs['subject'], "Test de notification")
        self.assertEqual(kwargs['message'], "Ceci est un test de notification.")
        self.assertEqual(kwargs['recipient_list'], [self.user.email])
        
        # Vérifier le résultat et le statut de la notification
        self.assertTrue(result)
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'sent')
    
    def test_process_pending_notifications(self):
        """Test du traitement des notifications en attente"""
        # Créer plusieurs notifications en attente
        notification1 = NotificationService.create_notification(
            user=self.user,
            title="Notification 1",
            message="Message 1",
            notification_type='email'
        )
        
        notification2 = NotificationService.create_notification(
            user=self.farmer,
            title="Notification 2",
            message="Message 2",
            notification_type='in_app'
        )
        
        # Mocker les méthodes d'envoi
        with patch.object(NotificationService, 'send_email_notification', return_value=True) as mock_email:
            NotificationService.process_pending_notifications()
            
            # Vérifier que send_email_notification a été appelée pour la notification email
            mock_email.assert_called_once()
            self.assertEqual(mock_email.call_args[0][0], notification1)
            
            # Vérifier le statut des notifications
            notification1.refresh_from_db()
            notification2.refresh_from_db()
            self.assertEqual(notification1.status, 'sent')  # Email envoyé
            self.assertEqual(notification2.status, 'pending')  # Notification in_app non traitée

class OrderServiceTests(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username="client",
            email="client@gmail.com",
            password="password123"
        )
        
        # Créer un fermier
        self.farmer = User.objects.create_user(
            username="fermier",
            email="fermier@gmail.com",
            password="password123"
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name="Légumes",
            slug="legumes",
            description="Légumes frais"
        )
        
        # Créer un produit
        self.product = Product.objects.create(
            name="Carottes",
            description="Carottes fraîches",
            price=2.50,
            category=self.category,
            farmer=self.farmer,
            stock=10
        )
        
        # Créer une commande
        self.order = Order.objects.create(
            customer=self.user,
            status='pending',
            pickup_date=timezone.now() + timezone.timedelta(days=1),
            pickup_time_slot="14:00 - 16:00"
        )
        
        # Ajouter un article à la commande
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    @patch.object(NotificationService, 'notify_order_status_change')
    def test_update_order_status(self, mock_notify):
        """Test de la mise à jour du statut d'une commande"""
        # Statut initial
        self.assertEqual(self.order.status, 'pending')
        
        # Transition valide : pending -> confirmed
        result = OrderService.update_order_status(self.order, 'confirmed')
        self.assertTrue(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')
        mock_notify.assert_called_once_with(self.order, 'pending')
        
        # Réinitialiser le mock
        mock_notify.reset_mock()
        
        # Transition valide : confirmed -> ready
        result = OrderService.update_order_status(self.order, 'ready')
        self.assertTrue(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'ready')
        mock_notify.assert_called_once_with(self.order, 'confirmed')
        
        # Réinitialiser le mock
        mock_notify.reset_mock()
        
        # Transition invalide : ready -> pending
        result = OrderService.update_order_status(self.order, 'pending')
        self.assertFalse(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'ready')  # Le statut ne change pas
        mock_notify.assert_not_called()

    @patch.object(NotificationService, 'create_notification')
    def test_check_pending_orders(self, mock_create_notification):
        """Test de la vérification des commandes en attente"""
        # Créer une commande en attente depuis 48h
        old_order = Order.objects.create(
            customer=self.user,
            status='pending',
            created_at=timezone.now() - timedelta(hours=49)
        )
        
        # Ajouter un article à la commande
        OrderItem.objects.create(
            order=old_order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
        
        # Définir le seuil à 48h
        time_threshold = timezone.now() - timedelta(hours=48)
        
        # Appeler la méthode à tester
        result = OrderService.check_pending_orders(time_threshold)
        
        # Vérifier que la méthode a trouvé 1 commande en attente
        self.assertEqual(result, 1)
        
        # Vérifier que create_notification a été appelée 2 fois (une pour le client, une pour le fermier)
        self.assertEqual(mock_create_notification.call_count, 2)

class ReviewServiceTests(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username="client",
            email="client@gmail.com",
            password="password123"
        )
        
        # Créer un fermier
        self.farmer = User.objects.create_user(
            username="fermier",
            email="fermier@gmail.com",
            password="password123"
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name="Légumes",
            slug="legumes",
            description="Légumes frais"
        )
        
        # Créer un produit
        self.product = Product.objects.create(
            name="Carottes",
            description="Carottes fraîches",
            price=2.50,
            category=self.category,
            farmer=self.farmer,
            stock=10
        )

    def test_add_review(self):
        """Test de l'ajout d'un avis"""
        # Créer un avis
        review_data = {
            'rating': 4,
            'title': 'Très bon produit',
            'comment': 'Les carottes sont fraîches et délicieuses.'
        }
        
        result = ReviewService.add_review(
            user=self.user,
            product=self.product,
            rating=review_data['rating'],
            title=review_data['title'],
            comment=review_data['comment']
        )
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['review'])
        
        # Vérifier que l'avis a été créé en base
        review = Review.objects.filter(user=self.user, product=self.product).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, review_data['rating'])
        self.assertEqual(review.title, review_data['title'])
        
        # Tester l'ajout d'un deuxième avis (doit échouer)
        result2 = ReviewService.add_review(
            user=self.user,
            product=self.product,
            rating=5,
            title='Avis mis à jour',
            comment='Commentaire mis à jour'
        )
        
        # Vérifier que l'ajout a échoué (un seul avis par produit et utilisateur)
        self.assertFalse(result2['success'])
        self.assertEqual(result2['error'], 'Vous avez déjà laissé un avis pour ce produit.')
        
        # Vérifier qu'il n'y a toujours qu'un seul avis
        self.assertEqual(Review.objects.filter(user=self.user, product=self.product).count(), 1)

class ReportServiceTests(TestCase):
    def setUp(self):
        # Créer un fermier
        self.farmer = User.objects.create_user(
            username="fermier",
            email="fermier@gmail.com",
            password="password123"
        )
        
        # Créer un client
        self.client_user = User.objects.create_user(
            username="client",
            email="client@gmail.com",
            password="password123"
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name="Légumes",
            slug="legumes",
            description="Légumes frais"
        )
        
        # Créer des produits
        self.product1 = Product.objects.create(
            name="Carottes",
            description="Carottes fraîches",
            price=2.50,
            category=self.category,
            farmer=self.farmer,
            stock=10
        )
        
        self.product2 = Product.objects.create(
            name="Tomates",
            description="Tomates fraîches",
            price=3.00,
            category=self.category,
            farmer=self.farmer,
            stock=5
        )
        
        # Créer des commandes complétées
        self.order1 = Order.objects.create(
            customer=self.client_user,
            status='completed',
            created_at=timezone.now() - timedelta(days=2)
        )
        
        OrderItem.objects.create(
            order=self.order1,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        
        self.order2 = Order.objects.create(
            customer=self.client_user,
            status='completed',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        OrderItem.objects.create(
            order=self.order2,
            product=self.product2,
            quantity=1,
            price=self.product2.price
        )

    def test_generate_sales_report(self):
        """Test de la génération d'un rapport de ventes"""
        # Définir la période du rapport
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Générer le rapport
        report = ReportService.generate_sales_report(
            farmer=self.farmer,
            start_date=start_date,
            end_date=end_date
        )
        
        # Vérifier les données du rapport
        self.assertEqual(report['farmer'], self.farmer)
        self.assertEqual(report['start_date'], start_date)
        self.assertEqual(report['end_date'], end_date)
        
        # Vérifier les statistiques globales
        expected_revenue = (self.product1.price * 2) + (self.product2.price * 1)  # 2.50*2 + 3.00 = 8.00
        self.assertEqual(report['total_revenue'], expected_revenue)
        self.assertEqual(report['total_orders'], 2)
        self.assertEqual(report['total_products_sold'], 3)  # 2 carottes + 1 tomate
        
        # Vérifier les produits les plus vendus
        self.assertEqual(len(report['top_products']), 2)
        
        # Le rapport contient les deux produits, mais le tri peut varier
        product_names = [p['product__name'] for p in report['top_products']]
        self.assertIn('Carottes', product_names)
        self.assertIn('Tomates', product_names)

    @patch('products.services.pdfkit')
    def test_generate_pdf_report(self, mock_pdfkit):
        """Test de la génération d'un rapport PDF"""
        # Créer des données de rapport fictives
        report_data = {
            'farmer': self.farmer,
            'start_date': timezone.now().date() - timedelta(days=7),
            'end_date': timezone.now().date(),
            'total_revenue': 100.0,
            'total_orders': 10,
            'total_products_sold': 25,
            'top_products': [],
            'daily_sales': []
        }
        
        # Mocker la fonction from_string
        mock_pdfkit.from_string.return_value = True
        
        # Générer le PDF
        with patch('builtins.open', create=True) as mock_open:
            file_mock = MagicMock()
            mock_open.return_value.__enter__.return_value = file_mock
            
            pdf_path = ReportService.generate_pdf_report(report_data)
            
            # Vérifier que la fonction from_string a été appelée
            mock_pdfkit.from_string.assert_called_once()
            
            # Vérifier que le chemin du fichier PDF est retourné
            self.assertIsNotNone(pdf_path)
            self.assertTrue(pdf_path.endswith('.pdf')) 