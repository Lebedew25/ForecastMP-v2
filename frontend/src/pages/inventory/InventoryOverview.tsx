import React from 'react';
import { Table, Button, Space, Typography, Card, Statistic, Row, Col } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import StockBadge from '@/components/shared/StockBadge';

const { Text } = Typography;

interface InventoryItem {
  id: string;
  sku: string;
  name: string;
  category: string;
  available: number;
  reserved: number;
  expected: number;
  forecast_days: number;
}

const InventoryOverview: React.FC = () => {
  const mockInventory: InventoryItem[] = [
    { id: '1', sku: 'SKU-001', name: 'Товар A', category: 'Электроника', available: 150, reserved: 30, expected: 100, forecast_days: 25 },
    { id: '2', sku: 'SKU-002', name: 'Товар B', category: 'Одежда', available: 45, reserved: 15, expected: 0, forecast_days: 5 },
    { id: '3', sku: 'SKU-003', name: 'Товар C', category: 'Продукты', available: 220, reserved: 50, expected: 150, forecast_days: 45 },
  ];

  const columns: ColumnsType<InventoryItem> = [
    {
      title: 'Товар',
      key: 'product',
      width: 250,
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Text strong>{record.name}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.sku}</Text>
        </Space>
      ),
    },
    {
      title: 'Категория',
      dataIndex: 'category',
      key: 'category',
      width: 150,
    },
    {
      title: 'Доступно',
      dataIndex: 'available',
      key: 'available',
      width: 100,
      align: 'right',
      render: (value: number) => <Text strong>{value}</Text>,
    },
    {
      title: 'Зарезервировано',
      dataIndex: 'reserved',
      key: 'reserved',
      width: 120,
      align: 'right',
    },
    {
      title: 'Ожидается',
      dataIndex: 'expected',
      key: 'expected',
      width: 100,
      align: 'right',
    },
    {
      title: 'Прогноз',
      key: 'forecast',
      width: 140,
      render: (_, record) => <StockBadge daysRemaining={record.forecast_days} />,
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic title="Всего товаров" value={mockInventory.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Доступно" value={mockInventory.reduce((sum, item) => sum + item.available, 0)} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Зарезервировано" value={mockInventory.reduce((sum, item) => sum + item.reserved, 0)} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Ожидается" value={mockInventory.reduce((sum, item) => sum + item.expected, 0)} />
          </Card>
        </Col>
      </Row>

      <Card
        extra={<Button icon={<DownloadOutlined />}>Экспорт</Button>}
      >
        <Table
          columns={columns}
          dataSource={mockInventory}
          rowKey="id"
          pagination={{
            showTotal: (total) => `Всего ${total} позиций`,
          }}
        />
      </Card>
    </Space>
  );
};

export default InventoryOverview;
