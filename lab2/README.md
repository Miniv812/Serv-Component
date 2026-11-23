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
<img width="1479" height="268" alt="{59224CA8-07D8-4930-846A-5587A0A9A32F}" src="https://github.com/user-attachments/assets/8ff86e5b-2894-4ff4-8ecd-5514bf9a6de9" />
<img width="1457" height="259" alt="{197409B3-D795-4CAF-AC3F-C3B0A9D5A0D0}" src="https://github.com/user-attachments/assets/99efbc65-9399-4d24-bfe2-b418f0ff1f93" />
<img width="1456" height="352" alt="{F9199212-80E6-4E9E-859D-BB2716D85E5F}" src="https://github.com/user-attachments/assets/a7cc3a98-d0e0-4777-86ef-3e89b6d98412" />


### 2. Фільтрація витрат за query-параметрами (`200 OK`)
<img width="974" height="390" alt="изображение" src="https://github.com/user-attachments/assets/92829ba0-ed3e-4c20-afae-61462095edf9" />


### 3. Валідація відсутності query-параметрів (`400 Bad Request`)
<img width="974" height="333" alt="изображение" src="https://github.com/user-attachments/assets/6f60b054-2937-4b5d-9193-72c2dc03ae3b" />
