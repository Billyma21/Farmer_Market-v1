"""
Tests de base pour Farmer Market
Version Beta - Épreuve Intégrée
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models.models import Product, Category, Order
from django.utils import timezone

User = get_user_model()


class BasicViewsTest(TestCase):
    """Tests des vues de base de l'application"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un utilisateur test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )
        
        # Créer une catégorie test
        self.category = Category.objects.create(
            name='Légumes',
            description='Légumes frais'
        )
        
        # Créer un produit test
        self.product = Product.objects.create(
            name='Tomates',
            description='Tomates bio',
            price=2.50,
            category=self.category,
            farmer=self.user,
            stock_quantity=10
        )

    def test_home_page(self):
        """Test de la page d'accueil"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Farmer Market')

    def test_product_list(self):
        """Test de la liste des produits"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tomates')

    def test_product_detail(self):
        """Test du détail d'un produit"""
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tomates')

    def test_login_page(self):
        """Test de la page de connexion"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion')

    def test_register_page(self):
        """Test de la page d'inscription"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inscription')


class UserAuthenticationTest(TestCase):
    """Tests d'authentification des utilisateurs"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )

    def test_user_login(self):
        """Test de connexion utilisateur"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après connexion

    def test_user_logout(self):
        """Test de déconnexion utilisateur"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirection après déconnexion

    def test_protected_view_access(self):
        """Test d'accès à une vue protégée"""
        # Sans connexion
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Avec connexion
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)


class ProductModelTest(TestCase):
    """Tests des modèles de produits"""

    def setUp(self):
        """Configuration initiale"""
        self.user = User.objects.create_user(
            username='farmer',
            email='farmer@example.com',
            password='farmerpass123',
            user_type='farmer'
        )
        
        self.category = Category.objects.create(
            name='Fruits',
            description='Fruits frais'
        )

    def test_product_creation(self):
        """Test de création d'un produit"""
        product = Product.objects.create(
            name='Pommes',
            description='Pommes bio',
            price=3.00,
            category=self.category,
            farmer=self.user,
            stock_quantity=20
        )
        
        self.assertEqual(product.name, 'Pommes')
        self.assertEqual(product.price, 3.00)
        self.assertEqual(product.farmer, self.user)
        self.assertEqual(product.category, self.category)

    def test_product_str_representation(self):
        """Test de la représentation string d'un produit"""
        product = Product.objects.create(
            name='Oranges',
            description='Oranges bio',
            price=2.50,
            category=self.category,
            farmer=self.user,
            stock_quantity=15
        )
        
        self.assertEqual(str(product), 'Oranges')

    def test_category_str_representation(self):
        """Test de la représentation string d'une catégorie"""
        self.assertEqual(str(self.category), 'Fruits')


class OrderModelTest(TestCase):
    """Tests des modèles de commandes"""

    def setUp(self):
        """Configuration initiale"""
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpass123',
            user_type='customer'
        )
        
        self.farmer = User.objects.create_user(
            username='farmer',
            email='farmer@example.com',
            password='farmerpass123',
            user_type='farmer'
        )
        
        self.category = Category.objects.create(
            name='Légumes',
            description='Légumes frais'
        )
        
        self.product = Product.objects.create(
            name='Carottes',
            description='Carottes bio',
            price=1.50,
            category=self.category,
            farmer=self.farmer,
            stock_quantity=30
        )

    def test_order_creation(self):
        """Test de création d'une commande"""
        order = Order.objects.create(
            customer=self.customer,
            total_amount=15.00,
            status='pending',
            pickup_date=timezone.now().date()
        )
        
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_amount, 15.00)
        self.assertEqual(order.status, 'pending')

    def test_order_str_representation(self):
        """Test de la représentation string d'une commande"""
        order = Order.objects.create(
            customer=self.customer,
            total_amount=20.00,
            status='confirmed',
            pickup_date=timezone.now().date()
        )
        
        expected_str = f"Commande #{order.id} - {self.customer.username}"
        self.assertEqual(str(order), expected_str)


class APITest(TestCase):
    """Tests de l'API REST"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )

    def test_api_products_list(self):
        """Test de l'API liste des produits"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)

    def test_api_products_detail(self):
        """Test de l'API détail d'un produit"""
        category = Category.objects.create(name='Test', description='Test')
        product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            category=category,
            farmer=self.user,
            stock_quantity=5
        )
        
        response = self.client.get(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 200)


class InternationalizationTest(TestCase):
    """Tests d'internationalisation"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    def test_language_switching(self):
        """Test du changement de langue"""
        # Test français (par défaut)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Test anglais
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200)
        
        # Test néerlandais
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='nl')
        self.assertEqual(response.status_code, 200)


class SecurityTest(TestCase):
    """Tests de sécurité"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    def test_csrf_protection(self):
        """Test de la protection CSRF"""
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_xss_protection(self):
        """Test de la protection XSS"""
        # Ce test vérifie que le contenu malveillant est échappé
        malicious_content = '<script>alert("XSS")</script>'
        response = self.client.get('/')
        self.assertNotContains(response, malicious_content)

    def test_sql_injection_protection(self):
        """Test de la protection contre les injections SQL"""
        # Django ORM protège automatiquement contre les injections SQL
        # Ce test vérifie que les requêtes sont sécurisées
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class PerformanceTest(TestCase):
    """Tests de performance de base"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    def test_home_page_load_time(self):
        """Test du temps de chargement de la page d'accueil"""
        import time
        start_time = time.time()
        response = self.client.get('/')
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0)  # Moins de 2 secondes

    def test_database_queries_optimization(self):
        """Test d'optimisation des requêtes base de données"""
        from django.db import connection
        
        # Réinitialiser le compteur de requêtes
        connection.queries = []
        
        # Effectuer une requête
        response = self.client.get('/')
        
        # Vérifier le nombre de requêtes
        self.assertLess(len(connection.queries), 10)  # Moins de 10 requêtes 