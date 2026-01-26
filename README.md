# Foodgram

> Платформа для публикации рецептов: пользователи регистрируются, публикуют свои рецепты, подписываются на других авторов, добавляют рецепты в избранное и формируют список покупок.

Сайт: [https://foodgram-8.ddns.net/](https://foodgram-8.ddns.net/)

[![Backend CI](https://github.com/humanpride/foodgram/actions/workflows/backend_ci.yml/badge.svg)](https://github.com/humanpride/foodgram/actions/workflows/backend_ci.yml)
[![Frontend CI](https://github.com/humanpride/foodgram/actions/workflows/frontend_ci.yml/badge.svg)](https://github.com/humanpride/foodgram/actions/workflows/frontend_ci.yml)
[![Deploy](https://github.com/humanpride/foodgram/actions/workflows/cd.yml/badge.svg)](https://github.com/humanpride/foodgram/actions/workflows/cd.yml)

---

# О проекте

**Foodgram** — веб-приложение для публикации и поиска рецептов. Пользователи могут создавать свои рецепты, добавлять чужие в избранное, формировать список покупок и подписываться на других авторов.

Основные сценарии:

* Регистрация и вход пользователей.
* Создание, просмотр, редактирование и удаление рецептов.
* Добавление рецептов в избранное и список покупок.
* Подписка на других пользователей и просмотр их публикаций.
* Фильтрация рецептов по тегам.
* Скачивание списка покупок с суммированными ингредиентами.

**Целевая аудитория:** пользователи, которые готовят по рецептам и хотят вести собственную коллекцию рецептов.

---

# Функции

* **Пользователи:** регистрация, аутентификация, смена пароля, загрузка и смена аватара.
* **Рецепты:** создание, редактирование, удаление, просмотр полной информации.
* **Избранное:** добавление рецептов в избранное и просмотр своего списка.
* **Список покупок:** добавление рецептов, просмотр и скачивание списка ингредиентов с суммарным количеством.
* **Подписки:** подписка на других авторов, страница подписок с последними рецептами по автору.
* **Фильтры:** фильтрация рецептов по тегам, поддержка нескольких тегов одновременно.
* **Разграничение прав:** гость, зарегистрированный пользователь, администратор.

---

# Стек технологий

* **Бэкенд:** Python, Django, Django REST Framework, djoser, python-dotenv, gunicorn, weasyprint, pre-commit, ruff
* **Фронтенд:** React, react-helmet-async, Vite
* **База данных:** PostgreSQL (альтернативно SQLite при `USE_SQLITE=True`)
* **DevOps:** Docker Compose, GitHub Actions (CI/CD)

---

# Как развернуть

## Продакшен (новый сервер)

### Требования
На сервере должны быть установлены:
- **Docker** (версия 20.10+)
- **Docker Compose** (v2)

### Клонирование проекта
```bash
git clone https://github.com/humanpride/foodgram.git
cd foodgram
```

### Настройка переменных окружения
Создайте файлы `backend/.env` и `frontend/.env` (см. раздел Environment variables). Внутри `.env` файла фронтенда обязательно укажите `VITE_API_URL=http://backend:<port>`.
<br>

### Запуск контейнров и инициализация проекта
Запустите проект с помощью Docker Compose:
```bash
cd infra
sudo docker compose -f docker-compose-prod.yml up -d
```
После старта контейнеров выполните миграции:
```bash
sudo docker compose -f docker-compose-prod.yml exec backend python manage.py migrate
```
Создайте суперпользователя:
```bash
sudo docker compose -f docker-compose-prod.yml exec backend python manage.py createsuperuser
```
Соберите статику:
```bash
sudo docker compose -f docker-compose-prod.ymlexec backend python manage.py collectstatic --noinput
```
Импортируйте фикстуры
```bash
sudo docker compose -f docker-compose-prod.ymlexec backend python manage.py import_ingredients
sudo docker compose -f docker-compose-prod.ymlexec backend python manage.py import_tags
```
После успешного запуска вы можете ознакомиться с документацией по API. Будет лежать по адресу `<ваш домен>/api/docs/`

---
## Локально

Для локального развёртывания используйте Docker Compose и `infra/docker-compose-dev.yml`. После поднятия контейнеров необходимо выполнить миграции и собрать статику.

### Требования

- **Docker** (версия 20.10+)
- **Docker Compose** (v2)

### Шаги для локального развёртывания

1. Клонируйте репозиторий:

```bash
git clone https://github.com/humanpride/foodgram.git
cd foodgram
```
2. Создайте файлы `backend/.env` и `frontend/.env` (см. раздел Environment variables).
<br>

3. Запустите контейнеры:
```bash
cd infra
docker compose -f docker-compose-dev.yml up --build -d
```

4. Выполните миграции Django:
```bash
docker compose -f docker-compose-dev.yml exec backend python manage.py migrate
```
5. Соберите статику Django:
```bash
docker compose -f docker-compose-dev.yml exec backend python manage.py collectstatic
docker compose -f docker-compose-dev.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
6. Создайте суперпользователя:
```bash
docker compose -f docker-compose-dev.yml exec backend python manage.py createsuperuser
```
7. (Опционально) Импортируйте файлы продуктов и тегов:
```bash
docker compose -f docker-compose-dev.yml exec backend python manage.py import_ingredients path/to/file
docker compose -f docker-compose-dev.yml exec backend python manage.py import_tags path/to/file
```
Поддерживаются 2 типа файлов: CSV и JSON
Подробнее в подсказке `--help`

## Environment variables — как заполнить `.env`

Файл: `.env` в папке `backend`. Пример:
```ini
# Django settings
DJANGO_SECRET_KEY='your-secret'
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS='127.0.0.1, localhost, backend, ..., ...'
USE_SQLITE=True  # True — SQLite, False — PostgreSQL

# DB settings
POSTGRES_DB='PDB'
POSTGRES_USER='postgres_user'
POSTGRES_PASSWORD='db_pass'
DB_HOST=db
DB_PORT=5432
```

Пояснения:
* `DJANGO_SECRET_KEY` — секретный ключ Django.
* `DJANGO_DEBUG` — включение/отключение режима отладки.
* `DJANGO_ALLOWED_HOSTS` — список хостов для доступа.
* `USE_SQLITE` — выбор базы данных: SQLite или PostgreSQL.
* `POSTGRES_*` и `DB_HOST/DB_PORT` — настройки для PostgreSQL.

---
## Локальное развёртывание без Docker
Вы можете весьма быстро и просто запустить локальный сервер разработки.

#### Для запуска бекэнда
Вам нужно установить Python v3.9+
Можете скачать дистрибутив с официального сайта [python.org](https://www.python.org/downloads/), установить через пакетный менеджер вашей системы или найти в магазине приложений.
После установки python откройте терминал в директории проекта.
Разверните виртуальное окружение:
```bash
cd backend
python -m venv venv
```
Активируйте окружение и установите зависимости:
```bash
source venv/Scripts/activate # для Windows
source venv/bin/activate # для Linux и macOS
python -m pip install --upgrade pip setuptools wheels
pip install -r requirements.txt
```
Выполните миграции:
```bash
python manage.py migrate
```
Создайте суперпользователя
```bash
python manage.py createsuperuser
```
Импортируйте фикстуры
```bash
python manage.py import_ingredients
python manage.py import_tags
```
Запустите сервер:
```bash
python manage.py runserver
```
#### Для фронтенда
Установите node v24+ (вместе с ним установится менеджер пакетов npm v10+). Можете [скачать](https://nodejs.org/en/download) с официального сайта, установить через менеджер пакетов или магазин приложений.
Перейдите в папку с файлами фронтенда и запустите установку пакетов:
```bash
cd frontend
npm install
```
По завершении установки можете запустить веб-сервер:
```bash
npm run dev
```
Если всё в порядке, то вас встретит сообщение:
```bash
VITE v7.3.1  ready in 2206 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```
Остановить сервер вы можете сочетанием клавиш `Ctrl+C`

---
## Полезные ссылки
* [Посмотреть проект вживую](https://foodgram-8.ddns.net)
* [Админ панель проекта](https://foodgram-8.ddns.net/admin)
* [Документация API](https://foodgram-8.ddns.net/api/docs/)
---

## Автор

Сергей Пашковский

[![GitHub](https://img.shields.io/badge/GitHub-humanpride-181717?logo=github&logoColor=white)](https://github.com/humanpride)
[![Telegram](https://img.shields.io/badge/Telegram-@spashk-2CA5E0?logo=telegram&logoColor=white)](https://t.me/spashk)
