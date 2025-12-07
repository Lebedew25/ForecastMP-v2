# 🚀 Быстрый старт StockPredictor

## Первоначальная настройка

### 1. Установка зависимостей

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка базы данных PostgreSQL

```sql
-- Подключитесь к PostgreSQL
psql -U postgres

-- Создайте базу данных
CREATE DATABASE stockpredictor;

-- Создайте пользователя (опционально)
CREATE USER stockpredictor_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stockpredictor TO stockpredictor_user;

\q
```

### 3. Применение миграций

```bash
# Создать миграции для всех приложений
python manage.py makemigrations accounts
python manage.py makemigrations products
python manage.py makemigrations sales
python manage.py makemigrations integrations
python manage.py makemigrations forecasting
python manage.py makemigrations procurement

# Применить все миграции
python manage.py migrate
```

### 4. Создание суперпользователя

```bash
python manage.py createsuperuser
# Введите email и пароль
```

### 5. Создание тестовой компании и данных через админку

```bash
# Запустите сервер
python manage.py runserver

# Откройте браузер: http://127.0.0.1:8000/admin/
```

**В админке создайте:**
1. **Company** - вашу компанию
2. **User** - привяжите к созданной компании (или обновите суперпользователя)
3. **Product** - несколько тестовых товаров
4. **MarketplaceProduct** - маппинг товаров на маркетплейсы
5. **ProductAttributes** - настройки закупок для товаров

### 6. Запуск Redis (для Celery)

**Windows:**
```bash
# Скачайте Redis для Windows или используйте Docker
docker run -d -p 6379:6379 redis:latest
```

**Linux/macOS:**
```bash
redis-server
```

### 7. Запуск Celery worker

**В новом терминале:**
```bash
# Активируйте venv
venv\Scripts\activate

# Запустите worker
celery -A stockpredictor worker -l info --pool=solo
```

> **Примечание:** На Windows используйте `--pool=solo` или установите `eventlet`:
> ```bash
> pip install eventlet
> celery -A stockpredictor worker -l info -P eventlet
> ```

### 8. Запуск Celery beat (scheduled tasks)

**В ещё одном терминале:**
```bash
# Активируйте venv
venv\Scripts\activate

# Запустите beat scheduler
celery -A stockpredictor beat -l info
```

## 🎯 Проверка работы системы

### 1. Ручной запуск синхронизации (тест)

```python
# В Django shell
python manage.py shell

from integrations.tasks import sync_all_marketplaces
from forecasting.tasks import generate_all_forecasts
from procurement.tasks import analyze_all_procurement

# Запустите задачи вручную для теста
sync_all_marketplaces.delay()
generate_all_forecasts.delay()
analyze_all_procurement.delay()
```

### 2. Просмотр Dashboard

Откройте браузер: **http://127.0.0.1:8000/dashboard/**

Вы должны увидеть dashboard с категориями:
- 🔴 Order Today
- ⚠️ Attention Required
- ✅ Already Ordered

## 📊 Тестовые данные

### Создание тестовых продаж

```python
from datetime import date, timedelta
from products.models import Product
from sales.models import SalesTransaction, DailySalesAggregate
from decimal import Decimal
import random

# Получите продукт
product = Product.objects.first()

# Создайте продажи за последние 60 дней
for i in range(60):
    sale_date = date.today() - timedelta(days=i)
    quantity = random.randint(5, 20)
    
    SalesTransaction.objects.create(
        product=product,
        marketplace='WILDBERRIES',
        sale_date=sale_date,
        quantity=quantity,
        revenue=Decimal(quantity * 500)
    )

# Обновите агрегаты
from integrations.tasks import update_daily_aggregates
update_daily_aggregates.delay(
    str(product.company.id),
    date.today() - timedelta(days=60),
    date.today()
)
```

### Создание тестового инвентаря

```python
from sales.models import InventorySnapshot
from datetime import date

product = Product.objects.first()

InventorySnapshot.objects.create(
    product=product,
    snapshot_date=date.today(),
    quantity_available=100,
    quantity_reserved=10
)
```

## 🔄 Автоматические задачи

Celery Beat автоматически запускает следующие задачи:

- **6:00 AM** - Синхронизация с маркетплейсами (`sync_all_marketplaces`)
- **7:00 AM** - Генерация прогнозов (`generate_all_forecasts`)
- **7:30 AM** - Анализ закупок (`analyze_all_procurement`)

## 🐛 Отладка

### Проверка статуса Celery

```bash
# Проверка подключения к Redis
redis-cli ping
# Должно вернуть: PONG

# Список активных задач Celery
celery -A stockpredictor inspect active

# Список зарегистрированных задач
celery -A stockpredictor inspect registered
```

### Логи

```bash
# Django логи
tail -f django.log

# Celery логи - в консоли где запущен worker
```

### Очистка очереди Celery

```bash
celery -A stockpredictor purge
```

## 📝 Полезные команды Django

```bash
# Создание новых миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Django shell
python manage.py shell

# Сброс базы (осторожно!)
python manage.py flush

# Создание дампа данных
python manage.py dumpdata > backup.json

# Загрузка дампа
python manage.py loaddata backup.json
```

## ✅ Чеклист для продакшена

- [ ] Изменить `SECRET_KEY` в `.env`
- [ ] Установить `DEBUG=False`
- [ ] Настроить `ALLOWED_HOSTS`
- [ ] Настроить HTTPS
- [ ] Настроить production базу данных
- [ ] Настроить Gunicorn/uWSGI
- [ ] Настроить Nginx
- [ ] Настроить мониторинг (Sentry, Prometheus)
- [ ] Настроить backup базы данных
- [ ] Настроить логирование
- [ ] Добавить CORS настройки для API
- [ ] Шифрование API ключей маркетплейсов

## 🆘 Помощь

Если возникли проблемы:
1. Проверьте, что PostgreSQL запущен
2. Проверьте, что Redis запущен
3. Проверьте логи Celery worker
4. Проверьте миграции применены: `python manage.py showmigrations`
5. Создайте issue в репозитории с описанием проблемы
