# Guide de Déploiement - Farmer Market v0.9.0 Beta

**Épreuve Intégrée - Bac Info Appli**  
*Instructions complètes pour le déploiement en production*

##  Prérequis Système

### Serveur
- **OS** : Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM** : Minimum 2GB (recommandé 4GB+)
- **CPU** : 2 cœurs minimum
- **Stockage** : 20GB minimum

### Logiciels Requis
- **Python** : 3.8 ou supérieur
- **PostgreSQL** : 12+ (ou MySQL 8+)
- **Redis** : 6.0+
- **Nginx** : 1.18+
- **wkhtmltopdf** : Pour la génération de PDF

##  Déploiement Automatisé

### Option 1 : Script de Déploiement

```bash
#!/bin/bash
# deploy.sh - Script de déploiement automatique

set -e

echo " Démarrage du déploiement Farmer Market v0.9.0 Beta"

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx wkhtmltopdf

# Création de l'utilisateur de l'application
sudo useradd -m -s /bin/bash farmermarket
sudo usermod -aG sudo farmermarket

# Configuration PostgreSQL
sudo -u postgres createdb farmermarket
sudo -u postgres createuser farmermarket
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE farmermarket TO farmermarket;"

# Configuration Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Clonage du projet
cd /home/farmermarket
sudo -u farmermarket git clone https://github.com/votre-username/farmer-market.git
cd farmer-market

# Configuration de l'environnement virtuel
sudo -u farmermarket python3 -m venv venv
sudo -u farmermarket venv/bin/pip install -r requirements.txt

# Configuration des variables d'environnement
sudo -u farmermarket cp env_example.txt .env
# Éditer le fichier .env avec les vraies valeurs

# Configuration de l'application
sudo -u farmermarket venv/bin/python manage.py migrate
sudo -u farmermarket venv/bin/python manage.py collectstatic --noinput
sudo -u farmermarket venv/bin/python manage.py createsuperuser

# Configuration Gunicorn
sudo tee /etc/systemd/system/farmermarket.service > /dev/null <<EOF
[Unit]
Description=Farmer Market Gunicorn
After=network.target

[Service]
User=farmermarket
Group=www-data
WorkingDirectory=/home/farmermarket/farmer-market
Environment="PATH=/home/farmermarket/farmer-market/venv/bin"
ExecStart=/home/farmermarket/farmer-market/venv/bin/gunicorn --workers 3 --bind unix:/home/farmermarket/farmer-market/farmermarket.sock markt_farme.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configuration Celery
sudo tee /etc/systemd/system/farmermarket-celery.service > /dev/null <<EOF
[Unit]
Description=Farmer Market Celery Worker
After=network.target

[Service]
User=farmermarket
Group=www-data
WorkingDirectory=/home/farmermarket/farmer-market
Environment="PATH=/home/farmermarket/farmer-market/venv/bin"
ExecStart=/home/farmermarket/farmer-market/venv/bin/celery -A markt_farme worker -l info

[Install]
WantedBy=multi-user.target
EOF

# Configuration Celery Beat
sudo tee /etc/systemd/system/farmermarket-celerybeat.service > /dev/null <<EOF
[Unit]
Description=Farmer Market Celery Beat
After=network.target

[Service]
User=farmermarket
Group=www-data
WorkingDirectory=/home/farmermarket/farmer-market
Environment="PATH=/home/farmermarket/farmer-market/venv/bin"
ExecStart=/home/farmermarket/farmer-market/venv/bin/celery -A markt_farme beat -l info

[Install]
WantedBy=multi-user.target
EOF

# Démarrage des services
sudo systemctl daemon-reload
sudo systemctl enable farmermarket
sudo systemctl enable farmermarket-celery
sudo systemctl enable farmermarket-celerybeat
sudo systemctl start farmermarket
sudo systemctl start farmermarket-celery
sudo systemctl start farmermarket-celerybeat

# Configuration Nginx
sudo tee /etc/nginx/sites-available/farmermarket > /dev/null <<EOF
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/farmermarket/farmer-market;
    }

    location /media/ {
        root /home/farmermarket/farmer-market;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/farmermarket/farmer-market/farmermarket.sock;
    }
}
EOF

# Activation du site Nginx
sudo ln -s /etc/nginx/sites-available/farmermarket /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

echo " Déploiement terminé avec succès!"
echo " Accédez à votre application: http://votre-domaine.com"
echo " Dashboard admin: http://votre-domaine.com/admin"
```

### Option 2 : Déploiement Manuel

#### 1. Préparation du Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx wkhtmltopdf git
```

#### 2. Configuration de la Base de Données

```bash
# Configuration PostgreSQL
sudo -u postgres createdb farmermarket
sudo -u postgres createuser farmermarket
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE farmermarket TO farmermarket;"
sudo -u postgres psql -c "ALTER USER farmermarket PASSWORD 'votre_mot_de_passe_securise';"
```

#### 3. Configuration de l'Application

```bash
# Clonage et configuration
cd /home/farmermarket
git clone https://github.com/votre-username/farmer-market.git
cd farmer-market

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Variables d'environnement
cp env_example.txt .env
# Éditer .env avec les vraies valeurs

