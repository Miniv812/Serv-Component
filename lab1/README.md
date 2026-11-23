# Лабораторна робота №1

**Тема:** Налаштування середовища, Docker Compose, Healthcheck API, керування залежностями та GitHub Actions CI.

## Виконані завдання

1. **Налаштування середовища та залежностей:** створено віртуальне середовище Python, зафіксовано версії `Flask` та `ruff` у `requirements.txt`, налаштовано правила перевірки стилю коду у `pyproject.toml`.
2. **Healthcheck API:** реалізовано два системні ендпоінти перевірки стану сервісу:
   - `GET /healthz/live` (Liveness probe) — повертає HTTP `200 OK`, `"status": "alive"` та поточну мітку часу в UTC ISO-8601:
     ```json
     {
       "status": "alive",
       "timestamp": "2026-11-23T12:16:58.879500+00:00"
     }
     ```
   - `GET /healthz/ready` (Readiness probe) — повертає HTTP `200 OK`, `"status": "ready"`, статус бази даних `"database": "not_connected_yet"` та UTC ISO-8601 timestamp:
     ```json
     {
       "status": "ready",
       "database": "not_connected_yet",
       "timestamp": "2026-11-23T12:17:08.959153+00:00"
     }
     ```
     
3. **Контейнеризація:** створено оптимізований `Dockerfile` на базі `python:3.11-slim` із запуском від непривілейованого користувача `appuser` та `docker-compose.yaml` для локального розгортання на порту `8080`.
4. **GitHub Actions CI:** налаштовано пайплайн `.github/workflows/ci.yml`, який при кожному `push` та `pull_request` у головну гілку запускає лінтер `ruff`, збирає Docker-образ та перевіряє `docker compose config`.

## Скріншоти результатів

<img width="674" height="162" alt="{267D5716-6914-4222-86D0-7F66090295C5}" src="https://github.com/user-attachments/assets/3b7579da-ffd1-417e-8d5f-7fec26528f68" /> <img width="760" height="195" alt="{B3CEECD8-E9BC-41E9-B7E2-C8C642B00669}" src="https://github.com/user-attachments/assets/4df7dc6e-ed0f-47c6-970b-59a5b4921b1c" />
 — перевірка відповідей `/healthz/live` та `/healthz/ready`.
- `screenshots/docker.png` — збірка та запуск контейнера через `docker compose up --build`.
- `screenshots/ci.png` — успішне проходження пайплайну в GitHub Actions.
