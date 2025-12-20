"""
Integration Tests for UI Components
Интеграционные тесты для проверки взаимодействия компонентов интерфейса
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Company
from products.models import Product
from procurement.models import ProcurementRecommendation, PurchaseOrder, PurchaseOrderItem
from sales.models import DailySalesAggregate

User = get_user_model()


class OrderCreationWorkflowTests(TestCase):
    """Тесты полного цикла создания заказа"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем продукты
        today = date.today()
        self.products = []
        for i in range(3):
            product = Product.objects.create(
                company=self.company,
                sku=f"WF-{i:03d}",
                name=f"Workflow Product {i}"
            )
            self.products.append(product)
            
            ProcurementRecommendation.objects.create(
                product=product,
                analysis_date=today,
                current_stock=10,
                runway_days=5,
                daily_burn_rate=Decimal('2.0'),
                recommended_quantity=50,
                action_category='ORDER_TODAY',
                priority_score=Decimal('90.0')
            )
        
        self.client = Client()
        
    def test_complete_order_creation_workflow(self):
        """Проверка полного цикла создания заказа"""
        self.client.force_login(self.user)
        
        # Шаг 1: Загрузка таблицы закупок
        response = self.client.get(reverse('procurement:buying_table'))
        self.assertEqual(response.status_code, 200)
        
        # Шаг 2: Создание формы заказа с выбранными продуктами
        product_ids = [p.id for p in self.products]
        response = self.client.post(
            reverse('procurement:create_order'),
            {'product_ids': product_ids}
        )
        self.assertEqual(response.status_code, 200)
        
        # Шаг 3: Отправка заказа
        order_data = {
            'supplier_name': 'Test Supplier',
            'notes': 'Test order',
            'product_ids': product_ids,
        }
        
        # Добавляем количество и стоимость для каждого продукта
        for product in self.products:
            order_data[f'quantity_{product.id}'] = '50'
            order_data[f'unit_cost_{product.id}'] = '100.00'
        
        response = self.client.post(
            reverse('procurement:submit_order'),
            order_data
        )
        
        # Проверяем переадресацию на страницу деталей заказа
        self.assertEqual(response.status_code, 302)
        
        # Шаг 4: Проверяем что заказ создан
        po = PurchaseOrder.objects.filter(company=self.company).first()
        self.assertIsNotNone(po)
        self.assertEqual(po.supplier_name, 'Test Supplier')
        self.assertEqual(po.status, 'SUBMITTED')
        self.assertEqual(po.items.count(), 3)
        
    def test_quick_order_workflow(self):
        """Проверка быстрого создания заказа"""
        self.client.force_login(self.user)
        
        # Создаем быстрый заказ
        response = self.client.post(
            reverse('procurement:quick_order', kwargs={'product_id': self.products[0].id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Проверяем переход на страницу деталей
        po_id = data['redirect_url'].split('/')[-2]
        response = self.client.get(
            reverse('procurement:purchase_order_detail', kwargs={'po_id': po_id})
        )
        self.assertEqual(response.status_code, 200)


class FilterAndSearchWorkflowTests(TestCase):
    """Тесты работы фильтров и поиска"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем продукты разных категорий
        today = date.today()
        categories = ['Electronics', 'Clothing', 'Food']
        statuses = ['ORDER_TODAY', 'ATTENTION_REQUIRED', 'NORMAL']
        
        for i, (category, status) in enumerate(zip(categories, statuses)):
            product = Product.objects.create(
                company=self.company,
                sku=f"FILTER-{i:03d}",
                name=f"Filter Product {i}",
                category=category
            )
            
            ProcurementRecommendation.objects.create(
                product=product,
                analysis_date=today,
                current_stock=10 + i * 10,
                runway_days=5 + i * 10,
                daily_burn_rate=Decimal('2.0'),
                recommended_quantity=50,
                action_category=status,
                priority_score=Decimal('80.0')
            )
        
        self.client = Client()
        
    def test_multiple_filters_combination(self):
        """Проверка комбинации нескольких фильтров"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('procurement:buying_table'), {
            'category': 'Electronics',
            'health_status': 'ORDER_TODAY'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FILTER-000')
        
    def test_search_and_filter_combination(self):
        """Проверка комбинации поиска и фильтра"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('procurement:buying_table'), {
            'search': 'Filter Product',
            'category': 'Clothing'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FILTER-001')
        
    def test_filter_reset_functionality(self):
        """Проверка сброса фильтров"""
        self.client.force_login(self.user)
        
        # Применяем фильтр
        response = self.client.get(reverse('procurement:buying_table'), {
            'category': 'Electronics'
        })
        self.assertEqual(response.status_code, 200)
        
        # Сбрасываем фильтр
        response = self.client.get(reverse('procurement:buying_table'))
        self.assertEqual(response.status_code, 200)
        # Все продукты должны быть видны
        self.assertContains(response, 'FILTER-000')
        self.assertContains(response, 'FILTER-001')
        self.assertContains(response, 'FILTER-002')


class DashboardDataIntegrationTests(TestCase):
    """Тесты интеграции данных на дашборде"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем продукты с разными статусами
        today = date.today()
        statuses = ['NORMAL'] * 70 + ['ATTENTION_REQUIRED'] * 20 + ['ORDER_TODAY'] * 10
        
        for i, status in enumerate(statuses):
            product = Product.objects.create(
                company=self.company,
                sku=f"DASH-{i:03d}",
                name=f"Dashboard Product {i}"
            )
            
            ProcurementRecommendation.objects.create(
                product=product,
                analysis_date=today,
                current_stock=10,
                runway_days=30 if status == 'NORMAL' else 5,
                daily_burn_rate=Decimal('2.0'),
                recommended_quantity=0 if status == 'NORMAL' else 50,
                action_category=status,
                priority_score=Decimal('50.0') if status == 'NORMAL' else Decimal('90.0')
            )
        
        self.client = Client()
        
    def test_dashboard_metrics_calculation(self):
        """Проверка расчета метрик на дашборде"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('dashboard:dashboard_metrics'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        
    def test_dashboard_shows_correct_statistics(self):
        """Проверка корректности статистики на дашборде"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('procurement:buying_table'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем что статистика отображается корректно
        summary = response.context['summary']
        self.assertEqual(summary['normal_count'], 70)
        self.assertEqual(summary['attention_count'], 20)
        self.assertEqual(summary['order_today_count'], 10)


class ExportIntegrationTests(TestCase):
    """Тесты экспорта данных"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем тестовые данные
        today = date.today()
        for i in range(5):
            product = Product.objects.create(
                company=self.company,
                sku=f"EXPORT-{i:03d}",
                name=f"Export Product {i}",
                category="Test Category"
            )
            
            ProcurementRecommendation.objects.create(
                product=product,
                analysis_date=today,
                current_stock=100,
                runway_days=30,
                daily_burn_rate=Decimal('3.5'),
                recommended_quantity=50,
                action_category='NORMAL',
                stockout_date=today + timedelta(days=30),
                priority_score=Decimal('60.0')
            )
        
        self.client = Client()
        
    def test_export_with_filters(self):
        """Проверка экспорта с применением фильтров"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('procurement:export_buying_table'), {
            'category': 'Test Category'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        content = response.content.decode('utf-8')
        # Проверяем наличие заголовков
        self.assertIn('SKU', content)
        self.assertIn('Название', content)
        
        # Проверяем наличие данных
        for i in range(5):
            self.assertIn(f'EXPORT-{i:03d}', content)
            
    def test_export_csv_format(self):
        """Проверка формата CSV файла"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('procurement:export_buying_table'))
        
        content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        
        # Проверяем наличие заголовка
        self.assertGreater(len(lines), 1)
        
        # Проверяем что данные разделены запятыми
        header = lines[0]
        self.assertIn(',', header)


class UserAccessControlTests(TestCase):
    """Тесты контроля доступа пользователей"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем две компании
        self.company1 = Company.objects.create(
            name="Company 1"
        )
        
        self.company2 = Company.objects.create(
            name="Company 2"
        )
        
        # Создаем пользователей для каждой компании
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="pass123"
        )
        self.user1.company = self.company1
        self.user1.save()
        
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="pass123"
        )
        self.user2.company = self.company2
        self.user2.save()
        
        # Создаем продукт для company1
        self.product1 = Product.objects.create(
            company=self.company1,
            sku="ACCESS-001",
            name="Product for Company 1"
        )
        
        # Создаем заказ для company1
        self.po1 = PurchaseOrder.objects.create(
            company=self.company1,
            po_number="PO-COMPANY1-001",
            order_date=date.today(),
            status='DRAFT'
        )
        
        self.client = Client()
        
    def test_user_cannot_access_other_company_products(self):
        """Проверка что пользователь не может видеть продукты другой компании"""
        self.client.force_login(self.user2)
        
        response = self.client.get(
            reverse('procurement:product_detail', kwargs={'product_id': self.product1.id})
        )
        
        # Должна быть ошибка 404
        self.assertEqual(response.status_code, 404)
        
    def test_user_cannot_access_other_company_orders(self):
        """Проверка что пользователь не может видеть заказы другой компании"""
        self.client.force_login(self.user2)
        
        response = self.client.get(
            reverse('procurement:purchase_order_detail', kwargs={'po_id': self.po1.id})
        )
        
        # Должна быть ошибка 404
        self.assertEqual(response.status_code, 404)
        
    def test_user_sees_only_own_company_data(self):
        """Проверка что пользователь видит только данные своей компании"""
        # Создаем рекомендации для обеих компаний
        today = date.today()
        
        ProcurementRecommendation.objects.create(
            product=self.product1,
            analysis_date=today,
            current_stock=10,
            runway_days=5,
            daily_burn_rate=Decimal('2.0'),
            recommended_quantity=50,
            action_category='ORDER_TODAY',
            priority_score=Decimal('95.0')
        )
        
        product2 = Product.objects.create(
            company=self.company2,
            sku="ACCESS-002",
            name="Product for Company 2"
        )
        
        ProcurementRecommendation.objects.create(
            product=product2,
            analysis_date=today,
            current_stock=10,
            runway_days=5,
            daily_burn_rate=Decimal('2.0'),
            recommended_quantity=50,
            action_category='ORDER_TODAY',
            priority_score=Decimal('95.0')
        )
        
        # Логинимся как user1
        self.client.force_login(self.user1)
        response = self.client.get(reverse('procurement:buying_table'))
        
        # Должны видеть только продукты company1
        self.assertContains(response, 'ACCESS-001')
        self.assertNotContains(response, 'ACCESS-002')


class StatusWorkflowTests(TestCase):
    """Тесты жизненного цикла статусов заказов"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        self.product = Product.objects.create(
            company=self.company,
            sku="STATUS-001",
            name="Status Test Product"
        )
        
        self.po = PurchaseOrder.objects.create(
            company=self.company,
            po_number="PO-STATUS-001",
            order_date=date.today(),
            status='DRAFT'
        )
        
        PurchaseOrderItem.objects.create(
            purchase_order=self.po,
            product=self.product,
            quantity_ordered=100
        )
        
        self.client = Client()
        
    def test_order_status_progression(self):
        """Проверка последовательности изменения статусов заказа"""
        self.client.force_login(self.user)
        
        # DRAFT -> SUBMITTED
        response = self.client.post(
            reverse('procurement:update_order_status', kwargs={'po_id': self.po.id}),
            {'status': 'SUBMITTED'}
        )
        self.assertEqual(response.status_code, 200)
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, 'SUBMITTED')
        
        # SUBMITTED -> CONFIRMED
        response = self.client.post(
            reverse('procurement:update_order_status', kwargs={'po_id': self.po.id}),
            {'status': 'CONFIRMED'}
        )
        self.assertEqual(response.status_code, 200)
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, 'CONFIRMED')
        
        # CONFIRMED -> IN_TRANSIT
        response = self.client.post(
            reverse('procurement:update_order_status', kwargs={'po_id': self.po.id}),
            {'status': 'IN_TRANSIT'}
        )
        self.assertEqual(response.status_code, 200)
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, 'IN_TRANSIT')
        
        # IN_TRANSIT -> DELIVERED
        response = self.client.post(
            reverse('procurement:update_order_status', kwargs={'po_id': self.po.id}),
            {'status': 'DELIVERED'}
        )
        self.assertEqual(response.status_code, 200)
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, 'DELIVERED')
        # Проверяем что дата доставки установлена
        self.assertIsNotNone(self.po.actual_delivery)
        
    def test_filter_orders_by_different_statuses(self):
        """Проверка фильтрации заказов по разным статусам"""
        # Создаем заказы с разными статусами
        statuses = ['DRAFT', 'SUBMITTED', 'CONFIRMED', 'IN_TRANSIT', 'DELIVERED']
        
        for status in statuses:
            PurchaseOrder.objects.create(
                company=self.company,
                po_number=f"PO-{status}-001",
                order_date=date.today(),
                status=status
            )
        
        self.client.force_login(self.user)
        
        # Проверяем фильтрацию по каждому статусу
        for status in statuses:
            response = self.client.get(reverse('procurement:purchase_orders'), {
                'status': status
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f'PO-{status}-001')


class UIPerformanceTests(TestCase):
    """Тесты производительности интерфейса"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем большое количество данных для тестирования производительности
        today = date.today()
        for i in range(100):
            product = Product.objects.create(
                company=self.company,
                sku=f"PERF-{i:03d}",
                name=f"Performance Test Product {i}"
            )
            
            ProcurementRecommendation.objects.create(
                product=product,
                analysis_date=today,
                current_stock=10,
                runway_days=5,
                daily_burn_rate=Decimal('2.0'),
                recommended_quantity=50,
                action_category='NORMAL',
                priority_score=Decimal('50.0')
            )
        
        self.client = Client()
        
    def test_buying_table_loads_with_many_products(self):
        """Проверка загрузки таблицы закупок с большим количеством продуктов"""
        self.client.force_login(self.user)
        
        import time
        start_time = time.time()
        
        response = self.client.get(reverse('procurement:buying_table'))
        
        end_time = time.time()
        load_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # Страница должна загрузиться за разумное время (< 5 секунд)
        self.assertLess(load_time, 5.0)
        
    def test_dashboard_metrics_performance(self):
        """Проверка производительности загрузки метрик дашборда"""
        self.client.force_login(self.user)
        
        import time
        start_time = time.time()
        
        response = self.client.get(reverse('dashboard:dashboard_metrics'))
        
        end_time = time.time()
        load_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        # API должно отвечать быстро (< 3 секунд)
        self.assertLess(load_time, 3.0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
