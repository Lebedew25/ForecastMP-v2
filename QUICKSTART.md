# Quick Start

## 1) Install dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Configure environment
Create `.env` in the project root:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 3) Migrate and create superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

## 4) Run the app
```bash
python manage.py runserver
```

## 5) Background tasks
```bash
celery -A stockpredictor worker -l info --pool=solo
celery -A stockpredictor beat -l info
```
