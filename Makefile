run:
	python manage.py runserver

migrate:
	python manage.py migrate

RATIO ?= 100

filldb:
	python manage.py filldb $(RATIO)
