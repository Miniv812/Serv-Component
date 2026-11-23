# Лабораторна робота №2

**Тема:** Проєктування базового RESTful API (In-Memory) та використання Bruno collection для його документування/тестування.

## Виконані завдання

1. **Моделювання сутностей (In-Memory):** реалізовано сховище в оперативній пам'яті (`app/storage.py`) для сутностей `User` (`id`, `name`), `Category` (`id`, `name`) та `Record` (`id`, `user_id`, `category_id`, `created_at` в ISO-8601, `amount`).
2. **RESTful-маршрути:** реалізовано повний набір CRUD-ендпоінтів із дотриманням HTTP статус-кодів (`200`, `201`, `204`, `400`, `404`):
   - **Користувачі:** `GET /users`, `GET /user/<user_id>`, `POST /user`, `DELETE /user/<user_id>`.
   - **Категорії:** `GET /category`, `POST /category`, `DELETE /category/<category_id>`.
   - **Витрати:** `POST /record`, `GET /record/<record_id>`, `DELETE /record/<record_id>`, `GET /record?user_id=X&category_id=Y`.
3. **Валідація фільтрації:** у маршруті `GET /record` додано перевірку query-параметрів — за відсутності обох параметрів (`user_id` та `category_id`) сервер повертає `400 Bad Request` із JSON-помилкою `"error": "invalid_request"`.
4. **Bruno OpenCollection:** у корені репозиторію створено колекцію `bruno_collection/` із середовищем `local` (`baseUrl = http://localhost:8080`) та запитами для всіх ендпоінтів.

## Скріншоти результатів

### 1. Створення сутностей (User, Category, Record)
![Create Record](screenshots/create_record.png)

### 2. Фільтрація витрат за query-параметрами (`200 OK`)
![Filter Records](screenshots/filter_records.png)

### 3. Валідація відсутності query-параметрів (`400 Bad Request`)
![Filter Records Validation](screenshots/filter_records_400.png)

