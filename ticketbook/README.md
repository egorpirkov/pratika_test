# TicketBook — Учебный сервис бронирования билетов

Учебная система для выполнения интеграционного тестирования.

## Архитектура

| Контейнер | Роль |
|-----------|------|
| `backend` | Flask API (Python 3.12, Gunicorn, SQLite) |
| `frontend` | Nginx — раздаёт SPA и проксирует `/api/*` → backend |

### Модули API

| Модуль | Маршруты |
|--------|----------|
| M1 Auth | `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me` |
| M2 Catalog | `GET /api/catalog/events`, `GET /api/catalog/events/<id>`, CRUD (admin) |
| M3 Booking | `POST /api/booking/create`, `GET /api/booking/<id>`, `POST /api/booking/<id>/cancel` |
| M4 Payment | `POST /api/payment/pay`, `GET /api/payment/history` |

## Быстрый старт

```bash
git clone <ваш-репозиторий>
cd ticketbook
docker compose up -d --build
```

Откройте http://localhost

## Тестовые данные

| Роль | Email | Пароль |
|------|-------|--------|
| Пользователь | user@test.com | Test1234! |
| Администратор | admin@test.com | Admin1234! |

Мероприятие с `event_id=5` (Спектакль: Гамлет) — создаётся автоматически при старте.

## Токены карт для тестирования

| Токен | Результат |
|-------|-----------|
| `tok_test_valid` | HTTP 200, payment_status: success, booking: paid |
| `tok_test_decline` | HTTP 402, payment_status: declined, booking: failed |
| любой другой | HTTP 402, declined |

## Интеграционные тест-кейсы

### TC-INT-01 — M1 → M3 (успешное бронирование)
```bash
# 1. Получить токен
TOKEN=$(curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test1234!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['session_token'])")

# 2. Создать бронь
curl -s -X POST http://localhost/api/booking/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"event_id": 5}'
# Ожидаем: HTTP 200, booking_id, status: pending
```

### TC-INT-02 — Невалидный токен
```bash
curl -s -X POST http://localhost/api/booking/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer INVALID_TOKEN_12345" \
  -d '{"event_id": 5}'
# Ожидаем: HTTP 401
```

### TC-INT-03 — Несуществующий event_id
```bash
curl -s -X POST http://localhost/api/booking/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"event_id": 99999}'
# Ожидаем: HTTP 404, "Event not found"
```

### TC-INT-04 — M3 → M4 (успешная оплата)
```bash
# BOOKING_ID — из TC-INT-01
curl -s -X POST http://localhost/api/payment/pay \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"booking_id": 1, "card_token": "tok_test_valid"}'
# Ожидаем: HTTP 200, payment_status: success, booking_status: paid

# Проверить статус брони:
curl -s http://localhost/api/booking/1 -H "Authorization: Bearer $TOKEN"
```

### TC-INT-05 — Двойная оплата
```bash
# Повторить запрос из TC-INT-04 с тем же booking_id
curl -s -X POST http://localhost/api/payment/pay \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"booking_id": 1, "card_token": "tok_test_valid"}'
# Ожидаем: HTTP 409, "Booking already paid"
```

### TC-INT-06 — Отказ оплаты → статус failed
```bash
# Создать новую бронь, затем:
curl -s -X POST http://localhost/api/payment/pay \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"booking_id": <NEW_BOOKING_ID>, "card_token": "tok_test_decline"}'
# Ожидаем: HTTP 402, payment_status: declined, booking_status: failed
```

## Сброс данных

```bash
docker compose down -v && docker compose up -d --build
```

Удаляет volume с БД и пересоздаёт с seed-данными.
