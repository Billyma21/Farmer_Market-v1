# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=markt_farme.settings

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gettext \
        wkhtmltopdf \
        && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . /app/

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Exposer le port
EXPOSE 8000

# Script de démarrage
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"] 