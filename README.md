# Проект FOODGRAM
 
 Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», а перед походом в магазин могут скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 ## Технологии:
 ![Static Badge](https://img.shields.io/badge/Python-3.9-green)
![Static Badge](https://img.shields.io/badge/Django-green)
![Static Badge](https://img.shields.io/badge/REST_framework-red)
![Static Badge](https://img.shields.io/badge/Djoser-green)
![Static Badge](https://img.shields.io/badge/PosgreSQL-blue)
![Static Badge](https://img.shields.io/badge/Docker-lightblue)
![Static Badge](https://img.shields.io/badge/Nginx-gray)
![Static Badge](https://img.shields.io/badge/Gunicorn-white)
![Static Badge](https://img.shields.io/badge/Node.js-orange)
![Static Badge](https://img.shields.io/badge/JS-yellow)
## ДАННЫЕ ДЛЯ ТЕСТОВ ЛЕЖАТ В ФАЙЛЕ foodgram_info.yml
## Запуск проекта на сервере на базе OC Linux.
Обновить пакетный менеджер
```
sudo apt update
sudo apt install curl
```
### Скачать Docker.
```
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin;
```
## Установка и настройка Nginx:
### Устанавливаем NGINX
```
sudo apt install nginx -y
```
### Запускаем
```
sudo systemctl start nginx
```
### Настраиваем firewall
```
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
```
### Включаем firewall
```
sudo ufw enable
```
### Открываем конфигурационный файл NGINX
```
sudo nano /etc/nginx/sites-enabled/default
```
### Полностью удаляем из него все и пишем новые настройки
```
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_set_header HOST $host;
        proxy_pass http://backend:8001;

    }
}
```
### Проверяем корректность настроек
```
sudo nginx -t
```
### Запускаем NGINX
```
sudo systemctl start nginx
```
### Установка пакетного менеджера snap.
```
sudo apt install snapd
```
### Установка и обновление зависимостей для пакетного менеджера snap.
```
sudo snap install core; sudo snap refresh core
```
 
### Установка пакета certbot.
```
sudo snap install --classic certbot
```
### Создание ссылки на certbot в системной директории,
### чтобы у пользователя с правами администратора был доступ к этому пакету.
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
### Получаем сертификат и настраиваем NGINX следуя инструкциям
```
sudo certbot --nginx
```
### Перезапускаем NGINX
```
sudo systemctl reload nginx
```

### Перейти в директорию проекта.
```
cd foodgram/
```
### Создать файл .env, и редактировать данные с пощью редактора nano.
```
sudo touch .env
sudo nano .env
```
### Редактируем данные и заменяем SECRET_KEY.
```
SECRET_KEY=<Смотреть ниже>
POSTGRES_DB=<Желаемое_имя_базы_данных>
POSTGRES_USER=<Желаемое_имя_пользователя_базы_данных>
POSTGRES_PASSWORD=<Желаемый_пароль_пользователя_базы_данных>
DB_HOST=БД
DB_PORT=5432 стандартный порт БД
DEBUG=<Указать для продакшена - False, для разработки - True>
```
### Генерируем новый секретный ключ Django.
```
sudo docker compose -f docker-compose.production.yml exec backend python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
### Далее выполняем последовательно.
```
sudo docker compose -f docker-compose.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend python manage.py loadcsv
```
### Создаем суперпользователся. Следуем инструкциям при выполнении.
```
sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```

---

## Примеры запросов:
![Static Badge](https://img.shields.io/badge/GET-1fa7)
![Static Badge](https://img.shields.io/badge/POST-00BFFF)
![Static Badge](https://img.shields.io/badge/PATCH-FF8C00)
![Static Badge](https://img.shields.io/badge/DEL-FF0000)

### Получеие списка рецептов:

![Static Badge](https://img.shields.io/badge/GET-1fa7)```https://you.domain/api/recipes/```

#### Ответ: ```200```

```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
### Создать рецепт
![Static Badge](https://img.shields.io/badge/POST-00BFFF)```https://you.domain/api/recipes/```

#### Ответ: ```200```

```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
## Автор проекта:
```
frostan
```
