# Foodgram

> Платформа для публикации рецептов: пользователи регистрируются, публикуют свои рецепты, подписываются на других авторов, добавляют рецепты в избранное и формируют список покупок.
Сайт: [https://foodgram-8.ddns.net/](https://foodgram-8.ddns.net/)
>

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

**Бэкенд:** Python, Django, Django REST Framework
*Дополнительно: djoser, python-dotenv, gunicorn, weasyprint, pre-commit, ruff*
**Фронтенд:** React, Vite
*Дополнительно: react-helmet-async*
**База данных:** PostgreSQL (альтернативно SQLite при `USE_SQLITE=True`)
**DevOps:** Docker Compose, GitHub Actions (CI/CD)

---

# Как развернуть

Для **продакшена** используйте файлы workflow GitHub Actions:
* `.github/workflows/backend_ci.yml` - тесты и сборка бэкенда
* `.github/workflows/frontend_ci.yml` - тесты и сборка фронтенда
* `.github/workflows/cd.yml` - деплой на сервер и оповещения

Для **локального** развёртывания используйте Docker Compose и `infra/docker-compose-dev.yml`. После поднятия контейнеров необходимо выполнить миграции и собрать статику.

## Предварительные требования

* Docker
* Docker Compose (v2 предпочтительно)
* Доступ к репозиторию

## Шаги для локального развёртывания

1. Клонируйте репозиторий:

```bash
git clone https://github.com/humanpride/foodgram.git
cd foodgram
```
2. Создайте файлы `infra/.env` и `frontend/.env` (см. раздел Environment variables).
3. Поднимите контейнеры:
```bash
docker compose -f infra/docker-compose-dev.yml up --build -d
```
4. Выполните миграции Django:
```bash
docker compose -f infra/docker-compose-dev.yml exec backend python manage.py migrate
```
5. Соберите статику Django:
```bash
docker compose -f infra/docker-compose-dev.yml exec backend python manage.py collectstatic
docker compose -f infra/docker-compose-dev.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
6. (Опционально) Создайте суперпользователя:
```bash
docker compose -f infra/docker-compose-dev.yml exec backend python manage.py createsuperuser
```
7. Проверьте логи:
```bash
docker compose -f infra/docker-compose-dev.yml logs <service>
```
### Продакшн (GitHub Actions)

Файлы в `.github/workflows/` содержат основной workflow CI/CD. Работают при наличии соответствующих секретов (см. ниже).

## Environment variables — как заполнить `.env`

Файл: `.env` в папке `infra`. Пример:
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

## Секреты для GitHub Actions

Добавьте в **Settings** → **Secrets and variables** → **Actions**:
* `DOCKER_USERNAME` — DockerHub
* `DOCKER_PASSWORD` — DockerHub
* `HOST` — IP сервера
* `SSH_KEY` — приватный SSH-ключ
* `SSH_PASSPHRASE` — пароль к ключу (если есть)
* `USER` — пользователь для SSH
* `TELEGRAM_TO` — ваш user ID Telegram (см. @userinfobot)
* `TELEGRAM_TOKEN` — токен вашего Telegram-бота для оповещений
* `FRONTEND_ENV` — .env файл фронтенда для продакшена (обязательно укажите `VITE_API_URL=http://backend:<port>`)

---

## Полезные команды / отладка

* Поднять стек:
```bash
docker compose -f docker-compose-prod.yml up --build -d
```
* Остановить и удалить контейнеры:
```bash
docker compose -f docker-compose-prod.yml down
```
* Посмотреть логи сервиса:
```bash
docker compose -f docker-compose-prod.yml logs <service>
```
* Выполнить команду внутри контейнера:
```bash
docker compose -f docker-compose-prod.yml exec <service> bash
```

---

## Автор

Sergei Pashkovskii · [@humanpride](https://github.com/humanpride)
