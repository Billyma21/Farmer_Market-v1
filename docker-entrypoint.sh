#!/bin/bash

# Script d'entrée pour Docker

set -e

# Attendre que la base de données soit prête
echo "Attente de la base de données..."
python manage.py wait_for_db

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate

# Créer un superutilisateur si nécessaire
if [ "$DJANGO_CREATE_SUPERUSER" = "true" ]; then
    echo "Création du superutilisateur..."
    python manage.py createsuperuser --noinput || true
fi

# Collecter les fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Compiler les traductions
echo "Compilation des traductions..."
python manage.py compilemessages

# Démarrer le serveur
echo "Démarrage du serveur..."
exec gunicorn markt_farme.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120 