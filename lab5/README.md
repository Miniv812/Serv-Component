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

1. **Мікросервісна декомпозиція:** монолітний застосунок розділено на два автономні сервіси (`user-service` та `expense-service`) із власними ізольованими базами даних PostgreSQL 16 (`user-db` та `expense-db`) та окремими міграціями Alembic у `docker-compose.yaml`.
2. **Protobuf-контракт та gRPC-сервер:** створено специфікацію `proto/auth.proto` (`AuthService` із методами `ValidateToken` та `ValidateUser`), згенеровано Python-стаби через `grpcio-tools` і реалізовано gRPC-сервер на порту `50051` у `user-service`.
3. **gRPC Interceptors (серверний та клієнтський):** реалізовано `RBACServerInterceptor` у `user-service` для перевірки JWT та ролей із gRPC Metadata (з поверненням `PERMISSION_DENIED` при порушенні прав) та `AuthClientInterceptor` у `expense-service` для автоматичного передавання `authorization: Bearer <token>`.
4. **JSON-RPC 2.0 (`POST /rpc`):** реалізовано публічний ендпоінт `POST /rpc` в `expense-service` із підтримкою як поодиноких (`Single`), так і пакетних (`Batch`) запитів зі стандартними кодами помилок JSON-RPC 2.0 (`-32600`, `-32601`, `-32602`, `-32700`).
5. **Оновлення Bruno OpenCollection та CI:** додано запити для REST (обох сервісів), JSON-RPC 2.0 (Single + Batch) і gRPC, а також оновлено тести `pytest` та GitHub Actions CI.

## Скріншоти результатів

### 1. Успішний прогін автотестів `pytest` у консолі 
<img width="974" height="223" alt="изображение" src="https://github.com/user-attachments/assets/9ea52ff5-4a2b-4626-a1e7-0b35357b7f23" />

### 2. Запуск усіх 4 контейнерів мікросервісної архітектури
<img width="974" height="156" alt="изображение" src="https://github.com/user-attachments/assets/469a1aee-303c-46a0-9607-8568bba0aae9" />
<img width="974" height="133" alt="изображение" src="https://github.com/user-attachments/assets/85b33576-9c6c-4912-a547-0c19aca0473f" />

### 3. Реєстрація та вхід у `user-service` (`http://localhost:8081/login`)
<img width="974" height="345" alt="изображение" src="https://github.com/user-attachments/assets/2005d631-0e08-456a-9560-d289e45f08c0" />
<img width="974" height="285" alt="изображение" src="https://github.com/user-attachments/assets/f059a4e5-c13e-45b3-8ca4-9e26e65484dd" />

### 4. Пакетний запит JSON-RPC 2.0 Batch (`POST http://localhost:8080/rpc`) зі списанням коштів
<img width="974" height="324" alt="изображение" src="https://github.com/user-attachments/assets/de0831ff-5337-44eb-bff2-29484df8fb83" />
<img width="974" height="501" alt="изображение" src="https://github.com/user-attachments/assets/ef691efa-1b50-4cc4-ae90-c59bce1ad551" />

### 5. Прямий виклик gRPC `ValidateUser` (`localhost:50051`) з Metadata та перевірка `RBACServerInterceptor` (`PERMISSION_DENIED`)
<img width="974" height="202" alt="изображение" src="https://github.com/user-attachments/assets/ceaab7f0-11ca-466c-bc23-c8dac1e73d3d" />
<img width="974" height="213" alt="изображение" src="https://github.com/user-attachments/assets/879e9132-aad0-476b-b320-3b407ac9f0ce" />
<img width="974" height="261" alt="изображение" src="https://github.com/user-attachments/assets/63ddfebc-4260-404d-b7a1-db54eac21000" />

