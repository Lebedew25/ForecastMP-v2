# Frontend Integration Guide

## Overview
React фронтенд успешно интегрирован с Django backend. Приложение может работать в двух режимах: development и production.

## Development Mode (Рекомендуется для разработки)

### Запуск фронтенда и бэкенда одновременно:

**Terminal 1 - Django Backend:**
```powershell
# Активировать виртуальное окружение
.\venv\Scripts\Activate.ps1

# Запустить Django сервер
python manage.py runserver
```

**Terminal 2 - React Frontend:**
```powershell
# Перейти в директорию frontend
cd frontend

# Установить зависимости (только первый раз)
npm install

# Запустить dev сервер Vite
npm run dev
```

### Доступ к приложению:
- **Frontend (React):** http://localhost:5173
- **Backend (Django API):** http://localhost:8000
- **Django Admin:** http://localhost:8000/admin

В dev режиме Vite автоматически проксирует API запросы на Django backend.

## Production Mode

### Сборка фронтенда:
```powershell
cd frontend
npm run build
```

Это создаст production сборку в `static/frontend/`.

### Запуск только Django:
```powershell
python manage.py runserver
```

Django будет отдавать собранный React через http://localhost:8000

## API Endpoints

### Dashboard
- `GET /api/dashboard/metrics/` - все метрики дашборда
- `GET /api/dashboard/urgent-products/` - срочные товары
- `GET /api/dashboard/recent-activities/` - последние активности

### Products
- `GET /api/products/` - список товаров (с поиском и пагинацией)
- `GET /api/products/{id}/` - детали товара
- `GET /api/products/warehouses/` - список складов

### Inventory
- `GET /api/inventory/movements/` - движения по складу
- `POST /api/inventory/adjust/` - корректировка остатков
- `POST /api/inventory/transfer/` - перемещение между складами

## Troubleshooting

### Проблема: React не подключается к API
**Решение:** Убедитесь, что Django сервер запущен на порту 8000

### Проблема: CORS errors
**Решение:** Проверьте что в settings.py есть:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

### Проблема: 401 Unauthorized
**Решение:** Войдите через Django admin сначала: http://localhost:8000/admin

## Architecture

```
User Browser
    ↓
http://localhost:5173 (Vite Dev Server)
    ↓
/api/* requests → Proxy → http://localhost:8000 (Django)
    ↓
Django REST API
    ↓
PostgreSQL/SQLite Database
```

## Next Steps

1. ✅ Frontend настроен и работает
2. ✅ API endpoints созданы
3. ⏳ Нужно создать пользователя и компанию для тестирования
4. ⏳ Проверить все страницы React работают с реальными данными
