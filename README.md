# ForecastMP-v2

Inventory and procurement platform for marketplace sellers. Django-based app with sales/inventory sync, procurement recommendations, and analytics.

## Features
- Multi-warehouse inventory tracking
- Marketplace sales/inventory sync
- Procurement recommendations and quick orders
- Dashboard analytics
- Data export
- Telegram notifications

## Tech
- Django 4.2
- Celery + Redis
- DB: SQLite (dev) / PostgreSQL (prod)
- Forecasting: XGBoost + simple forecast tasks
- Export: CSV/Excel/PDF

## Project layout
- `accounts/` — users, companies, subscriptions
- `products/` — product catalog and marketplace mapping
- `sales/` — sales, warehouses, inventory
- `integrations/` — marketplace sync
- `forecasting/` — demand forecasting
- `procurement/` — recommendations and orders
- `dashboard/` — metrics and analytics
- `export/` — export services
- `telegram_notifications/` — notifications
- `onboarding/` — onboarding wizard
- `templates/`, `static/` — server-rendered UI
- `stockpredictor/` — Django settings
- `tests_ui.py`, `tests_integration.py` — main tests

## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment (.env):
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   USE_SQLITE=True
   # PostgreSQL:
   # USE_SQLITE=False
   # DB_NAME=stockpredictor
   # DB_USER=postgres
   # DB_PASSWORD=postgres
   # DB_HOST=localhost
   # DB_PORT=5432

   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

3. Migrate:
   ```bash
   python manage.py migrate
   ```

4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run server:
   ```bash
   python manage.py runserver
   ```

## Tests
- Django:
  ```bash
  python manage.py test
  ```
- Pytest:
  ```bash
  DJANGO_SETTINGS_MODULE=stockpredictor.settings pytest tests_ui.py tests_integration.py -v
  ```

## Celery
- Worker (Windows):
  ```bash
  celery -A stockpredictor worker -l info --pool=solo
  ```
- Beat:
  ```bash
  celery -A stockpredictor beat -l info
  ```

## Docker
`docker-compose.yml` starts PostgreSQL and Redis:
```bash
docker-compose up -d
```
