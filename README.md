# Expense Tracker Backend

Серверний застосунок для обліку витрат із JWT-аутентифікацією, рольовим розмежуванням доступу (RBAC) та PostgreSQL, розроблений у межах курсу «Технології розроблення серверних компонентів».

## Структура проєкту

```text
Serv-Component/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI (ruff, міграції, pytest + PostgreSQL, Docker)
├── app/
│   ├── __init__.py                 # Фабрика Flask-застосунку, ініціалізація БД, JWT та Blueprints
│   ├── auth.py                     # Хешування Argon2, декоратор @roles_required, обробники JWT 401
│   ├── config.py                   # Конфігурація підключення до PostgreSQL та JWT_SECRET_KEY
│   ├── extensions.py               # Ініціалізація SQLAlchemy, Flask-Migrate та JWTManager
│   ├── models.py                   # ORM-моделі (User, Category, Account, Record)
│   ├── schemas.py                  # Схеми валідації Marshmallow та DTO
│   ├── views.py                    # Системні ендпоінти Healthcheck (/healthz/live, /healthz/ready)
│   └── resources/
│       ├── auth.py                 # Публічні ендпоінти POST /register та POST /login
│       ├── users.py                # REST API користувачів з RBAC та зміною ролей
│       ├── categories.py           # REST API глобальних та персональних категорій
│       ├── accounts.py             # REST API рахунків користувача
│       └── records.py              # REST API витрат зі списанням коштів та фільтрацією
├── migrations/                     # Версіоновані міграції бази даних Alembic
├── tests/                          # Автоматизовані модульні та e2e тести (pytest)
├── bruno_collection/               # Колекція API-запитів у форматі Bruno OpenCollection
├── lab1/                           # Звіт та скріншоти виконання Лабораторної роботи №1
├── lab2/                           # Звіт та скріншоти виконання Лабораторної роботи №2
├── lab3/                           # Звіт та скріншоти виконання Лабораторної роботи №3
├── lab4/                           # Звіт та скріншоти виконання Лабораторної роботи №4
├── .dockerignore                   # Виключення файлів при збірці Docker-образу
├── .env.example                    # Шаблон змінних середовища для PostgreSQL та JWT
├── .gitignore                      # Виключення службових файлів для Git
├── Dockerfile                      # Конфігурація збірки контейнера застосунку з автоміграціями
├── docker-compose.yaml             # Оркестрація застосунку та PostgreSQL 16
├── pyproject.toml                  # Налаштування лінтера ruff
├── requirements.txt                # Зафіксовані залежності Python
└── run.py                          # Точка входу для запуску сервера
```

## Локальний запуск через Docker Compose

1. Клонувати репозиторій та перейти в кореневу директорію проєкту:

```bash
git clone https://github.com/Miniv812/Serv-Component.git
cd Serv-Component
```

2. Створити файл `.env` на основі шаблону `.env.example`:

```bash
cp .env.example .env
```

3. Зібрати Docker-образ та запустити застосунок разом із PostgreSQL 16:

```bash
docker compose up --build -d
```

4. Перевірити статус контейнерів:

```bash
docker compose ps
```

Після запуску сервер доступний за адресою `http://localhost:8080`, а PostgreSQL — на порту `5432`.

5. Зупинити контейнери (зі збереженням даних у volume `postgres_data`):

```bash
docker compose down
```

## Запуск тестів та локальна розробка без Docker

1. Активувати віртуальне середовище та встановити залежності:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Запустити перевірку лінтером `ruff` та набір тестів `pytest`:

```bash
ruff check .
pytest --maxfail=1 --disable-warnings -v
```

3. Застосувати міграції та запустити застосунок локально:

```bash
flask --app run db upgrade
python run.py
```
