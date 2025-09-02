FROM python:3.9-slim

WORKDIR /app

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# По умолчанию запускаем инициализацию
CMD ["python", "init_app.py"] 