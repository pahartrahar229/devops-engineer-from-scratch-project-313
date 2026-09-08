# Link Shortener API

[![CI](https://github.com/pahartrahar229/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/pahartrahar229/devops-engineer-from-scratch-project-313/actions)

Веб-приложение на FastAPI: сервис сокращения ссылок (CRUD) с базой данных
PostgreSQL, веб-интерфейсом и мониторингом ошибок через Bugsink.

## Установка

```bash
make install
```

Устанавливает и зависимости бэкенда (`uv sync`), и фронтенда (`npm install`).

## Переменные окружения

| Переменная             | Назначение                                    | Пример                                              |
|-------------------------|------------------------------------------------|-------------------------------------------------------|
| `PORT`                  | Публичный порт (слушает nginx)                | `80`                                                    |
| `DATABASE_URL`          | Строка подключения к PostgreSQL                | `postgres://user:pass@host:5432/db?sslmode=disable`      |
| `BASE_URL`               | Базовый адрес для формирования `short_url`      | `https://myapp.onrender.com`                              |
| `CORS_ALLOWED_ORIGINS`   | Разрешённые Origin для CORS (через запятую)     | `http://localhost:5173`                                     |
| `SENTRY_DSN`             | DSN проекта в Bugsink (необязательно)            | `https://xxx@bugsink.example.com/1`                           |

Для локальной разработки можно создать файл `.env` (загружается через
`python-dotenv`).

## Локальный запуск

Только бэкенд:

```bash
make run
```

Бэкенд и фронтенд одновременно (для разработки UI):

```bash
make dev
```

Бэкенд — `http://localhost:8080`, фронтенд — `http://localhost:5173`.

## API

- `GET /api/links` — список ссылок, поддерживает пагинацию через
  `?range=[start,end]` (заголовок ответа `Content-Range`)
- `POST /api/links` — создать ссылку
- `GET /api/links/{id}` — получить ссылку по id
- `PUT /api/links/{id}` — обновить ссылку
- `DELETE /api/links/{id}` — удалить ссылку
- `GET /r/{short_name}` — редирект (302) на `original_url`
- `GET /ping` — проверка живости сервиса

Ошибки валидации возвращаются с кодом `422` и телом `{"detail": ...}`.
Отсутствующая запись — `404` с телом `{"detail": "Link not found"}`.

Интерактивная документация доступна на `/docs` (Swagger UI).

## Разработка

```bash
make lint    # проверка стиля кода (ruff)
make test    # запуск тестов (pytest)
```

Тесты лежат в `tests/` и используют изолированную in-memory SQLite-базу,
реальный PostgreSQL для их запуска не требуется.

## Деплой

Приложение развёрнуто на [Render](https://render.com/) единым контейнером:
Nginx раздаёт статику фронтенда и проксирует `/api/*` и `/r/*` на backend.

🔗 **[https://devops-engineer-from-scratch-project-313-hlm4.onrender.com](https://devops-engineer-from-scratch-project-313-hlm4.onrender.com)**

### Настройка на Render

1. **PostgreSQL**: New → PostgreSQL → создать базу, скопировать
   Internal Database URL
2. **Web Service**: New → Web Service → подключить репозиторий
   - Language: **Docker**
   - Instance Type: **Free**
   - Переменные окружения:
     - `PORT=80`
     - `DATABASE_URL` — Internal Database URL из шага 1
     - `BASE_URL` — публичный адрес сервиса на Render
     - `SENTRY_DSN` — DSN проекта в Bugsink (если подключён мониторинг)

Render автоматически обслуживает сервис по HTTPS.

### Мониторинг ошибок

Используется [Bugsink](https://www.bugsink.com/) (Sentry-совместимый
сервис). При наличии переменной окружения `SENTRY_DSN` приложение
автоматически отправляет туда необработанные исключения через
`sentry-sdk`.

### Локальная сборка Docker-образа

```bash
docker build -t link-shortener .
docker run -p 8080:80 \
  -e PORT=80 \
  -e DATABASE_URL="postgres://user:pass@host:5432/db" \
  -e BASE_URL="http://localhost:8080" \
  link-shortener
```