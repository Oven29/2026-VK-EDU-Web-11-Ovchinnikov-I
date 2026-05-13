Веб технологии
Овчинников Иван Web-11

### Стек технологий

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![jQuery](https://img.shields.io/badge/jquery-%230769AD.svg?style=for-the-badge&logo=jquery&logoColor=white)

### Установка зависимостей
```sh
python -m venv venv
source venv/bin/activate
# venv\Scripts\activate на винде
pip install -r requirements.txt
```

### Настройка `.env`
Пример `.env` файла в `example.env`

### Выполнение миграций
```sh
python manage.py migrate
# или 
make migrate
```

### Запуск сервера
```sh
python manage.py runserver
# или 
make run
```
Сервер запустится на http://127.0.0.1:8000

### Запуск через docker
Также можно запустить через Docker. База сама поднимается и запускается
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

### Вставка "тестовых" данных в бд
```sh
python manage.py filldb [ratio]
```
или
```sh
make filldb RATIO=
```
где `ratio` - коэффициент заполнения сущностей. Допустимое значение от 1 до 100000. Соответственно, после применения команды в базу будет добавлено:

* пользователей — *ratio*;
* вопросов — *ratio x 10*;
* ответы — *ratio x 100*;
* тэгов - *ratio*;
* оценок пользователей - *ratio x 200* (100 для ответов и 100 для вопросов).
