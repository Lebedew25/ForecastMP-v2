# React Frontend Integration - Summary

## 🎯 Что было сделано

### 1. Django Backend Configuration

#### Settings (stockpredictor/settings.py)
- ✅ Добавлена поддержка статических файлов
- ✅ Настроены TEMPLATES для использования базовых шаблонов
- ✅ CORS настроен для портов 5173, 5174 (Vite dev server)
- ✅ CORS_ALLOW_CREDENTIALS = True для session auth

#### URL Routing (stockpredictor/urls.py)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/dashboard/', include('dashboard.urls')),
    path('api/products/', include('products.urls')),
    path('api/inventory/', include('sales.urls')),
    path('api/telegram/', include('telegram_notifications.urls')),
    path('api/export/', include('export.urls')),
    # Legacy HTML views (backward compatibility)
    path('legacy/onboarding/', include('onboarding.urls')),
    path('legacy/dashboard/', include('procurement.urls')),
    # React SPA - catch-all route
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
```

#### Template (templates/index.html)
- ✅ Универсальный шаблон работает в dev и production режимах
- ✅ Dev mode: подключается к Vite dev server
- ✅ Production mode: использует статические файлы

### 2. API Endpoints Created

#### Dashboard API (dashboard/views.py & urls.py)
- `GET /api/dashboard/metrics/` - все метрики
- `GET /api/dashboard/inventory-value/` - стоимость инвентаря
- `GET /api/dashboard/inventory-turnover/` - оборачиваемость
- `GET /api/dashboard/stock-status/` - статусы остатков
- `GET /api/dashboard/urgent-products/` - срочные товары
- `GET /api/dashboard/recent-activities/` - последние активности
- `GET /api/dashboard/forecast-accuracy/` - точность прогнозов

#### Products API (products/views.py & urls.py) - НОВОЕ
- `GET /api/products/` - список товаров с фильтрами
- `GET /api/products/{id}/` - детали товара
- `GET /api/products/warehouses/` - список складов

Параметры для списка товаров:
- `search` - поиск по name, sku, description
- `page` - номер страницы
- `page_size` - размер страницы (max 100)
- `warehouse_id` - фильтр по складу

#### Inventory API (sales/views.py & urls.py)
- `POST /api/inventory/adjust/` - корректировка остатков
- `POST /api/inventory/transfer/` - перемещение между складами
- `GET /api/inventory/status/` - текущие остатки
- `GET /api/inventory/history/{product_id}/` - история движений
- `GET /api/inventory/movements/` - все движения с фильтрами

### 3. Frontend Configuration

#### Vite Config (frontend/vite.config.ts)
```typescript
server: {
  port: 5173, // или 5174 если 5173 занят
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    },
    '/admin': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

#### Build Config
- Output directory: `../static/frontend/`
- Code splitting: vendor, antd, charts chunks
- Production build создает минифицированные JS/CSS

### 4. API Service (frontend/src/services/api.ts)
```typescript
class ApiService {
  // Authentication
  getCurrentUser()
  logout()
  
  // Dashboard
  getDashboardMetrics()
  getUrgentProducts(limit)
  getRecentActivities(limit)
  
  // Products
  getProducts(params)
  getProduct(id)
  createProduct(data)
  updateProduct(id, data)
  deleteProduct(id)
  
  // Warehouses
  getWarehouses()
  
  // Inventory
  adjustInventory(data)
  transferInventory(data)
  getInventoryMovements(params)
}
```

## 📊 Architecture Flow

### Development Mode
```
User → http://localhost:5174 (Vite)
     → /api/* → Proxy → http://localhost:8000 (Django)
     → Django REST API → Database
```

### Production Mode
```
User → http://localhost:8000 (Django)
     → Serves React SPA from static files
     → /api/* → Django REST API → Database
```

## 🔑 Key Files Modified/Created

### Created:
1. `templates/index.html` - главный шаблон
2. `products/urls.py` - products API routes
3. `products/views.py` - products API views (ProductsListView, ProductDetailView, WarehousesListView)
4. `static/` - директория для статики
5. `QUICKSTART_REACT.md` - инструкция по запуску
6. `REACT_INTEGRATION_SUMMARY.md` - этот файл

### Modified:
1. `stockpredictor/settings.py` - статика, шаблоны, CORS
2. `stockpredictor/urls.py` - роутинг API и SPA
3. `dashboard/urls.py` - убрана дупликация /api/
4. `frontend/vite.config.ts` - порт и proxy
5. `README.md` - добавлен Quick Start

## 🚀 How to Run

### Development (2 terminals):
```powershell
# Terminal 1 - Django
.\venv\Scripts\Activate.ps1
python manage.py runserver

# Terminal 2 - React
cd frontend
npm install  # first time only
npm run dev
```

Open: http://localhost:5174

### Production (1 terminal):
```powershell
# Build frontend
cd frontend
npm run build

# Run Django (serves React + API)
cd ..
python manage.py runserver
```

Open: http://localhost:8000

## ⚠️ Important Notes

### Authentication
- React использует Django Session Authentication
- Нужно сначала войти через `/admin/`
- CSRF token автоматически добавляется к запросам

### Company Assignment
- Пользователь должен иметь назначенную компанию
- Без компании API вернет 403 Forbidden
- Назначить можно через Django admin или shell

### API Response Format
```json
{
  "success": true,
  "products": [...],
  "page": 1,
  "page_size": 50,
  "total_count": 150
}
```

## 🎉 Result

✅ React SPA полностью интегрирован с Django
✅ API endpoints работают
✅ Dev mode с HMR настроен
✅ Production build готов
✅ Все страницы React доступны через роутинг

## 📝 Next Steps

1. Войти в систему через `/admin/`
2. Создать компанию и назначить пользователю
3. Создать склады и товары
4. Открыть React app и проверить все страницы
5. При необходимости добавить дополнительные API endpoints
