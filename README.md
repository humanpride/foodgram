# Foodgram

> Foodgram helps home cooks discover and share recipes, build a personal collection, follow other authors, and create shopping lists.

Website: [https://foodgram.servebeer.com](https://foodgram.servebeer.com)

[![Backend CI](https://github.com/humanpride/foodgram/actions/workflows/backend_ci.yml/badge.svg)](https://github.com/humanpride/foodgram/actions/workflows/backend_ci.yml)
[![Frontend CI](https://github.com/humanpride/foodgram/actions/workflows/frontend_ci.yml/badge.svg)](https://github.com/humanpride/foodgram/actions/workflows/frontend_ci.yml)
[![Deploy](https://github.com/humanpride/foodgram/actions/workflows/deploy.yml/badge.svg)](https://github.com/humanpride/foodgram/actions/workflows/deploy.yml)

---

## Features

* **User accounts:** registration, authentication, password changes, and avatar uploads and updates.
* **Recipes:** create, edit, delete, and view full recipe details.
* **Favorites:** save recipes and browse your favorites.
* **Shopping list:** add recipes, view the ingredient list, and download it with quantities combined across recipes.
* **Following:** follow other authors and view their latest recipes, grouped by author, on a dedicated page.
* **Filters:** filter recipes by one or more tags.
* **Access control:** separate permissions for guests, registered users, and administrators.

---

## Tech stack

* **Backend:** Python, Django, Django REST Framework, djoser, python-dotenv, gunicorn
* **Frontend:** React, react-helmet-async, Vite
* **Database:** PostgreSQL (or SQLite when `USE_SQLITE=True`)
* **DevOps:** Docker Compose, GitHub Actions (CI/CD)

---

## Configuration

Choose the environment file location for your setup:

* **Local development or Docker builds:** `backend/.env`.
* **Production with prebuilt images:** `infra/.env`, alongside `docker-compose-prod.yml`.

Backend environment variables:

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

Settings:

* `DJANGO_SECRET_KEY` — Django's secret key.
* `DJANGO_DEBUG` — enables or disables debug mode.
* `DJANGO_ALLOWED_HOSTS` — hostnames the application is allowed to serve.
* `USE_SQLITE` — selects SQLite or PostgreSQL as the database.
* `POSTGRES_*` and `DB_HOST/DB_PORT` — PostgreSQL connection settings.

For frontend builds, create `frontend/.env` and set `VITE_API_URL=http://backend:<port>`.

---

## Local development

### With Docker

Build and run the application with `infra/docker-compose-dev.yml`. Start Compose from `infra` with `-p foodgram -f docker-compose-dev.yml`. Once the containers are running, the `docker compose -p foodgram exec ...` commands below can be run from any directory. Keep `-f` when running `up` again or building images.

#### Prerequisites

* **Docker** (20.10+)
* **Docker Compose** (v2)

#### Setup steps

1. Clone the repository:

    ```bash
    git clone https://github.com/humanpride/foodgram.git
    cd foodgram
    ```

2. Create `backend/.env` and `frontend/.env` (see [Configuration](#configuration)).

3. From the repository root, switch to `infra` and start the containers:

    ```bash
    cd infra
    docker compose -p foodgram -f docker-compose-dev.yml up -d --build
    ```

4. Apply the Django database migrations:

    ```bash
    docker compose -p foodgram exec backend python manage.py migrate
    ```

5. Collect Django static files:

    ```bash
    docker compose -p foodgram exec backend python manage.py collectstatic
    docker compose -p foodgram exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

6. Create a superuser:

    ```bash
    docker compose -p foodgram exec backend python manage.py createsuperuser
    ```

7. Import the ingredient data:

    ```bash
    docker compose -p foodgram exec backend python manage.py import_ingredients
    ```

The import command supports JSON files. Use `--help` for details.

---

### Without Docker

#### Backend

Install the uv package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # for macOS and Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"  # for Windows
```

Install Python 3.14:

```bash
uv python install 3.14
```

Install the dependencies:

```bash
cd backend
uv sync
```

Activate the virtual environment:

```bash
source venv/bin/activate # for Linux and macOS
source venv/Scripts/activate # for Windows
```

Apply the database migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Import the ingredient data:

```bash
python manage.py import_ingredients
```

Start the server:

```bash
python manage.py runserver
```

#### Frontend

Install Node.js 24+ (which includes npm 10+). Use nvm:

With curl:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
```

With wget:

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
```

Then run:

```bash
nvm install 24
```

Install frontend dependencies:

```bash
cd ../frontend
npm install
```

Start the development server:

```bash
npm run dev
```

Example output:

```bash
VITE v7.3.1  ready in 2206 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

Press `Ctrl+C` to stop the server.

---

## Production deployment

### Prerequisites

Server requirements:

* **Docker** (20.10+)
* **Docker Compose** (v2)

### Clone the repository

```bash
git clone https://github.com/humanpride/foodgram.git
cd foodgram
```

### Configure environment variables

For prebuilt images, create `infra/.env` alongside `docker-compose-prod.yml`. To build images on the server with `docker-compose-dev.yml`, create `backend/.env` and `frontend/.env` instead. See [Configuration](#configuration).

### Start the containers and initialize the application

Run one of the following commands from the repository root; each switches to `infra` before starting Compose:

#### Use images from Docker Hub

```bash
cd infra
sudo docker compose -p foodgram -f docker-compose-prod.yml up -d
```

#### Build your own images on the server

```bash
cd infra
sudo docker compose -p foodgram -f docker-compose-dev.yml up -d --build
```

Once the containers are running, the following `docker compose -p foodgram exec ...` commands can be run from any directory. Keep `-f` when running `up` again or building images.

Apply database migrations:

```bash
sudo docker compose -p foodgram exec backend python manage.py migrate
```

Create a superuser:

```bash
sudo docker compose -p foodgram exec backend python manage.py createsuperuser
```

Collect static files:

```bash
sudo docker compose -p foodgram exec backend python manage.py collectstatic --noinput
```

Import the ingredient data:

```bash
sudo docker compose -p foodgram exec backend python manage.py import_ingredients
```

API documentation: `<your-domain>/api/docs/`.

---

<!-- ## Useful links
* [Live demo](https://foodgram-8.ddns.net)
* [API documentation](https://foodgram-8.ddns.net/api/docs/)
--- -->

## Author

Sergei Pashkovskii

[![GitHub](https://img.shields.io/badge/GitHub-humanpride-181717?logo=github&logoColor=white)](https://github.com/humanpride)
[![Telegram](https://img.shields.io/badge/Telegram-@bronze_beard8-2CA5E0?logo=telegram&logoColor=white)](https://t.me/bronze_beard8)
