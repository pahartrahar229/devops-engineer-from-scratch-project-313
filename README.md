# Ping App

[![CI](https://github.com/pahartrahar229/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/pahartrahar229/devops-engineer-from-scratch-project-313/actions)

Минимальное веб-приложение на Flask с одним маршрутом `/ping`.

## Установка

```bash
make install
```

## Запуск

```bash
make run
```

Приложение запустится на порту `8080`.

## Проверка

```bash
curl http://localhost:8080/ping
# pong
```

## Разработка

```bash
make lint    # проверка стиля кода (ruff)
make test    # запуск тестов (pytest)
```

## Деплой

Приложение развёрнуто на [Render](https://render.com/):

🔗 **[https://devops-engineer-from-scratch-project-313.onrender.com](https://devops-engineer-from-scratch-project-313.onrender.com)**

Проверка после деплоя:

```bash
curl https://devops-engineer-from-scratch-project-313.onrender.com/ping
# pong
```

### Настройка на Render

1. New → Web Service → подключить этот репозиторий
2. Language: **Docker**
3. Instance Type: **Free**
4. Переменные окружения:
   - `PORT=8080`
   - `DATABASE_URL` — если используется база данных
   - `SENTRY_DSN` — DSN проекта в Bugsink, для мониторинга ошибок

### Мониторинг ошибок

Используется [Bugsink](https://www.bugsink.com/) (Sentry-совместимый сервис). При наличии переменной окружения `SENTRY_DSN` приложение автоматически отправляет туда необработанные исключения через `sentry-sdk`.

### Локальная сборка Docker-образа

```bash
docker build -t ping-app .
docker run -p 8080:8080 -e PORT=8080 ping-app
```