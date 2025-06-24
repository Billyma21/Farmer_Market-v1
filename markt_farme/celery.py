import os
from celery import Celery

# Définir la variable d'environnement pour les paramètres Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'markt_farme.settings')

app = Celery('markt_farme')

# Utiliser les paramètres Django pour la configuration de Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger automatiquement les tâches des applications Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 