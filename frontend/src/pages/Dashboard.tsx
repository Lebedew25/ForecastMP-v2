import React, { useEffect, useState } from 'react';
import { Row, Col, Typography, Spin, Table, Space, Card } from 'antd';
import { WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import KPICard from '@/components/shared/KPICard';
import StockBadge from '@/components/shared/StockBadge';
import MovementTypeIcon from '@/components/shared/MovementTypeIcon';
import type { DashboardMetrics, UrgentProduct, RecentActivity } from '@/types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [urgentProducts, setUrgentProducts] = useState<UrgentProduct[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // In production, these would be real API calls
      // For now, using mock data structure
      
      // Mock metrics
      setMetrics({
        total_inventory_value: 1245678.50,
        average_turnover: 23.5,
        low_stock_count: 15,
        dead_stock_count: 8,
        today_sales: 45230.20,
        weekly_sales: 312456.80,
      });

      // Mock urgent products
      setUrgentProducts([
        {
          product: {
            id: '1',
            company: 'comp1',
            sku: 'SKU-001',
            name: 'Product A',
            category: 'Electronics',
            description: '',
            is_active: true,
            created_at: '',
            updated_at: '',
          },
          issue_type: 'LOW_STOCK',
          current_stock: 5,
          days_remaining: 2,
        },
      ]);

      // Mock recent activities
      setRecentActivities([
        {
          id: '1',
          timestamp: new Date().toISOString(),
          operation_type: 'INBOUND',
          product_sku: 'SKU-001',
          product_name: 'Product A',
          quantity: 100,
          warehouse_name: 'Main Warehouse',
          user_name: 'Admin',
        },
      ]);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock chart data
  const inventoryTrendData = [
    { date: '1 Dec', inventory: 1200000, sales: 45000 },
    { date: '2 Dec', inventory: 1180000, sales: 52000 },
    { date: '3 Dec', inventory: 1220000, sales: 38000 },
    { date: '4 Dec', inventory: 1210000, sales: 48000 },
    { date: '5 Dec', inventory: 1245000, sales: 55000 },
  ];

  const productPerformanceData = [
    { name: 'Product A', sales: 450 },
    { name: 'Product B', sales: 380 },
    { name: 'Product C', sales: 320 },
    { name: 'Product D', sales: 280 },
    { name: 'Product E', sales: 210 },
  ];

  const urgentProductsColumns = [
    {
      title: 'Товар',
      dataIndex: ['product', 'name'],
      key: 'product',
      render: (_: any, record: UrgentProduct) => (
        <Space direction="vertical" size="small">
          <Text strong>{record.product.name}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.product.sku}</Text>
        </Space>
      ),
    },
    {
      title: 'Проблема',
      dataIndex: 'issue_type',
      key: 'issue',
      render: (type: string) => {
        const typeMap: Record<string, { icon: React.ReactNode; text: string; color: string }> = {
          NEGATIVE_STOCK: { icon: <WarningOutlined />, text: 'Перепродажа', color: '#F5222D' },
          LOW_STOCK: { icon: <WarningOutlined />, text: 'Низкий остаток', color: '#FA8C16' },
          NO_MOVEMENT: { icon: <CheckCircleOutlined />, text: 'Нет движения', color: '#8C8C8C' },
        };
        const config = typeMap[type] || typeMap.NO_MOVEMENT;
        return (
          <Space style={{ color: config.color }}>
            {config.icon}
            {config.text}
          </Space>
        );
      },
    },
    {
      title: 'Текущий остаток',
      dataIndex: 'current_stock',
      key: 'stock',
      align: 'right' as const,
    },
    {
      title: 'Прогноз',
      dataIndex: 'days_remaining',
      key: 'forecast',
      render: (days: number) => <StockBadge daysRemaining={days} />,
    },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>Главная панель</Title>
      
      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={8}>
          <KPICard
            title="Общая стоимость запасов"
            value={metrics?.total_inventory_value || 0}
            prefix="₽"
            precision={2}
            trend={{ value: 5.2, isPositive: true }}
          />
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <KPICard
            title="Средняя оборачиваемость"
            value={metrics?.average_turnover || 0}
            suffix="дней"
            precision={1}
            trend={{ value: 2.1, isPositive: false }}
          />
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <KPICard
            title="Низкий остаток"
            value={metrics?.low_stock_count || 0}
            trend={{ value: 15, isPositive: false }}
          />
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <KPICard
            title="Неликвидные товары"
            value={metrics?.dead_stock_count || 0}
          />
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <KPICard
            title="Продажи сегодня"
            value={metrics?.today_sales || 0}
            prefix="₽"
            precision={2}
            trend={{ value: 12.3, isPositive: true }}
          />
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <KPICard
            title="Продажи за неделю"
            value={metrics?.weekly_sales || 0}
            prefix="₽"
            precision={2}
            trend={{ value: 8.7, isPositive: true }}
          />
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={14}>
          <Card title="Динамика запасов и продаж (последние 5 дней)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={inventoryTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="inventory" stroke="#1890FF" name="Стоимость запасов (₽)" />
                <Line yAxisId="right" type="monotone" dataKey="sales" stroke="#52C41A" name="Ежедневные продажи (₽)" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="Топ-5 товаров по продажам">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={productPerformanceData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="sales" fill="#52C41A" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Tables */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Товары, требующие внимания">
            <Table
              columns={urgentProductsColumns}
              dataSource={urgentProducts}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Последняя активность">
            <Space direction="vertical" style={{ width: '100%' }}>
              {recentActivities.map(activity => (
                <div key={activity.id} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <Space>
                    <MovementTypeIcon type={activity.operation_type as any} />
                    <div>
                      <Text strong>{activity.product_sku}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {activity.operation_type} • {activity.quantity} units
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        {dayjs(activity.timestamp).fromNow()}
                      </Text>
                    </div>
                  </Space>
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
