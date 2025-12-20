"""
UI Interface Tests for StockPredictor
Тесты интерфейса для проверки работы основных страниц и функций
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Company
from products.models import Product, MarketplaceProduct
from procurement.models import ProcurementRecommendation, PurchaseOrder, PurchaseOrderItem
from sales.models import DailySalesAggregate

User = get_user_model()


class DashboardUITests(TestCase):
    """Тесты интерфейса главной панели управления"""
    
    def setUp(self):
        """Подготовка тестовых данных перед каждым тестом"""
        # Создаем компанию
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем клиента для тестирования
        self.client = Client()
        
    def test_dashboard_page_requires_login(self):
        """Проверка что дашборд требует авторизации"""
        response = self.client.get(reverse('home'))
        # Должна быть переадресация на страницу логина
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())
        
    def test_dashboard_page_loads_for_authenticated_user(self):
        """Проверка что дашборд загружается для авторизованного пользователя"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        
    def test_dashboard_contains_required_elements(self):
        """Проверка наличия обязательных элементов на дашборде"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        
        # Проверяем наличие ключевых элементов
        self.assertContains(response, 'Дашборд')
        self.assertContains(response, 'Обзор текущей ситуации с запасами')
        
    def test_dashboard_metrics_api_endpoint(self):
        """Проверка API эндпоинта для метрик дашборда"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard:dashboard_metrics'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Проверяем структуру JSON ответа
        data = response.json()
        self.assertIn('success', data)


