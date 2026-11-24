# Лабораторна робота №5

**Тема:** Мікросервісна декомпозиція, міжсервісна взаємодія через gRPC (HTTP/2) та інтерфейс JSON-RPC 2.0.

## Архітектура системи

Система декомпозована на два автономні мікросервіси з ізольованими базами даних PostgreSQL 16:

- **`user-service` (User / Auth Service):**
  - REST API (`http://localhost:8081`): реєстрація (`POST /register`), аутентифікація з видачею JWT (`POST /login`), керування користувачами й ролями (`GET /users`, `PATCH /user/<id>/role`).
  - gRPC Server (`localhost:50051`): реалізація `auth.AuthService` (`ValidateToken`, `ValidateUser`) із серверним перехоплювачем авторизації `RBACServerInterceptor`.
  - База даних: `user-db` (PostgreSQL 16, порт `5433`).
- **`expense-service` (Expense Service):**
  - REST API (`http://localhost:8080`): керування категоріями (`/category`), рахунками користувача (`/account`, Варіант 3) та витратами (`/record`).
  - JSON-RPC 2.0 API (`POST http://localhost:8080/rpc`): підтримка поодиноких (`Single`) та пакетних (`Batch`) запитів (`create_record`, `get_records`, `create_account`, `deposit_account`, `get_categories`).
  - gRPC Client + `AuthClientInterceptor`: синхронна перевірка користувача та його ролі через `user-service:50051` із передачею Bearer-токена у gRPC Metadata.
  - База даних: `expense-db` (PostgreSQL 16, порт `5432`).

## Виконані завдання

1. **Мікросервісна декомпозиція:** монолітний застосунок розділено на два автономні сервіси (`user-service` та `expense-service`) із власними ізольованими базами даних PostgreSQL 16 (`user-db` та `expense-db`) та окремими міграціями Alembic у `docker-compose.yaml`[cite: 8].
2. **Protobuf-контракт та gRPC-сервер:** створено специфікацію `proto/auth.proto` (`AuthService` із методами `ValidateToken` та `ValidateUser`), згенеровано Python-стаби через `grpcio-tools` і реалізовано gRPC-сервер на порту `50051` у `user-service`[cite: 8].
3. **gRPC Interceptors (серверний та клієнтський):** реалізовано `RBACServerInterceptor` у `user-service` для перевірки JWT та ролей із gRPC Metadata (з поверненням `PERMISSION_DENIED` при порушенні прав) та `AuthClientInterceptor` у `expense-service` для автоматичного передавання `authorization: Bearer <token>`[cite: 8].
4. **JSON-RPC 2.0 (`POST /rpc`):** реалізовано публічний ендпоінт `POST /rpc` в `expense-service` із підтримкою як поодиноких (`Single`), так і пакетних (`Batch`) запитів зі стандартними кодами помилок JSON-RPC 2.0 (`-32600`, `-32601`, `-32602`, `-32700`)[cite: 8].
5. **Оновлення Bruno OpenCollection та CI:** додано запити для REST (обох сервісів), JSON-RPC 2.0 (Single + Batch) і gRPC, а також оновлено тести `pytest` та GitHub Actions CI[cite: 8].

## Скріншоти результатів

### 1. Успішний прогін автотестів `pytest` у консолі 

### 2. Запуск усіх 4 контейнерів мікросервісної архітектури

### 3. Реєстрація та вхід у `user-service` (`http://localhost:8081/login`)

### 4. Пакетний запит JSON-RPC 2.0 Batch (`POST http://localhost:8080/rpc`) зі списанням коштів

### 5. Прямий виклик gRPC `ValidateUser` (`localhost:50051`) з Metadata та перевірка `RBACServerInterceptor` (`PERMISSION_DENIED`)