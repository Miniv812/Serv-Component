# Expense Tracker Backend

Серверний застосунок для обліку витрат, розроблений на Python та Flask у межах курсу «Технології розроблення серверних компонентів».

## Структура проєкту

```text
Serv-Component/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI (лінтинг, збірка образу, перевірка compose)
├── app/
│   ├── __init__.py                 # Фабрика Flask-застосунку, ініціалізація БД та Blueprints
│   ├── config.py                   # Конфігурація підключення до PostgreSQL
│   ├── extensions.py               # Ініціалізація SQLAlchemy та Flask-Migrate
│   ├── models.py                   # ORM-моделі (User, Category, Account, Record)
│   ├── schemas.py                  # Схеми валідації Marshmallow та DTO
│   ├── views.py                    # Системні ендпоінти Healthcheck (/healthz/live, /healthz/ready)
│   └── resources/
│       ├── users.py                # REST API для сутності User
│       ├── categories.py           # REST API для сутності Category
│       ├── accounts.py             # REST API для сутності Account 
│       └── records.py              # REST API та фільтрація для сутності Record
├── migrations/                     # Версіоновані міграції бази даних Alembic
├── bruno_collection/               # Колекція API-запитів у форматі Bruno OpenCollection
├── lab1/                           # Звіт та скріншоти виконання Лабораторної роботи №1
├── lab2/                           # Звіт та скріншоти виконання Лабораторної роботи №2
├── lab3/                           # Звіт та скріншоти виконання Лабораторної роботи №3
├── .dockerignore                   # Виключення файлів при збірці Docker-образу
├── .env.example                    # Шаблон змінних середовища для PostgreSQL
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

3. Зібрати Docker-образ та запустити застосунок разом із PostgreSQL 16 (міграції БД застосуються автоматично під час старту контейнера):

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

## Локальна розробка без Docker

1. Створити та активувати віртуальне середовище (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Встановити залежності:

```bash
pip install -r requirements.txt
```

3. Застосувати міграції бази даних:

```bash
flask --app run db upgrade
```

4. Запустити перевірку коду лінтером `ruff`:

```bash
ruff check .
```

5. Запустити застосунок локально:

```bash
python run.py
```