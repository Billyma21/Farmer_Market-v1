.PHONY: help install test lint format clean docker-build docker-run docker-stop migrate collectstatic superuser shell

help: ## Afficher cette aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installer les dépendances
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## Lancer les tests
	pytest

test-coverage: ## Lancer les tests avec couverture
	pytest --cov=. --cov-report=html --cov-report=term-missing

lint: ## Lancer le linting
	flake8 .
	black --check .
	isort --check-only .

format: ## Formater le code
	black .
	isort .

clean: ## Nettoyer les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build
	rm -rf dist

docker-build: ## Construire l'image Docker
	docker-compose build

docker-run: ## Démarrer les services Docker
	docker-compose up -d

docker-stop: ## Arrêter les services Docker
	docker-compose down

docker-logs: ## Afficher les logs Docker
	docker-compose logs -f

migrate: ## Appliquer les migrations
	python manage.py migrate

makemigrations: ## Créer les migrations
	python manage.py makemigrations

collectstatic: ## Collecter les fichiers statiques
	python manage.py collectstatic --noinput

superuser: ## Créer un superutilisateur
	python manage.py createsuperuser

shell: ## Ouvrir un shell Django
	python manage.py shell

runserver: ## Démarrer le serveur de développement
	python manage.py runserver

compilemessages: ## Compiler les traductions
	python manage.py compilemessages

makemessages: ## Créer les fichiers de traduction
	python manage.py makemessages -l fr
	python manage.py makemessages -l en
	python manage.py makemessages -l nl

check: ## Vérifier la configuration Django
	python manage.py check

security-check: ## Vérifier la sécurité
	bandit -r . -f json -o bandit-report.json
	safety check

setup-dev: ## Configuration initiale pour le développement
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
	python manage.py migrate
	python manage.py collectstatic --noinput
	@echo "Configuration de développement terminée!"

setup-prod: ## Configuration initiale pour la production
	pip install -r requirements.txt
	python manage.py migrate
	python manage.py collectstatic --noinput
	python manage.py compilemessages
	@echo "Configuration de production terminée!"

backup: ## Sauvegarder la base de données
	python manage.py dumpdata > backup_$(shell date +%Y%m%d_%H%M%S).json

restore: ## Restaurer la base de données (usage: make restore FILE=backup_file.json)
	python manage.py loaddata $(FILE)

deploy: ## Déployer l'application
	@echo "Déploiement en cours..."
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "Déploiement terminé!"

monitor: ## Surveiller l'application
	@echo "Surveillance de l'application..."
	@echo "Logs en temps réel:"
	docker-compose logs -f web

health-check: ## Vérifier la santé de l'application
	@echo "Vérification de la santé de l'application..."
	curl -f http://localhost:8000/health/ || echo "Application non accessible"
	@echo "Vérification de la base de données..."
	python manage.py check --database default

performance-test: ## Tests de performance
	@echo "Lancement des tests de performance..."
	python -m pytest tests/test_performance.py -v

load-test: ## Tests de charge
	@echo "Lancement des tests de charge..."
	locust -f tests/locustfile.py --host=http://localhost:8000

update-deps: ## Mettre à jour les dépendances
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt
	pip install --upgrade -r requirements-dev.txt

clean-docker: ## Nettoyer Docker
	docker system prune -f
	docker volume prune -f
	docker image prune -f

docs: ## Générer la documentation
	@echo "Génération de la documentation..."
	pydoc-markdown
	@echo "Documentation générée dans docs/"

release: ## Créer une nouvelle release
	@echo "Création d'une nouvelle release..."
	@read -p "Version (ex: 1.0.0): " version; \
	git tag -a v$$version -m "Release v$$version"; \
	git push origin v$$version; \
	@echo "Release v$$version créée!"

# Variables d'environnement
export DJANGO_SETTINGS_MODULE=markt_farme.settings
export PYTHONPATH=. 