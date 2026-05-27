run:
	python manage.py runserver

migrate:
	python manage.py migrate

RATIO ?= 100

filldb:
	python manage.py filldb $(RATIO)

celery-worker:
	celery --app application worker --loglevel=info

celery-beat:
	celery --app application beat --loglevel=info

celery-flower:
	celery --app application flower --loglevel=info
