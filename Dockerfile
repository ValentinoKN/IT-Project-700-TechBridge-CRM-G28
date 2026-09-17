FROM python:3.12-slim
# Everything in the container lives under /app, which matches the volume in docker-compose.yml.
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Install packages before copying the whole project. Docker can reuse this layer when code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_demo && python manage.py runserver 0.0.0.0:8000"]
