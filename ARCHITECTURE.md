# Architecture (short)

Monolithic Django application with Celery for background jobs.

## Core components
- Apps: `accounts`, `products`, `sales`, `integrations`, `forecasting`, `procurement`, `dashboard`, `export`, `telegram_notifications`, `onboarding`.
- Database: SQLite in dev, PostgreSQL in prod.
- Celery + Redis for sync, forecasting, and notifications.

## Data flows (simplified)
- `integrations.tasks.sync_*` for marketplace sync.
- `forecasting.tasks` for forecast generation.
- `procurement` for recommendations and orders.

## UI
- Server-rendered templates in `templates/`.
- `frontend/` exists as optional frontend, not wired into the current UI.