class ProcurementUITests(TestCase):
    """Тесты интерфейса модуля закупок"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем компанию
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем тестовые продукты
        self.product1 = Product.objects.create(
            company=self.company,
            sku="TEST-001",
            name="Тестовый товар 1",
            category="Electronics"
        )
        
        self.product2 = Product.objects.create(
            company=self.company,
            sku="TEST-002",
            name="Тестовый товар 2",
            category="Clothing"
        )
        
        # Создаем рекомендации по закупкам
        today = date.today()
        self.recommendation1 = ProcurementRecommendation.objects.create(
            product=self.product1,
            analysis_date=today,
            current_stock=10,
            runway_days=5,
            daily_burn_rate=Decimal('2.0'),
            recommended_quantity=50,
            action_category='ORDER_TODAY',
            priority_score=Decimal('95.0')
        )
        
        self.recommendation2 = ProcurementRecommendation.objects.create(
            product=self.product2,
            analysis_date=today,
            current_stock=100,
            runway_days=30,
            daily_burn_rate=Decimal('3.0'),
            recommended_quantity=0,
            action_category='NORMAL',
            priority_score=Decimal('10.0')
        )
        
        self.client = Client()
        
    def test_procurement_dashboard_loads(self):
        """Проверка загрузки главной страницы закупок"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'procurement/dashboard.html')
        
    def test_procurement_dashboard_shows_recommendations(self):
        """Проверка отображения рекомендаций на дашборде закупок"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:dashboard'))
        
        # Проверяем наличие товаров в ответе
        self.assertContains(response, 'TEST-001')
        self.assertContains(response, 'Тестовый товар 1')
        
    def test_buying_table_page_loads(self):
        """Проверка загрузки таблицы закупок"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'procurement/buying_table.html')
        
    def test_buying_table_shows_products(self):
        """Проверка отображения продуктов в таблице закупок"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'))
        
        # Проверяем наличие продуктов
        self.assertContains(response, 'TEST-001')
        self.assertContains(response, 'TEST-002')
        
    def test_buying_table_filter_by_category(self):
        """Проверка фильтрации по категориям"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'), {
            'category': 'Electronics'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-001')
        self.assertNotContains(response, 'TEST-002')
        
    def test_buying_table_filter_by_health_status(self):
        """Проверка фильтрации по статусу здоровья"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'), {
            'health_status': 'ORDER_TODAY'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-001')
        self.assertNotContains(response, 'TEST-002')
        
    def test_buying_table_search_by_sku(self):
        """Проверка поиска по SKU"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'), {
            'search': 'TEST-001'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-001')
        self.assertNotContains(response, 'TEST-002')
        
    def test_buying_table_search_by_name(self):
        """Проверка поиска по названию"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'), {
            'search': 'товар 1'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый товар 1')
        
    def test_export_buying_table(self):
        """Проверка экспорта таблицы закупок в CSV"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:export_buying_table'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Проверяем содержимое CSV
        content = response.content.decode('utf-8')
        self.assertIn('TEST-001', content)
        self.assertIn('Тестовый товар 1', content)
        
    def test_quick_order_creation(self):
        """Проверка быстрого создания заказа"""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('procurement:quick_order', kwargs={'product_id': self.product1.id})
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем что заказ создан
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('po_number', data)
        
        # Проверяем что заказ в БД
        po = PurchaseOrder.objects.filter(
            company=self.company,
            po_number=data['po_number']
        ).first()
        self.assertIsNotNone(po)
        self.assertEqual(po.items.count(), 1)
        
    def test_purchase_orders_page_loads(self):
        """Проверка загрузки страницы заказов на закупку"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:purchase_orders'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'procurement/purchase_orders.html')


class LoginUITests(TestCase):
    """Тесты интерфейса авторизации"""
    
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
        
        self.client = Client()
        
    def test_login_page_loads(self):
        """Проверка загрузки страницы логина"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        
    def test_login_with_valid_credentials(self):
        """Проверка входа с корректными данными"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Проверяем что произошла переадресация (302) или успешный вход (200)
        self.assertIn(response.status_code, [200, 302])
        
        # Если переадресация, проверяем URL
        if response.status_code == 302:
            self.assertEqual(response.url, reverse('home'))
        
    def test_login_with_invalid_credentials(self):
        """Проверка входа с неправильными данными"""
        response = self.client.post(reverse('accounts:login'), {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        })
        
        # Должна остаться на странице логина
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        
        # Проверяем наличие сообщения об ошибке
        self.assertContains(response, 'Invalid username or password')
        
    def test_logout_functionality(self):
        """Проверка функциональности выхода"""
        # Сначала авторизуемся
        self.client.force_login(self.user)
        
        # Проверяем что авторизованы
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Выходим
        response = self.client.get(reverse('accounts:logout'))
        
        # Должна быть переадресация
        self.assertEqual(response.status_code, 302)
        
    def test_authenticated_user_redirects_from_login(self):
        """Проверка что авторизованный пользователь переадресуется с логина"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:login'))
        
        # Должна быть переадресация на главную
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class PurchaseOrderUITests(TestCase):
    """Тесты интерфейса заказов на закупку"""
    
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
            sku="TEST-001",
            name="Тестовый товар"
        )
        
        # Создаем тестовый заказ
        self.po = PurchaseOrder.objects.create(
            company=self.company,
            po_number="PO-20231219-001",
            order_date=date.today(),
            status='DRAFT',
            supplier_name="Test Supplier"
        )
        
        PurchaseOrderItem.objects.create(
            purchase_order=self.po,
            product=self.product,
            quantity_ordered=100,
            unit_cost=Decimal('50.00')
        )
        
        self.client = Client()
        
    def test_purchase_order_detail_loads(self):
        """Проверка загрузки детальной страницы заказа"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('procurement:purchase_order_detail', kwargs={'po_id': self.po.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-20231219-001')
        self.assertContains(response, 'TEST-001')
        
    def test_update_order_status(self):
        """Проверка обновления статуса заказа"""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('procurement:update_order_status', kwargs={'po_id': self.po.id}),
            {'status': 'SUBMITTED'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем что статус обновлен
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, 'SUBMITTED')
        
    def test_purchase_orders_filter_by_status(self):
        """Проверка фильтрации заказов по статусу"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:purchase_orders'), {
            'status': 'DRAFT'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-20231219-001')
        
    def test_purchase_orders_filter_by_period(self):
        """Проверка фильтрации заказов по периоду"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:purchase_orders'), {
            'period': 'today'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-20231219-001')
        
    def test_purchase_orders_search(self):
        """Проверка поиска заказов"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:purchase_orders'), {
            'search': 'PO-20231219'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-20231219-001')


