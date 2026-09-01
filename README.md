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