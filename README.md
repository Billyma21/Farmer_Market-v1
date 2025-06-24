# Farmer Market - Plateforme de Vente Directe de Produits Fermiers

## Description

Farmer Market est une plateforme web multilingue (français, anglais, néerlandais) permettant la vente directe de produits fermiers locaux. Cette application facilite la mise en relation entre les consommateurs et les producteurs locaux, favorisant ainsi l'économie circulaire et la consommation responsable.

## Fonctionnalités Principales

### 🛒 **Gestion des Produits**
- Catalogue de produits avec photos et descriptions détaillées
- Système de catégorisation (légumes, fruits, viandes, etc.)
- Gestion des stocks en temps réel
- Prix dynamiques et promotions

### 👨‍🌾 **Espace Fermier**
- Tableau de bord personnalisé avec statistiques de vente
- Gestion des commandes et des créneaux de retrait
- Système de notation et d'avis clients
- Rapports de vente détaillés

### 🗺️ **Carte Interactive**
- Localisation géographique des fermiers
- Filtrage par type de produit et certification bio
- Recherche par localisation
- Informations détaillées sur chaque ferme

### 💳 **Système de Paiement**
- Intégration Stripe pour les paiements sécurisés
- Paiement par virement bancaire
- Génération automatique de factures PDF
- Suivi des statuts de paiement

### 🔔 **Notifications**
- Notifications par email pour les changements de statut
- Rappels automatiques pour les retraits
- Alertes de stock faible
- Notifications de nouveaux avis

### 🌍 **Support Multilingue**
- Interface en français, anglais et néerlandais
- Changement de langue en temps réel
- Contenu localisé selon la région

## Technologies Utilisées

### Backend
- **Django 4.2.7** - Framework web Python
- **Django REST Framework** - API RESTful
- **PostgreSQL** - Base de données
- **Celery** - Traitement asynchrone des tâches
- **Redis** - Cache et broker de messages

### Frontend
- **HTML5/CSS3** - Interface utilisateur
- **JavaScript** - Interactivité côté client
- **Bootstrap 5** - Framework CSS responsive
- **Leaflet.js** - Cartes interactives

### Services Externes
- **Stripe** - Paiements en ligne
- **pdfkit** - Génération de PDF
- **OpenStreetMap** - Données cartographiques

## Installation

### Prérequis
- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- wkhtmltopdf (pour la génération PDF)

### Installation Locale

1. **Cloner le repository**
```bash
git clone https://github.com/bmaayoud/farmer-market.git
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

4. **Configurer la base de données**
```bash
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

### Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```env
DEBUG=True
SECRET_KEY=votre-clé-secrète
DATABASE_URL=postgresql://user:password@localhost/farmer_market
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
REDIS_URL=redis://localhost:6379/0
```

## Structure du Projet

```
farmer_market/
├── accounts/           # Gestion des utilisateurs
├── products/           # Application principale
│   ├── api/           # API RESTful
│   ├── models/        # Modèles de données
│   ├── views/         # Vues de l'application
│   └── templates/     # Templates HTML
├── static/            # Fichiers statiques
├── media/             # Fichiers uploadés
├── templates/         # Templates globaux
└── markt_farme/       # Configuration Django
```

## API RESTful

L'application expose une API RESTful complète :

- `GET /api/products/` - Liste des produits
- `GET /api/farmers/` - Données des fermiers pour la carte
- `POST /api/orders/` - Création de commandes
- `GET /api/categories/` - Catégories de produits

Documentation complète disponible sur `/api/` en mode développement.

## Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
```

## Déploiement

### Production

1. **Configurer les variables d'environnement**
2. **Collecter les fichiers statiques**
   ```bash
   python manage.py collectstatic
   ```
3. **Configurer un serveur web (Nginx/Apache)**
4. **Utiliser Gunicorn comme serveur WSGI**
5. **Configurer Celery pour les tâches asynchrones**

### Docker (Optionnel)

```bash
docker-compose up -d
```

## Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est développé dans le cadre d'un examen de bachelier en informatique de gestion.

## Auteur

**b maayoud** - Étudiant en informatique de gestion

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

---

*Développé avec ❤️ pour favoriser l'agriculture locale et la consommation responsable.*