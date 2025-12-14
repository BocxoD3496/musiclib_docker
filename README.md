# MusicLib — Django приложение для работы с музыкальными альбомами

> В этом репозитории проект упакован в Docker и переведён с SQLite на PostgreSQL.
>
> Требования: Docker + Docker Compose.

## Возможности
- Выбор хранилища: **БД** (PostgreSQL) или **JSON**
- Проверка на дубликаты (в БД и в JSON)
- CRUD (создание/редактирование/удаление) для альбомов
- AJAX-поиск по базе (API) и просмотр списка

## Быстрый старт (Docker Compose, режим разработки)

1) Скопируйте пример окружения:
```bash
cp .env.example .env
```

2) Запустите сервисы:
```bash
docker compose up --build
```

3) Откройте приложение:
- http://localhost:8000/

Контейнер `web` при старте автоматически выполняет:
- `python manage.py migrate`
- `python manage.py collectstatic`

> В dev-режиме в `docker-compose.yml` подключён bind mount проекта (`.:/app`), поэтому правки в коде сразу видны в контейнере.

## Запуск для production

В репозитории есть `docker-compose.prod.yml`, который:
- не монтирует исходники,
- запускает `gunicorn`,
- собирает статику в volume.

Запуск:
```bash
cp .env.example .env
# обязательно поменяйте DJANGO_SECRET_KEY и POSTGRES_PASSWORD

docker compose -f docker-compose.prod.yml up --build -d
```

Проверка логов:
```bash
docker compose -f docker-compose.prod.yml logs -f web
```

## Переменные окружения

Все секреты передаются через `.env` (он в `.gitignore`).

Минимальный набор (см. `.env.example`):
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (1/0)
- `DJANGO_ALLOWED_HOSTS` (через запятую)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `POSTGRES_HOST`, `POSTGRES_PORT`

## Миграция данных SQLite → PostgreSQL

Ниже безопасный и повторяемый вариант через Django fixtures.

### Вариант A (рекомендуется): dumpdata/loaddata

1) **Сделайте дамп из старого проекта (SQLite)**.

Если у вас ещё остался файл `db.sqlite3` из версии на PythonAnywhere/локально, выполните **на хосте** (в виртуальном окружении) или в контейнере со включённым SQLite:

```bash
# ЛОКАЛЬНО (использует SQLite по умолчанию, если DJANGO_DB_ENGINE не задан)
python manage.py dumpdata \
  --indent 2 \
  --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission \
  > sqlite_dump.json
```

2) **Запустите PostgreSQL через Docker** (можно обычный `docker compose up -d db`).

3) **Импортируйте дамп в PostgreSQL**:
```bash
docker compose run --rm web python manage.py loaddata /app/sqlite_dump.json
```

> Если проект содержит только модель `albums.Album`, можно дампить/заливать только её:
> `python manage.py dumpdata albums.Album > albums.json`

### Вариант B: pgloader

Можно использовать `pgloader` для прямой миграции SQLite → PostgreSQL.
Плюсы: быстро и «как есть». Минусы: нужно поставить pgloader и следить за схемой/кодировками.

Пример команды (адаптируйте пути/доступы):
```bash
pgloader db.sqlite3 postgresql://musiclib:musiclib@localhost:5432/musiclib
```

## Статические файлы

- В Docker статика собирается командой `collectstatic` в каталог `/app/staticfiles`.
- Для постоянства используется Docker volume `static_volume`.
- WhiteNoise включён в `musiclib/settings.py` для раздачи статики приложением (подходит для простого production и для учебного проекта).

## Структура Docker-файлов

- `Dockerfile` — сборка образа Django-приложения
- `docker-compose.yml` — dev-оркестрация (Django + PostgreSQL)
- `docker-compose.prod.yml` — production-оркестрация
- `.dockerignore` — исключение лишних файлов из build context
- `.env.example` — пример переменных окружения
- `scripts/entrypoint.sh` — ожидание БД, миграции, сбор статики и запуск сервера

## Полезные команды

Остановить:
```bash
docker compose down
```

Удалить volumes (в т.ч. данные Postgres):
```bash
docker compose down -v
```

Выполнить миграции вручную:
```bash
docker compose run --rm web python manage.py migrate
```

Создать суперпользователя:
```bash
docker compose run --rm web python manage.py createsuperuser
```
