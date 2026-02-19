# LangStudy — приложение для изучения языков (Django + PostgreSQL + Docker)

Это учебный проект под требования:
- PostgreSQL + минимум 3 связанные таблицы
- Общие поля `created_at`, `updated_at` вынесены в абстрактную базовую модель
- Роли: **Гость** (без авторизации), **Пользователь** (сохранение прогресса), **Администратор** (admin-панель)
- Доп. функционал: **поиск и сортировка** уроков, + REST API (JWT) для интеграции
- В админ-панели есть **выгрузка отчёта XLSX** с выбором таблиц и полей
- Docker (web + postgres), статика и media отображаются

---

## 1) Запуск через Docker

1. Убедитесь, что установлен Docker + docker compose.
2. В корне проекта есть `.env` (можете править под себя).

Запуск:

```bash
docker compose up --build
```

Открыть:
- сайт: http://localhost:8000
- админка: http://localhost:8000/admin/

### Создать администратора (в отдельном терминале)

```bash
docker compose exec web python manage.py createsuperuser
```

### Заполнить демо-данные (языки/уроки/карточки)

```bash
docker compose exec web python manage.py seed_demo
```

---

## 2) Роли и доступ

- **Гость**: может просматривать языки/уроки и проходить уроки в гостевом режиме (без сохранения).
- **Пользователь**: после регистрации/входа получает доступ к **сохранению прогресса**, странице **Мой прогресс**.
- **Администратор**: имеет доступ к `/admin/` и к выгрузке XLSX.

---

## 3) XLSX-выгрузка в админке

Зайдите в админ-панель и в шапке нажмите **«⬇️ Выгрузка XLSX»**  
или откройте напрямую:

`/admin/report-export/`

Выберите таблицы (модели) и поля — получите Excel-файл с листами по таблицам.

---

## 4) REST API (JWT)

Эндпоинты:
- `POST /api/token/` — получить JWT (username/password)
- `POST /api/token/refresh/` — обновить токен
- `GET /api/languages/`
- `GET /api/lessons/?language=en&q=...`
- `GET /api/cards/?lesson=<id>`
- `GET/POST /api/progress/` (требует JWT)

Пример получения токена:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS"}'
```

---

## 5) Безопасность (SQLi / XSS / пароли)

- Пароли хранятся **хэшами** (Django PBKDF2).
- SQL-инъекции: используется Django ORM (параметризованные запросы).
- XSS: шаблоны Django по умолчанию экранируют вывод; формы используют CSRF.
- Включены стандартные middlewares Django (CSRF, sessions, auth).

---

## Стек

- Django 5
- PostgreSQL 15
- DRF + SimpleJWT
- openpyxl (xlsx)
- Bootstrap 5 (адаптивность: телефон/планшет/ПК)
