# Лабораторна робота №4

**Тема:** Забезпечення безпеки (JWT, хешування паролів, рольова модель RBAC) та автоматизоване тестування (`pytest`).

## Безпека та рольова модель (RBAC)

- **Хешування паролів:** при реєстрації (`POST /register`) паролі хешуються за алгоритмом **Argon2id** (`passlib[argon2]`), у відповідях API чутливі поля ніколи не повертаються.
- **JWT-аутентифікація:** при вході (`POST /login`) генерується Access JWT (`Flask-JWT-Extended`) з передачею ідентифікатора користувача та ролі у claims. Запити без токена або з невалідним токеном відхиляються зі статусом `401 Unauthorized`.
- **Матриця ролей (`user`, `auditor`, `admin`):**
  - `user` — керує власним профілем, рахунками, витратами та персональними категоріями (`POST /category`).
  - `auditor` — доступ у режимі «Тільки для читання» (`GET /users`, `GET /user/<id>`, перегляд рахунків, категорій і фільтрація витрат усіх користувачів); при спробі модифікації даних отримує `403 Forbidden`.
  - `admin` — повний доступ до всіх ресурсів, керування ролями (`PATCH /user/<id>/role`) та глобальними категоріями (`POST /category/global`).

## Виконані завдання

1. **Криптографічне хешування паролів:** у модулі `app/auth.py` реалізовано хешування (`argon2.hash`) та перевірку паролів (`argon2.verify`) за стандартом **Argon2id**.
2. **JWT-аутентифікація:** створено публічні ендпоінти `POST /register` та `POST /login` (`app/resources/auth.py`) із генерацією Access JWT та передачею ролі користувача у claims. Налаштовано стандартну обробку помилок токена з поверненням `401 Unauthorized`.
3. **Рольова модель контролю доступу (RBAC):** впроваджено декоратор `@roles_required` та розмежування прав для ролей `user`, `auditor` і `admin` у всіх ресурсах (`users`, `categories`, `accounts`, `records`) із поверненням `403 Forbidden` при порушенні прав доступу.
4. **Автоматизоване тестування (`pytest`):** створено тестовий пакет `tests/` (`conftest.py`, `test_health.py`, `test_auth_rbac.py`, `test_expenses.py`) для перевірки міток часу (`freezegun`), аутентифікації, матриці ролей та бізнес-логіки списання коштів з рахунку.
5. **Інтеграція тестів у GitHub Actions CI:** у `.github/workflows/ci.yml` додано сервіс `postgres:16-alpine`, перевірку міграцій та автоматичний запуск `pytest`.

## Скріншоти результатів

### 1. Успішний прогін автотестів `pytest` у консолі
<img width="974" height="300" alt="изображение" src="https://github.com/user-attachments/assets/96342da7-cbae-4790-9be6-4f1690254e5e" />

### 2. Реєстрація та вхід користувача з отриманням Access JWT (`POST /register`, `POST /login`)
<img width="974" height="208" alt="изображение" src="https://github.com/user-attachments/assets/fe207ad6-4156-42ea-9e64-a77ecd898695" />
<img width="974" height="179" alt="изображение" src="https://github.com/user-attachments/assets/491cc532-b2dd-40fa-bce3-41126971af19" />
<img width="974" height="322" alt="изображение" src="https://github.com/user-attachments/assets/7d26bb16-0e98-4821-beb7-b985757e2f8d" />

### 3. Захист ендпоінтів без токена (`401 Unauthorized`)
<img width="974" height="239" alt="изображение" src="https://github.com/user-attachments/assets/55fbdfbd-e5ed-4125-95e6-a5e5a42e0570" />

### 4. Перевірка рольової моделі RBAC (`403 Forbidden` при спробі створити глобальну категорію з роллю `user`)
<img width="974" height="199" alt="изображение" src="https://github.com/user-attachments/assets/211c838c-ebd1-4d19-84e2-731cd721922c" />

### 5. Create Record із Bearer-токеном (`201 Created` та списання коштів з рахунку)
<img width="974" height="233" alt="изображение" src="https://github.com/user-attachments/assets/c6707759-2079-4510-a4be-75a23b7a89e4" />
