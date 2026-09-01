# Ping App

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
```