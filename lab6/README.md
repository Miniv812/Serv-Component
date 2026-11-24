# Лабораторна робота №6

**Тема:** Спостережуваність (Observability): розподілене трасування OpenTelemetry + Jaeger, метрики Prometheus, Grafana Provisioning та кореляційне JSON-логування.

## Архітектура системи

Система складається з двох автономних мікросервісів з ізольованими базами даних PostgreSQL 16 та централізованого стеку спостережуваності:

- **`user-service` (User / Auth Service):**
  - REST API (`http://localhost:8081`): реєстрація (`POST /register`), аутентифікація з видачею JWT (`POST /login`), керування користувачами й ролями (`GET /users`, `PATCH /user/<id>/role`).
  - gRPC Server (`localhost:50051`): реалізація `auth.AuthService` (`ValidateToken`, `ValidateUser`) із серверним перехоплювачем авторизації `RBACServerInterceptor` та екстракцією W3C Trace Context.
  - База даних: `user-db` (PostgreSQL 16, порт `5433`).
- **`expense-service` (Expense Service):**
  - REST API (`http://localhost:8080`): керування категоріями (`/category`), рахунками користувача (`/account`, Варіант 3) та витратами (`/record`).
  - JSON-RPC 2.0 API (`POST http://localhost:8080/rpc`): підтримка поодиноких (`Single`) та пакетних (`Batch`) запитів (`create_record`, `get_records`, `create_account`, `deposit_account`, `get_categories`).
  - gRPC Client + `AuthClientInterceptor`: синхронна перевірка користувача та його ролі через `user-service:50051` із передачею Bearer-токена та W3C `traceparent` у gRPC Metadata.
  - База даних: `expense-db` (PostgreSQL 16, порт `5432`).
- **Стек спостережуваності (Observability Stack):**
  - **OpenTelemetry SDK & Collector (`otel-collector`, порти `4317` gRPC / `4318` HTTP):** наскрізне трасування запитів (W3C Trace Context), збір кастомних метрик (`Counter`, `Histogram`) та структуроване JSON-логування із прив'язкою `trace_id` і `span_id`.
  - **Jaeger UI (`http://localhost:16686`):** візуалізація розподілених трейсів і дерева кадрів (Spans) між мікросервісами.
  - **Prometheus (`http://localhost:9090`):** збір і зберігання технічних та бізнес-метрик (`expenses_created_total`, `expense_amount_total`, `expense_amount_distribution`, `grpc_user_validations_total`, `grpc_validation_duration_ms`, `user_auth_events_total`).
  - **Grafana (`http://localhost:3000`):** автоматичне розгортання джерел даних та JSON-дашборду *Expense Tracker Observability* через Grafana Provisioning.

## Виконані завдання

1. **Distributed Tracing (OpenTelemetry & Jaeger):** обидва мікросервіси (`user-service` та `expense-service`) інструментовано за допомогою OpenTelemetry SDK (`FlaskInstrumentor`, `GrpcInstrumentorClient`, `GrpcInstrumentorServer`). Забезпечено наскрізну передачу W3C Trace Context (`traceparent`) через HTTP та gRPC Metadata, завдяки чому у Jaeger UI формується єдине дерево кадрів (Spans) між сервісами.
2. **OTel Metrics & Prometheus:** реалізовано збір кастомних бізнес- і технічних метрик (`Counter` — `expenses_created`, `expense_amount`, `grpc_user_validations`, `user_auth_events`; `Histogram` — `expense_amount_distribution`, `grpc_validation_duration_ms`) та їх експорт через `otel-collector` у Prometheus.
3. **Grafana Dashboard Provisioning:** створено JSON-дашборд `monitoring/grafana/dashboards/expense_dashboard.json` та налаштовано автоматичне розгортання джерел даних (`Prometheus`, `Jaeger`) і дашборду через `dashboards.yaml` та volume mounts у `docker-compose.yaml`.
4. **Кореляційне JSON-логування:** реалізовано `OTelTraceContextFilter` та `JsonLogFormatter` для форматування всіх логів обох сервісів у JSON із автоматичним підставленням активних `trace_id` та `span_id`.
5. **Повнота стеку та автотести:** розгорнуто зв'язку `otel-collector` + `jaeger` + `prometheus` + `grafana`, додано автотести у `tests/test_observability.py` та оновлено документацію в `README.md`.

## Скріншоти результатів

### 1. Перевірка працездатності усіх 8 контейнерів

### 2. Успішний прогін автотестів `pytest` у консолі 

### 3. Перевірка в Jaeger UI (`http://localhost:16686`)

### 4. Кореляційні JSON-логи обох мікросервісів із прив'язкою `trace_id` та `span_id`

### 5. Перевірка в Prometheus (`http://localhost:9090`)

### 6. Перевірка в Grafana (`http://localhost:3000`)
