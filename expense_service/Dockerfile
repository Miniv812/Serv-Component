FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY observability/ ./observability/
COPY expense_service/expense_app/ ./expense_app/
COPY expense_service/migrations/ ./migrations/
COPY expense_service/run.py .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "flask --app run db upgrade && python run.py"]
