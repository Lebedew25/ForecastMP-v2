# ForecastMP-v2: Inventory Management & Forecasting System

Multi-tenant SaaS platform for marketplace sellers to manage inventory, track sales, forecast demand, and automate procurement recommendations across multiple marketplaces (Wildberries, Ozon, custom websites).

## 🚀 Features

### Core Functionality
- **Multi-Warehouse Inventory Management**: Track stock across multiple warehouses and marketplace fulfillment centers
- **Sales Tracking**: Automated sales data synchronization from marketplaces
- **Simplified Forecasting**: Moving average-based demand forecasting
- **Procurement Recommendations**: Automated purchase order suggestions based on forecast and stock levels
- **Telegram Notifications**: Critical stock alerts, daily digests, and weekly reports
- **Data Export**: Export procurement orders in Excel, PDF, and CSV formats
- **Dashboard Analytics**: Real-time inventory metrics, turnover analysis, and forecast accuracy
- **Onboarding Wizard**: Step-by-step setup for new users

### Supported Marketplaces
- Wildberries (Russian marketplace)
- Ozon (Russian marketplace)
- Custom website integration via webhooks

## 📋 Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Task Queue**: Celery + Redis
- **Forecasting**: Simplified moving average (no ML dependencies)
- **Notifications**: Telegram Bot API
- **File Processing**: openpyxl (Excel), reportlab (PDF)

## 🏗️ Project Structure

```
ForecastMP-v2/
├── accounts/              # User authentication, companies, telegram subscriptions
├── products/              # Product catalog, marketplace product mappings
├── sales/                 # Sales transactions, inventory tracking, warehouses
├── integrations/          # Marketplace API clients, webhooks
├── forecasting/           # Demand forecasting engine
├── procurement/           # Procurement recommendations
├── telegram_notifications/ # Telegram bot notifications service
├── export/                # Export generation (Excel, PDF, CSV)
├── dashboard/             # Dashboard metrics and analytics
├── onboarding/            # User onboarding wizard
└── stockpredictor/        # Django project settings
```

## 🔧 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (set USE_SQLITE=False for PostgreSQL)
USE_SQLITE=True
DB_NAME=stockpredictor
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Telegram (optional)
# TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Verify Installation

```bash
python test_setup.py
```

## 🚀 Running the Application

### Development Server

```bash
python manage.py runserver
```

Access at: http://localhost:8000

### Celery Worker (Background Tasks)

```bash
celery -A stockpredictor worker -l info
```

### Celery Beat (Scheduled Tasks)

```bash
celery -A stockpredictor beat -l info
```

## 📊 Database Models

### Key Models

#### Accounts App
- **User**: Custom user model with company association
- **Company**: Multi-tenant company/organization
- **TelegramSubscription**: Telegram notification preferences

#### Products App
- **Product**: Core product catalog (SKU, name, cost, price)
- **MarketplaceProduct**: Product mapping to marketplace IDs

#### Sales App
- **Warehouse**: Warehouse locations and marketplace fulfillment centers
- **SalesTransaction**: Individual sales records
- **InventorySnapshot**: Daily inventory level snapshots
- **InventoryMovement**: Audit trail of all inventory changes

#### Integrations App
- **MarketplaceCredential**: API credentials for marketplace integrations
- **SyncHistory**: Synchronization log

#### Forecasting App
- **ForecastResult**: Demand forecast results

#### Procurement App
- **ProcurementRecommendation**: Purchase order suggestions

## 🔗 API Endpoints

### Inventory Management
- `POST /api/inventory/adjust/` - Adjust stock levels
- `POST /api/inventory/transfer/` - Transfer stock between warehouses
- `GET /api/inventory/movements/` - Get movement history

### Dashboard
- `GET /api/dashboard/metrics/` - Overall metrics
- `GET /api/dashboard/inventory-value/` - Inventory value over time
- `GET /api/dashboard/inventory-turnover/` - Turnover analysis
- `GET /api/dashboard/stock-status/` - Stock status distribution
- `GET /api/dashboard/urgent-products/` - Products needing attention

### Export
- `POST /api/export/procurement-orders/` - Export procurement orders

### Integrations
- `POST /api/webhooks/website/` - Website order webhook

## 📅 Scheduled Tasks

Configured in `settings.CELERY_BEAT_SCHEDULE`:

- **06:00 AM Daily**: Sync marketplace data
- **07:00 AM Daily**: Generate forecasts
- **07:30 AM Daily**: Analyze procurement needs
- **08:00 AM Daily**: Send Telegram daily digest
- **09:00 AM Monday**: Send Telegram weekly report

## 🎯 MVP Implementation Status

### ✅ Completed Phases

1. **Database Schema** - All models and migrations created
2. **Simplified Forecasting** - Moving average forecasting engine
3. **Product Import** - CSV/XLSX bulk import functionality
4. **Inventory Management** - Stock adjustments and movements
5. **Website Integration** - Webhook handler for custom websites
6. **Telegram Notifications** - Bot integration for alerts
7. **Export Functionality** - Excel, PDF, CSV export generation
8. **Enhanced Dashboard** - Real-time metrics and analytics
9. **Onboarding Wizard** - Step-by-step user setup
10. **Inventory Table UI** - Unified inventory view
11. **Data Migration** - Warehouse backfill and migration scripts

### 🔄 Scheduled Tasks Configured

- Marketplace data synchronization
- Daily forecast generation
- Procurement analysis
- Telegram notifications (daily/weekly)

## 🧪 Testing

Run verification script:

```bash
python test_setup.py
```

Run Django tests:

```bash
python manage.py test
```

## 📝 Next Steps

### For Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure PostgreSQL database (`USE_SQLITE=False`)
3. Set up Redis server for Celery
4. Configure proper `SECRET_KEY`
5. Set up Telegram bot and add token to `.env`
6. Configure marketplace API credentials via Django admin
7. Set up Nginx/Apache as reverse proxy
8. Configure SSL certificate
9. Set up monitoring and logging

### Optional Enhancements

- Frontend UI (React/Vue.js)
- Advanced ML forecasting models
- Multi-currency support
- More marketplace integrations
- Mobile app
- Advanced analytics and reporting

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates

## 📄 License

Proprietary - All rights reserved

## 👥 Support

For issues or questions, contact the development team.

---

**Version**: 1.0.0 (MVP)  
**Last Updated**: 2025
