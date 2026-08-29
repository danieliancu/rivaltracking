FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ ./requirements/

RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Default (web) command: apply migrations on startup (idempotent), then serve.
# DJANGO_SETTINGS_MODULE and DB_*/REDIS_URL come from the environment.
# Run the Phase 3 engine as separate services from this same image:
#   worker: celery -A config worker -l info -Q scraping,processing,matching,ai,alerts,reports
#   beat:   celery -A config beat -l info        (never inside the web process)
# Seed the demo workspace once with: python manage.py seed_demo
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]