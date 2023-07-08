![example workflow](https://github.com/WhatIsMyNam3/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Продуктовый помощник Foodgram

### Описание
Продуктовый помощник Foodgram - сервис, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии
- Python 3.7
- Django 3.2
- Djoser 2.1.0
- Django Rest Framework 3.12.

### Установка и запуск проекта
- Склонируйте репозиторий.
- Создайте виртуальное окружение, находясь в папке проекта:  
``` python -m venv venv ```  
- Активируйте виртуальное окружение: 
Windows: `source venv\scripts\activate`;
Linux/Mac: `sorce venv/bin/activate`
- Для запуска, создайте в папке /infra/ файл .env и заполните его:  
```SECRET_KEY=секретный ключ джанго```
```POSTGRES_DB=назвение бд```
```POSTGRES_USER=имя пользователя```
```POSTGRES_PASSWORD=пароль для бд```
```DB_HOST=db```
```DB_PORT=5432 ```  
- Далее переходим на сервер.
- Устанавливаем Docker и docker-compose:
```sudo apt install docker docker-compose```
- Копируем на ваш сервер файлы docker-compose.yml и nginx.conf:
```scp docker-compose.yml <username>@<server_ip>:/home/<username>/```
```scp nginx.conf <username>@<server_ip>:/home/<username>/```
- Запускаем проект:
```sudo docker-compose up```
- Выполняем миграции:
```sudo docker-compose exec -T backend python manage.py migrate --noinput```
- Создаем при необходимости администратора
```sudo docker-compose exec backend python manage.py createsuperuser```
- Собираем статику:
```sudo docker-compose exec -T backend python manage.py collectstatic --no-input```
- И если потребуется, можно заполнить базу данных ингредиентами: 
```sudo docker-compose exec backend python manage.py load_ingredients```

