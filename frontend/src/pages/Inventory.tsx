import React, { useState } from 'react';
import { Table, Button, Space, Typography, Card, Statistic, Row, Col } from 'antd';
import { DownloadOutlined, ToolOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import StockBadge from '@/components/shared/StockBadge';
import WarehouseSelector from '@/components/shared/WarehouseSelector';

const { Title, Text } = Typography;

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

const Inventory: React.FC = () => {
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('all');

  // Mock data
  const mockWarehouses = [
    { id: 'all', name: 'Все склады', warehouse_type: 'OWN' as const, company: '', is_primary: true, is_active: true, created_at: '', metadata: {} },
    { id: '1', name: 'Основной склад', warehouse_type: 'OWN' as const, company: '', is_primary: true, is_active: true, created_at: '', metadata: {} },
    { id: '2', name: 'Ozon FF', warehouse_type: 'MARKETPLACE_FF' as const, marketplace: 'OZON' as const, company: '', is_primary: false, is_active: true, created_at: '', metadata: {} },
  ];

  const mockInventory: InventoryItem[] = [
    {
      id: '1',
      sku: 'SKU-001',
      name: 'Товар A',
      category: 'Электроника',
      available: 150,
      reserved: 30,
      expected: 100,
      forecast_days: 25,
    },
    {
      id: '2',
      sku: 'SKU-002',
      name: 'Товар B',
      category: 'Одежда',
      available: 45,
      reserved: 15,
      expected: 0,
      forecast_days: 5,
    },
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
      width: 100,
      align: 'right',
    },
    {
      title: 'Ожидается',
      dataIndex: 'expected',
      key: 'expected',
      width: 100,
      align: 'right',
      render: (value: number) => value > 0 ? <Text type="success">+{value}</Text> : <Text type="secondary">—</Text>,
    },
    {
      title: 'Всего',
      key: 'total',
      width: 100,
      align: 'right',
      render: (_, record) => <Text strong>{record.available + record.reserved}</Text>,
    },
    {
      title: 'Прогноз',
      dataIndex: 'forecast_days',
      key: 'forecast',
      width: 140,
      render: (days: number) => <StockBadge daysRemaining={days} />,
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 120,
      render: () => (
        <Space>
          <Button type="link" size="small">Корректировать</Button>
          <Button type="link" size="small">Переместить</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>Обзор склада</Title>
        <Space>
          <Button icon={<DownloadOutlined />}>Экспорт</Button>
          <Button type="primary" icon={<ToolOutlined />}>Корректировка остатков</Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Всего товаров" value={mockInventory.length} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Общий остаток" value={mockInventory.reduce((sum, item) => sum + item.available, 0)} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Зарезервировано" value={mockInventory.reduce((sum, item) => sum + item.reserved, 0)} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Ожидается поставка" value={mockInventory.reduce((sum, item) => sum + item.expected, 0)} />
          </Card>
        </Col>
      </Row>

      {/* Warehouse Selector */}
      <div style={{ marginBottom: '16px' }}>
        <WarehouseSelector
          warehouses={mockWarehouses}
          selectedWarehouse={selectedWarehouse}
          onChange={setSelectedWarehouse}
          showSummary
        />
      </div>

      {/* Inventory Table */}
      <Table
        columns={columns}
        dataSource={mockInventory}
        rowKey="id"
        scroll={{ x: 1000 }}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `Всего ${total} позиций`,
        }}
      />
    </div>
  );
};

export default Inventory;
