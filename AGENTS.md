# Repository Guidelines

## Project Structure & Module Organization
- Django apps live at the repo root: `accounts/`, `products/`, `sales/`, `integrations/`, `forecasting/`, `procurement/`, `dashboard/`, `onboarding/`, `export/`, `telegram_notifications/`.
- Project configuration and settings are in `stockpredictor/`.
- Server-rendered UI assets are in `templates/` and `static/`.
- Tests are in root files: `tests_ui.py`, `tests_integration.py`, and `test_setup.py`.
- Optional frontend assets (if used) are in `frontend/src/` (Vite config in `frontend/vite.config.ts`).

## Build, Test, and Development Commands
- `pip install -r requirements.txt` installs backend dependencies.
- `python manage.py migrate` applies database migrations.
- `python manage.py runserver` starts the dev server at `http://localhost:8000`.
- `celery -A stockpredictor worker -l info --pool=solo` runs background jobs (Windows-friendly pool).
- `celery -A stockpredictor beat -l info` runs scheduled tasks.
- `docker-compose up -d` starts PostgreSQL and Redis containers.
- `python test_setup.py` runs a quick environment verification.
- `python manage.py test` runs Django tests; `pytest tests_ui.py tests_integration.py -v` runs the same suites via pytest.

## Coding Style & Naming Conventions
- Python: 4-space indentation, follow Django and PEP 8 conventions.
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_CASE` for constants.
- Formatting and linting tools are available in `requirements.txt`: `black .` and `flake8`.

## Testing Guidelines
- Primary test modules: `tests_ui.py` and `tests_integration.py`.
- Test classes end with `Tests`, and test methods use the `test_` prefix.
- Run focused tests via Django: `python manage.py test tests_ui.DashboardUITests`.

## Commit & Pull Request Guidelines
- Use Conventional Commits as seen in history: `feat(scope): ...`, `fix(scope): ...`, `refactor(scope): ...` (example scope: `procurement`, `dashboard`).
- PRs should include a clear description, list of tests run, and screenshots or GIFs for UI changes.

## Security & Configuration Tips
- Keep secrets in `.env`; do not commit real tokens or passwords.
- For production-like runs, set `DEBUG=False` and point to PostgreSQL/Redis via environment variables.
