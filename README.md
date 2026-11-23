# Expense Tracker Backend

Серверний застосунок для обліку витрат, розроблений на Python та Flask у межах курсу «Технології розроблення серверних компонентів».

## Структура проєкту

```text
Serv-Component/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI (лінтинг, збірка образу, перевірка compose)
├── app/
│   ├── __init__.py         # Фабрика Flask-застосунку
│   └── views.py            # Маршрути API
├── lab1/                   # Звіт та скріншоти виконання Лабораторної роботи №1
├── .dockerignore           # Виключення файлів при збірці Docker-образу
├── .gitignore              # Виключення службових файлів для Git
├── Dockerfile              # Конфігурація збірки контейнера застосунку
├── docker-compose.yaml     # Оркестрація сервісів для локального запуску
├── pyproject.toml          # Налаштування лінтера ruff
├── requirements.txt        # Зафіксовані залежності Python
└── run.py                  # Точка входу для запуску сервера
```

## Локальний запуск через Docker Compose

1. Клонувати репозиторій та перейти в кореневу директорію проєкту:

```bash
git clone https://github.com/Miniv812/Serv-Component.git
cd Serv-Component
```

2. Зібрати Docker-образ та запустити сервіс у фоновому режимі:

```bash
docker compose up --build -d
```

3. Перевірити статус запущеного контейнера:

```bash
docker compose ps
```

Після запуску сервер доступний за адресою `http://localhost:8080`.

4. Зупинити та видалити контейнери:

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

3. Запустити перевірку коду лінтером `ruff`:

```bash
ruff check .
```

4. Запустити застосунок локально:

```bash
python run.py
```