# Configuration Django
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Configuration des Services

```bash
# Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 markt_farme.wsgi:application

# Celery (dans un autre terminal)
celery -A markt_farme worker -l info

# Celery Beat (dans un autre terminal)
celery -A markt_farme beat -l info
```

## 🔧 Configuration des Variables d'Environnement

### Fichier `.env` de Production

```env
# Configuration Django
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,IP_DU_SERVEUR

# Base de données
DATABASE_URL=postgresql://farmermarket:votre_mot_de_passe@localhost/farmermarket

# Configuration Stripe (Production)
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx

# Configuration Email (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
DEFAULT_FROM_EMAIL=Farmer Market <noreply@votre-domaine.com>

# Configuration Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Sécurité Production
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')

# Configuration PDF
WKHTMLTOPDF_CMD=/usr/bin/wkhtmltopdf
```

##  Sécurisation de Production

### 1. Configuration SSL/HTTPS

```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx

# Obtention du certificat SSL
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique
sudo crontab -e
# Ajouter: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Configuration Firewall

```bash
# UFW (Uncomplicated Firewall)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. Sécurisation PostgreSQL

```bash
# Édition de pg_hba.conf
sudo nano /etc/postgresql/12/main/pg_hba.conf

# Ajouter/modifier:
local   farmermarket    farmermarket    md5
host    farmermarket    farmermarket    127.0.0.1/32    md5

# Redémarrage PostgreSQL
sudo systemctl restart postgresql
```

##  Monitoring et Maintenance

### 1. Logs et Surveillance

```bash
# Vérification des logs
sudo journalctl -u farmermarket -f
sudo journalctl -u farmermarket-celery -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Sauvegarde Automatique

```bash
#!/bin/bash
# backup.sh - Script de sauvegarde

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/farmermarket"

# Sauvegarde base de données
pg_dump farmermarket > $BACKUP_DIR/db_$DATE.sql

# Sauvegarde fichiers média
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/farmermarket/farmer-market/media/

# Nettoyage des anciennes sauvegardes (garde 7 jours)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 3. Mise à Jour de l'Application

```bash
#!/bin/bash
# update.sh - Script de mise à jour

cd /home/farmermarket/farmer-market

# Sauvegarde avant mise à jour
./backup.sh

# Pull des dernières modifications
git pull origin main

# Mise à jour des dépendances
source venv/bin/activate
pip install -r requirements.txt

# Migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Redémarrage des services
sudo systemctl restart farmermarket
sudo systemctl restart farmermarket-celery
sudo systemctl restart farmermarket-celerybeat
```

##  Dépannage

### Problèmes Courants

#### 1. Erreur de Permission
```bash
sudo chown -R farmermarket:www-data /home/farmermarket/farmer-market
sudo chmod -R 755 /home/farmermarket/farmer-market
```

#### 2. Erreur de Base de Données
```bash
# Vérifier la connexion
sudo -u postgres psql -d farmermarket -c "\dt"

# Réinitialiser les migrations si nécessaire
python manage.py migrate --fake-initial
```

#### 3. Erreur de Services
```bash
# Vérifier le statut des services
sudo systemctl status farmermarket
sudo systemctl status farmermarket-celery
sudo systemctl status nginx

# Redémarrer les services
sudo systemctl restart farmermarket
sudo systemctl restart nginx
```

##  Optimisations de Performance

### 1. Configuration Nginx Avancée

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 2. Cache Redis

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 3. Optimisation Base de Données

```sql
-- Index pour les requêtes fréquentes
CREATE INDEX idx_product_category ON products_product(category_id);
CREATE INDEX idx_order_customer ON products_order(customer_id);
CREATE INDEX idx_order_status ON products_order(status);
```

##  Checklist de Déploiement

- [ ] Serveur configuré et sécurisé
- [ ] Base de données PostgreSQL installée et configurée
- [ ] Redis installé et configuré
- [ ] Application déployée et configurée
- [ ] Variables d'environnement définies
- [ ] Migrations appliquées
- [ ] Fichiers statiques collectés
- [ ] Services systemd configurés et démarrés
- [ ] Nginx configuré et démarré
- [ ] SSL/HTTPS configuré
- [ ] Firewall configuré
- [ ] Sauvegardes automatisées configurées
- [ ] Monitoring configuré
- [ ] Tests de fonctionnalité effectués

## 📞Support

Pour toute question ou problème de déploiement :
- Consulter les logs : `sudo journalctl -u farmermarket -f`
- Vérifier la configuration : `python manage.py check --deploy`
- Tester la connectivité : `python manage.py shell`

---

**Version Beta v0.9.0** - *Guide de déploiement professionnel pour l'Épreuve Intégrée* 