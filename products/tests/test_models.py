from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from products.models.product import Product, Category
from products.models.models import Order, OrderItem, Cart, CartItem, Review, Notification

User = get_user_model()

class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Légumes",
            slug="legumes",
            description="Légumes frais"
        )

    def test_category_creation(self):
        """Test de la création d'une catégorie"""
        self.assertEqual(self.category.name, "Légumes")
        self.assertEqual(self.category.slug, "legumes")
        self.assertEqual(str(self.category), "Légumes")

class ProductModelTests(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
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
            farmer=self.user,
            stock=10
        )

    def test_product_creation(self):
        """Test de la création d'un produit"""
        self.assertEqual(self.product.name, "Carottes")
        self.assertEqual(self.product.price, 2.50)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.farmer, self.user)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(str(self.product), "Carottes")

    def test_get_image_url(self):
        """Test de la méthode get_image_url"""
        # Sans image
        self.assertEqual(self.product.get_image_url(), '/static/images/default-image.jpg')
        
        # Avec une image (simulation)
        # Note: Un test plus complet nécessiterait de mocker l'upload de fichier
        self.product.image = 'test.jpg'
        self.assertEqual(self.product.get_image_url(), 'test.jpg')

    def test_get_average_rating(self):
        """Test de la méthode get_average_rating"""
        # Sans avis
        self.assertEqual(self.product.get_average_rating(), 0)
        
        # Créer un client pour laisser un avis
        client = User.objects.create_user(
            username="client",
            email="client@gmail.com",
            password="password123"
        )
        
        # Ajouter des avis
        Review.objects.create(product=self.product, user=client, rating=4, title="Bon", comment="Très bon produit")
        Review.objects.create(product=self.product, user=self.user, rating=5, title="Excellent", comment="Excellente qualité")
        
        # Vérifier la moyenne
        self.assertEqual(self.product.get_average_rating(), 4.5)

class OrderModelTests(TestCase):
    def setUp(self):
        # Créer un client
        self.client_user = User.objects.create_user(
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
            customer=self.client_user,
            status='pending',
            pickup_date=timezone.now() + timezone.timedelta(days=1),
            pickup_time_slot="14:00 - 16:00",
            total_amount=0
        )
        
        # Ajouter un article à la commande
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )
        
        # Mettre à jour le total de la commande
        self.order.calculate_total()

    def test_order_creation(self):
        """Test de la création d'une commande"""
        self.assertEqual(self.order.customer, self.client_user)
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(str(self.order), f"Commande #{self.order.id} - {self.client_user.username}")

    def test_calculate_total(self):
        """Test de la méthode calculate_total"""
        expected_total = self.product.price * 2  # 2.50 * 2 = 5.00
        self.assertEqual(self.order.total_amount, expected_total)
        
        # Ajouter un autre article et recalculer
        product2 = Product.objects.create(
            name="Tomates",
            description="Tomates fraîches",
            price=3.00,
            category=self.category,
            farmer=self.farmer,
            stock=5
        )
        
        OrderItem.objects.create(
            order=self.order,
            product=product2,
            quantity=1,
            price=product2.price
        )
        
        new_total = self.order.calculate_total()
        expected_new_total = (self.product.price * 2) + (product2.price * 1)  # 5.00 + 3.00 = 8.00
        self.assertEqual(new_total, expected_new_total)
        self.assertEqual(self.order.total_amount, expected_new_total)

    def test_order_validation(self):
        """Test de la validation de la commande"""
        # Date de retrait dans le passé
        past_order = Order(
            customer=self.client_user,
            pickup_date=timezone.now() - timezone.timedelta(days=1),
            status='pending'
        )
        
        with self.assertRaises(ValidationError):
            past_order.clean()

class NotificationModelTests(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username="client",
            email="client@gmail.com",
            password="password123"
        )
        
        # Créer une notification
        self.notification = Notification.objects.create(
            user=self.user,
            title="Test de notification",
            message="Ceci est un test de notification.",
            notification_type='email',
            status='pending'
        )

    def test_notification_creation(self):
        """Test de la création d'une notification"""
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.title, "Test de notification")
        self.assertEqual(self.notification.status, 'pending')
        self.assertEqual(str(self.notification), f"Notification à {self.user.username}: Test de notification")

    def test_mark_as_sent(self):
        """Test de la méthode mark_as_sent"""
        self.notification.mark_as_sent()
        self.assertEqual(self.notification.status, 'sent')
        self.assertIsNotNone(self.notification.sent_at)

    def test_mark_as_read(self):
        """Test de la méthode mark_as_read"""
        self.notification.mark_as_read()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)

class CartModelTests(TestCase):
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
        
        # Créer un panier
        self.cart = Cart.objects.create(user=self.user)
        
        # Ajouter des articles au panier
        self.cart_item1 = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        self.cart_item2 = CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )

    def test_cart_creation(self):
        """Test de la création d'un panier"""
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.items.count(), 2)
        self.assertEqual(str(self.cart), f"Panier de {self.user.username}")

    def test_get_total_cost(self):
        """Test de la méthode get_total_cost"""
        expected_total = (self.product1.price * 2) + (self.product2.price * 1)  # 2.50*2 + 3.00 = 8.00
        self.assertEqual(self.cart.get_total_cost(), expected_total)
        
        # Modifier la quantité d'un article
        self.cart_item1.quantity = 3
        self.cart_item1.save()
        
        new_expected_total = (self.product1.price * 3) + (self.product2.price * 1)  # 2.50*3 + 3.00 = 10.50
        self.assertEqual(self.cart.get_total_cost(), new_expected_total)

    def test_clear(self):
        """Test de la méthode clear"""
        self.cart.clear()
        self.assertEqual(self.cart.items.count(), 0) 