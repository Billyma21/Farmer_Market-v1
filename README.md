# 🌾 Farmer Market - Plateforme de Vente Directe de Produits Fermiers

## 📋 Description du Projet

**Farmer Market** est une plateforme web multilingue (français, anglais, néerlandais) de vente directe de produits fermiers locaux. Cette application Django moderne permet aux fermiers de vendre leurs produits directement aux consommateurs, avec un système de commande, de paiement sécurisé et de gestion complète.

## ✨ Fonctionnalités Principales

### 🛒 Pour les Consommateurs
- **Catalogue de produits** avec filtres et recherche avancée
- **Système de panier** avec gestion des quantités
- **Paiement sécurisé** via Stripe
- **Système d'avis et notes** sur les produits
- **Gestion des commandes** avec suivi en temps réel
- **Rendez-vous de retrait** avec créneaux horaires
- **Notifications** par email et dans l'application

### 👨‍🌾 Pour les Fermiers
- **Dashboard complet** avec statistiques de vente
- **Gestion des produits** (ajout, modification, suppression)
- **Gestion des commandes** avec mise à jour des statuts
- **Rapports de vente** avec export PDF
- **Gestion des créneaux de retrait**
- **Réponses aux avis clients**

### 🗺️ Fonctionnalités Avancées
- **Carte interactive** avec localisation des fermiers
- **API RESTful** complète pour intégration mobile
- **Système de logging** pour audit d'activité
- **Internationalisation** complète (FR/EN/NL)
- **Interface responsive** et moderne

## 🛠️ Technologies Utilisées

### Backend
- **Django 5.1.3** - Framework web Python
- **Django REST Framework** - API RESTful
- **Celery** - Tâches asynchrones
- **Redis** - Cache et broker de messages
- **PostgreSQL** - Base de données (configurable)
- **Stripe** - Paiements en ligne
- **pdfkit** - Génération de PDF

### Frontend
- **Bootstrap 5** - Framework CSS
- **JavaScript ES6+** - Interactivité
- **Leaflet.js** - Cartes interactives
- **Chart.js** - Graphiques et statistiques

### DevOps & Outils
- **Whitenoise** - Gestion des fichiers statiques
- **Gunicorn** - Serveur WSGI
- **Docker** - Conteneurisation (optionnel)
- **Git** - Contrôle de version

## 🚀 Installation et Configuration

### Prérequis
- Python 3.11+
- pip
- Redis (pour Celery)
- wkhtmltopdf (pour les PDF)

### Installation

1. **Cloner le repository**
```bash
git clone https://github.com/votre-username/farmer-market.git
cd farmer-market
```

2. **Créer un environnement virtuel**
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de l'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Migrations de base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic
```

8. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

### Configuration des Services

#### Redis (pour Celery)
```bash
# Installation sur Ubuntu/Debian
sudo apt-get install redis-server

# Installation sur macOS
brew install redis
```

#### wkhtmltopdf (pour les PDF)
```bash
# Installation sur Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# Installation sur macOS
brew install wkhtmltopdf
```

## 📁 Structure du Projet

```
farmer-market/
├── accounts/                 # Gestion des utilisateurs
├── products/                 # Application principale
│   ├── models/              # Modèles de données
│   ├── views/               # Vues de l'application
│   ├── api/                 # API RESTful
│   └── templates/           # Templates HTML
├── markt_farme/             # Configuration Django
├── static/                  # Fichiers statiques
├── media/                   # Fichiers uploadés
├── templates/               # Templates globaux
├── logs/                    # Fichiers de log
├── requirements.txt         # Dépendances Python
├── manage.py               # Script de gestion Django
└── README.md               # Documentation
```

## 🔧 Configuration

### Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```env
# Django
SECRET_KEY=votre-clé-secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/farmer_market

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Redis
REDIS_URL=redis://localhost:6379/0

# wkhtmltopdf
WKHTMLTOPDF_CMD=/usr/local/bin/wkhtmltopdf
```

## 🚀 Déploiement

### Production avec Gunicorn

1. **Installer Gunicorn**
```bash
pip install gunicorn
```

2. **Lancer le serveur**
```bash
gunicorn markt_farme.wsgi:application --bind 0.0.0.0:8000
```

### Docker (optionnel)

```bash
# Construire l'image
docker build -t farmer-market .

# Lancer les conteneurs
docker-compose up -d
```

## 📊 API RESTful

L'API RESTful est disponible à `/api/` avec les endpoints suivants :

- `GET /api/products/` - Liste des produits
- `GET /api/products/{id}/` - Détail d'un produit
- `GET /api/farmers/` - Liste des fermiers
- `GET /api/orders/` - Commandes de l'utilisateur
- `POST /api/orders/` - Créer une commande
- `GET /api/reviews/{product_id}/` - Avis d'un produit

### Authentification API

L'API utilise JWT (JSON Web Tokens) pour l'authentification :

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Utiliser le token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/products/
```

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📝 Logs et Monitoring

Le système de logging est configuré dans `markt_farme/settings.py` avec :

- **django.log** - Logs généraux de l'application
- **audit.log** - Audit des actions utilisateurs
- **error.log** - Erreurs et exceptions
- **security.log** - Événements de sécurité

## 🌍 Internationalisation

L'application supporte 3 langues :
- Français (fr)
- Anglais (en)
- Néerlandais (nl)

Pour ajouter une nouvelle langue :

1. Créer les fichiers de traduction
2. Compiler les traductions
3. Ajouter la langue dans `settings.py`

## 🔒 Sécurité

- **CSRF Protection** activée
- **XSS Protection** configurée
- **Content Security Policy** implémentée
- **Validation des données** stricte
- **Logs de sécurité** automatiques

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **Étudiant** - *Développement initial* - [GitHub](https://github.com/votre-username)

## 🙏 Remerciements

- Django Documentation
- Bootstrap Team
- Stripe Documentation
- OpenStreetMap pour les cartes

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Farmer Market** - Connecter les fermiers et les consommateurs pour une alimentation locale et durable 🌱