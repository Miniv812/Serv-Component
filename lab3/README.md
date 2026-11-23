# Лабораторна робота №3

**Тема:** Інтеграція PostgreSQL, ORM, міграцій, валідації та варіанти бізнес-логіки.

## Розрахунок індивідуального варіанта

- **Номер залікової книжки ($N$):** `4421`
- **Формула:** $V = (N \pmod 3) + 1 = (4421 \pmod 3) + 1 = 2 + 1 = 3$
- **Варіант 3 — Рахунки користувача (`Account`):**
  - Реалізовано сутність `Account (id, user_id, balance)` із зовнішнім ключем на `users.id`.
  - Додано ендпоінти створення рахунку (`POST /account`), перегляду балансу (`GET /account/<account_id>`, `GET /user/<user_id>/accounts`) та поповнення рахунку (`POST /account/<account_id>/deposit`).
  - Під час створення запису витрати (`POST /record`) виконується перевірка достатності коштів на рахунку користувача та автоматичне списання суми витрати з балансу в межах транзакції БД.

## Виконані завдання

1. **Інтеграція PostgreSQL та ORM:** у `docker-compose.yaml` додано контейнер `postgres:16-alpine` з постійним томом `postgres_data` та `healthcheck`. In-memory сховище замінено на ORM-моделі SQLAlchemy (`UserModel`, `CategoryModel`, `AccountModel`, `RecordModel`) зі зв'язками `ForeignKey` та каскадним видаленням.
2. **Міграції Alembic:** ініціалізовано директорію `migrations/`, згенеровано початкову міграцію схеми БД та налаштовано автоматичне виконання `flask --app run db upgrade` при запуску контейнера.
3. **Валідація даних (Marshmallow):** створено схеми валідації вхідних JSON-запитів, query-параметрів і проміжних DTO (`app/schemas.py`) з поверненням HTTP `400 Bad Request` при помилках валідації.
4. **Бізнес-логіка Варіанта 3:** реалізовано ендпоінти `POST /account`, `GET /account/<account_id>`, `GET /user/<user_id>/accounts`, `POST /account/<account_id>/deposit`, а також автоматичну перевірку балансу та списання суми витрати з рахунку при `POST /record`.
5. **Оновлення Bruno OpenCollection:** додано запити для створення, перегляду й поповнення рахунків, а також перевірки помилки при нестачі коштів (`insufficient_funds`).

## Скріншоти результатів

### 1. Готовність сервісу та підключення до PostgreSQL (`GET /healthz/ready`)
<img width="974" height="250" alt="изображение" src="https://github.com/user-attachments/assets/db3bd5b4-0046-456f-b07b-aff53e9d09a1" />

### 2. Створення та поповнення рахунку користувача (`POST /account`, `POST /account/<id>/deposit`)
<img width="974" height="217" alt="изображение" src="https://github.com/user-attachments/assets/0035cd77-9a46-47bf-bd24-444ddc742bed" />
<img width="974" height="211" alt="изображение" src="https://github.com/user-attachments/assets/3b5186e9-9007-4f4f-a4b5-c3530532d419" />

### 3. Створення витрати з автоматичним списанням коштів (`POST /record`)
<img width="974" height="248" alt="изображение" src="https://github.com/user-attachments/assets/26b1d3ea-a6c4-4e96-971a-7131254c9fdd" />

### 4. Валідація нестачі коштів на рахунку (`400 Bad Request — insufficient_funds`)
<img width="974" height="229" alt="изображение" src="https://github.com/user-attachments/assets/a2d9996a-5657-48e3-8c76-a8d36b7797e5" />

