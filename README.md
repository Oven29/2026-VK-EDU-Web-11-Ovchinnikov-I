Веб технологии
Овчинников Иван Web-11

### Установка зависимостей
```sh
python -m venv venv
source venv/bin/activate
# venv\Scripts\activate на винде
pip install -r requirements.txt
```

### Настройка `.env`
Пример `.env` файла в `example.env`

### Запуск сервера
```sh
python manage.py runserver
# или 
make run
```
Сервер запустится на http://127.0.0.1:8000

### Запуск через docker
Также можно запустить через Docker
```sh
docker compose up -d --build
# остановить
docker compose down
```
Если нужно запустить именно приложеение (без бд и прочей инфрастуктуры), то
```sh
docker build -t ivan_ask .
docker run -p 8000:8000 ivan_ask
```
