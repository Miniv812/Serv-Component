# Expense Tracker Microservices

Мікросервісний застосунок для обліку витрат із міжсервісною взаємодією через **gRPC (HTTP/2)**, публічним інтерфейсом **JSON-RPC 2.0 (Single/Batch)**, JWT-аутентифікацією, рольовим розмежуванням доступу (RBAC) та повним стеком спостережуваності (**OpenTelemetry, Jaeger, Prometheus, Grafana**), розроблений у межах курсу «Технології розроблення серверних компонентів».

## Структура проєкту

```text
Serv-Component/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI
├── proto/
│   ├── auth.proto                  # Protobuf-контракт міжсервісної взаємодії (AuthService)
│   ├── auth_pb2.py                 # Згенеровані Protobuf-повідомлення
│   ├── auth_pb2.pyi                # Типізація Protobuf-повідомлень
│   └── auth_pb2_grpc.py            # Згенеровані gRPC stubs та servicer
├── user_service/
│   ├── user_app/
│   │   ├── __init__.py             # Фабрика Flask-застосунку User Service
│   │   ├── auth.py                 # Хешування Argon2, декоратори RBAC, обробники JWT
│   │   ├── config.py               # Конфігурація підключення до user-db та JWT
│   │   ├── extensions.py           # Ініціалізація SQLAlchemy, Flask-Migrate та JWTManager
│   │   ├── grpc_server.py          # Реалізація AuthService та запуск gRPC-сервера (:50051)
│   │   ├── interceptors.py         # Серверний перехоплювач RBACServerInterceptor
│   │   ├── models.py               # ORM-модель UserModel
│   │   ├── schemas.py              # Схеми валідації Marshmallow та DTO
│   │   ├── views.py                # Healthcheck (/healthz/live, /healthz/ready)
│   │   └── resources/              # REST-ендпоінти auth.py та users.py
│   ├── migrations/                 # Міграції Alembic для user-db
│   ├── Dockerfile                  # Образ контейнера user-service
│   └── run.py                      # Точка входу (REST :8081 + gRPC :50051)
├── expense_service/
│   ├── expense_app/
│   │   ├── __init__.py             # Фабрика Flask-застосунку Expense Service
│   │   ├── auth.py                 # Перевірка JWT та ролей RBAC
│   │   ├── config.py               # Конфігурація expense-db та адреси gRPC-сервера
│   │   ├── extensions.py           # Ініціалізація SQLAlchemy, Flask-Migrate та JWTManager
│   │   ├── grpc_client.py          # gRPC-клієнт та клієнтський перехоплювач AuthClientInterceptor
│   │   ├── models.py               # ORM-моделі CategoryModel, AccountModel, RecordModel
│   │   ├── schemas.py              # Схеми валідації Marshmallow та DTO
│   │   ├── views.py                # Healthcheck (/healthz/live, /healthz/ready)
│   │   └── resources/              # REST-ендпоінти та JSON-RPC 2.0 (rpc.py)
│   ├── migrations/                 # Міграції Alembic для expense-db
│   ├── Dockerfile                  # Образ контейнера expense-service
│   └── run.py                      # Точка входу (REST + JSON-RPC 2.0 :8080)
├── observability/
│   ├── __init__.py
│   ├── telemetry.py                # Ініціалізація OTel Tracing/Metrics та JSON-логер з trace_id
│   └── metrics.py                  # Кастомні бізнес- і технічні метрики (Counter, Histogram)
├── monitoring/
│   ├── otel-collector-config.yaml  # Конфігурація OTel Collector (OTLP -> Jaeger & Prometheus)
│   ├── prometheus/
│   │   └── prometheus.yml          # Конфігурація збору метрик Prometheus
│   └── grafana/
│       ├── dashboards/
│       │   └── expense_dashboard.json   # JSON-дашборд моніторингу витрат та gRPC
│       └── provisioning/
│           ├── dashboards/
│           │   └── dashboards.yaml      # Провайдер автоімпорту JSON-дашбордів
│           └── datasources/
│               └── datasources.yaml     # Автопідключення джерел даних (Prometheus, Jaeger)
├── tests/                          # Інтеграційні тести gRPC, JSON-RPC 2.0 та RBAC (pytest)
├── bruno_collection/               # Колекція запитів Bruno (REST, JSON-RPC 2.0 Batch, gRPC)
├── lab1/ .. lab6/                  # Звіти та скріншоти виконання лабораторних робіт
├── .dockerignore                   # Виключення зайвих файлів під час збірки Docker-образів
├── .env.example                    # Шаблон змінних середовища для локального запуску
├── .gitignore                      # Список файлів і директорій, що ігноруються Git
├── docker-compose.yaml             # Оркестрація 8 контейнерів (БД, мікросервіси та стек Observability)
├── pyproject.toml                  # Налаштування ruff, pytest та pyright
└── requirements.txt                # Зафіксовані залежності Python
```

## Локальний запуск через Docker Compose

1. Клонувати репозиторій та перейти в кореневу директорію проєкту:

```bash
git clone https://github.com/Miniv812/Serv-Component.git
cd Serv-Component
```

2. Створити файл `.env` на основі `.env.example`:

```bash
cp .env.example .env
```

3. Зібрати Docker-образи та запустити всі 4 контейнери:

```bash
docker compose up --build -d
docker compose ps
```

4. Веб-інтерфейси стеку спостережуваності:
   - **Jaeger UI:** `http://localhost:16686`
   - **Prometheus:** `http://localhost:9090`
   - **Grafana:** `http://localhost:3000` (логін/пароль за замовчуванням: `admin` / `admin`)

5. Зупинити контейнери:

```bash
docker compose down
```

## Запуск тестів та локальна розробка без Docker

1. Створити та активувати віртуальне середовище, встановити залежності:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Запустити перевірку лінтером `ruff` та автотести `pytest` (працюють автономно без зовнішньої БД):

```bash
ruff check .
pytest --maxfail=1 --disable-warnings -v
```

3. Застосувати міграції для обох баз даних (за умови запущеного локального PostgreSQL на портах `5433` та `5432`):

```bash
flask --app user_service/run db upgrade -d user_service/migrations
flask --app expense_service/run db upgrade -d expense_service/migrations
```

4. Запустити мікросервіси у двох окремих терміналах:

- **Термінал 1 (`user-service` — REST на `:8081` та gRPC на `:50051`):**
  ```bash
  python user_service/run.py
  ```

- **Термінал 2 (`expense-service` — REST та JSON-RPC 2.0 на `:8080`):**
  ```bash
  python expense_service/run.py
  ```
  