class HTMXIntegrationTests(TestCase):
    """Тесты HTMX интеграции в интерфейсе"""
    
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
            sku="TEST-001",
            name="Тестовый товар"
        )
        
        ProcurementRecommendation.objects.create(
            product=self.product,
            analysis_date=date.today(),
            current_stock=10,
            runway_days=5,
            daily_burn_rate=Decimal('2.0'),
            recommended_quantity=50,
            action_category='ORDER_TODAY',
            priority_score=Decimal('90.0')
        )
        
        self.client = Client()
        
    def test_htmx_request_returns_partial_template(self):
        """Проверка что HTMX запрос возвращает частичный шаблон"""
        self.client.force_login(self.user)
        
        # Отправляем HTMX запрос
        response = self.client.get(
            reverse('procurement:buying_table'),
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        # Должен быть использован частичный шаблон
        self.assertTemplateUsed(response, 'procurement/partials/buying_table_rows.html')
        
    def test_normal_request_returns_full_template(self):
        """Проверка что обычный запрос возвращает полный шаблон"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('procurement:buying_table'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'procurement/buying_table.html')


class ResponsiveUITests(TestCase):
    """Тесты отзывчивости интерфейса"""
    
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
        
        self.client = Client()
        
    def test_dashboard_contains_responsive_classes(self):
        """Проверка наличия классов адаптивности на дашборде"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        
        # Проверяем наличие Tailwind адаптивных классов
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'md:grid-cols-2')
        self.assertContains(response, 'lg:grid-cols-4')
        
    def test_buying_table_contains_responsive_classes(self):
        """Проверка наличия классов адаптивности в таблице закупок"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'))
        
        self.assertContains(response, 'overflow-x-auto')
        self.assertContains(response, 'grid')


class ErrorHandlingUITests(TestCase):
    """Тесты обработки ошибок в интерфейсе"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        import uuid
        
        self.company = Company.objects.create(
            name="Test Company"
        )
        
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.user.company = self.company
        self.user.save()
        
        # Создаем несуществующие UUID для тестов
        self.fake_product_id = uuid.uuid4()
        self.fake_po_id = uuid.uuid4()
        
        self.client = Client()
        
    def test_404_for_nonexistent_product(self):
        """Проверка 404 для несуществующего продукта"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('procurement:product_detail', kwargs={'product_id': self.fake_product_id})
        )
        
        self.assertEqual(response.status_code, 404)
        
    def test_404_for_nonexistent_purchase_order(self):
        """Проверка 404 для несуществующего заказа"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('procurement:purchase_order_detail', kwargs={'po_id': self.fake_po_id})
        )
        
        self.assertEqual(response.status_code, 404)
        
    def test_invalid_status_update(self):
        """Проверка обработки неправильного статуса"""
        po = PurchaseOrder.objects.create(
            company=self.company,
            po_number="PO-TEST-001",
            order_date=date.today(),
            status='DRAFT'
        )
        
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('procurement:update_order_status', kwargs={'po_id': po.id}),
            {'status': 'INVALID_STATUS'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)


class PaginationUITests(TestCase):
    """Тесты пагинации в интерфейсе"""
    
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
        
        # Создаем много продуктов для тестирования пагинации
        today = date.today()
        for i in range(60):
            product = Product.objects.create(
                company=self.company,
                sku=f"TEST-{i:03d}",
                name=f"Тестовый товар {i}"
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
        
    def test_buying_table_pagination_first_page(self):
        """Проверка первой страницы пагинации"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'))
        
        self.assertEqual(response.status_code, 200)
        # Должно быть максимум 50 элементов на странице
        self.assertContains(response, 'TEST-')
        
    def test_buying_table_pagination_second_page(self):
        """Проверка второй страницы пагинации"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:buying_table'), {'page': 2})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-')
        
    def test_purchase_orders_pagination(self):
        """Проверка пагинации заказов"""
        # Создаем много заказов
        for i in range(30):
            PurchaseOrder.objects.create(
                company=self.company,
                po_number=f"PO-TEST-{i:03d}",
                order_date=date.today(),
                status='DRAFT'
            )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('procurement:purchase_orders'))
        
        self.assertEqual(response.status_code, 200)
        # Должно быть максимум 25 элементов на странице
        self.assertContains(response, 'PO-TEST-')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
