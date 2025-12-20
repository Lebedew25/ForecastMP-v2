"""
Скрипт для создания тестовых данных для работы интерфейса
"""
import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from accounts.models import Company, User
from products.models import Product
from procurement.models import ProcurementRecommendation, PurchaseOrder, PurchaseOrderItem

def create_test_data():
    """Создаем тестовые данные"""
    
    # Проверяем, есть ли компания
    company = Company.objects.first()
    if not company:
        print("Создаем тестовую компанию...")
        company = Company.objects.create(name="Тестовая Компания")
        print(f"✓ Компания создана: {company.name}")
    else:
        print(f"✓ Используем существующую компанию: {company.name}")
    
    # Проверяем, есть ли пользователь
    user = User.objects.filter(company=company).first()
    if not user:
        print("Создаем тестового пользователя...")
        user = User.objects.create_user(
            email="admin@test.com",
            password="admin123",
            first_name="Админ",
            last_name="Тестовый"
        )
        user.company = company
        user.save()
        print(f"✓ Пользователь создан: {user.email} (пароль: admin123)")
    else:
        print(f"✓ Используем существующего пользователя: {user.email}")
    
    # Создаем продукты
    print("\nСоздаем тестовые продукты...")
    categories = ['Электроника', 'Одежда', 'Продукты питания', 'Бытовая техника']
    products = []
    
    for i in range(20):
        category = categories[i % len(categories)]
        product = Product.objects.create(
            company=company,
            sku=f"TEST-{i+1:04d}",
            name=f"Тестовый товар {i+1}",
            category=category
        )
        products.append(product)
    
    print(f"✓ Создано {len(products)} продуктов")
    
    # Создаем рекомендации по закупкам
    print("\nСоздаем рекомендации по закупкам...")
    today = date.today()
    statuses = ['ORDER_TODAY', 'ATTENTION_REQUIRED', 'NORMAL', 'ALREADY_ORDERED']
    
    for i, product in enumerate(products):
        status = statuses[i % len(statuses)]
        
        # Варьируем параметры в зависимости от статуса
        if status == 'ORDER_TODAY':
            current_stock = 5 + i
            runway_days = 3 + (i % 5)
            recommended_qty = 100 + (i * 10)
            priority = Decimal('95.0') - (i * 2)
        elif status == 'ATTENTION_REQUIRED':
            current_stock = 20 + i
            runway_days = 10 + (i % 5)
            recommended_qty = 50 + (i * 5)
            priority = Decimal('70.0') - i
        elif status == 'ALREADY_ORDERED':
            current_stock = 15 + i
            runway_days = 7 + (i % 5)
            recommended_qty = 75 + (i * 7)
            priority = Decimal('60.0') - i
        else:  # NORMAL
            current_stock = 100 + (i * 5)
            runway_days = 30 + (i % 10)
            recommended_qty = 0
            priority = Decimal('30.0') - i
        
        rec = ProcurementRecommendation.objects.create(
            product=product,
            analysis_date=today,
            current_stock=current_stock,
            runway_days=runway_days,
            stockout_date=today + timedelta(days=runway_days) if runway_days < 30 else None,
            daily_burn_rate=Decimal(str(2.5 + (i % 5) * 0.5)),
            recommended_quantity=recommended_qty,
            action_category=status,
            priority_score=priority,
            notes=f"Автоматическая рекомендация для {product.name}"
        )
    
    print(f"✓ Создано {len(products)} рекомендаций")
    
    # Создаем несколько тестовых заказов
    print("\nСоздаем тестовые заказы...")
    order_statuses = ['DRAFT', 'SUBMITTED', 'CONFIRMED', 'IN_TRANSIT']
    
    for i in range(5):
        po = PurchaseOrder.objects.create(
            company=company,
            po_number=f"PO-{today.strftime('%Y%m%d')}-{i+1:03d}",
            order_date=today - timedelta(days=i),
            expected_delivery=today + timedelta(days=14 - i),
            status=order_statuses[i % len(order_statuses)],
            supplier_name=f"Поставщик {i+1}",
            notes=f"Тестовый заказ #{i+1}"
        )
        
        # Добавляем 2-3 товара в каждый заказ
        for j in range(2 + (i % 2)):
            product = products[(i * 3 + j) % len(products)]
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=product,
                quantity_ordered=50 + (j * 25),
                unit_cost=Decimal(str(100 + (j * 50)))
            )
    
    print(f"✓ Создано 5 тестовых заказов")
    
    # Финальная статистика
    print("\n" + "="*60)
    print("ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
    print("="*60)
    print(f"Компания: {company.name}")
    print(f"Пользователь: {user.email}")
    print(f"  Пароль: admin123")
    print(f"Продуктов: {Product.objects.filter(company=company).count()}")
    print(f"Рекомендаций: {ProcurementRecommendation.objects.count()}")
    print(f"  - Заказать сегодня: {ProcurementRecommendation.objects.filter(action_category='ORDER_TODAY').count()}")
    print(f"  - Требует внимания: {ProcurementRecommendation.objects.filter(action_category='ATTENTION_REQUIRED').count()}")
    print(f"  - Норма: {ProcurementRecommendation.objects.filter(action_category='NORMAL').count()}")
    print(f"  - Уже заказано: {ProcurementRecommendation.objects.filter(action_category='ALREADY_ORDERED').count()}")
    print(f"Заказов: {PurchaseOrder.objects.filter(company=company).count()}")
    print("="*60)
    print("\nТеперь можете войти в систему и проверить работу интерфейса!")
    print("URL: http://localhost:8000")
    print(f"Email: {user.email}")
    print("Пароль: admin123")

if __name__ == '__main__':
    create_test_data()
