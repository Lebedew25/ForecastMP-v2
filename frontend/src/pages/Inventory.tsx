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
    { id: 'all', name: 'All Warehouses', warehouse_type: 'OWN' as const, company: '', is_primary: true, is_active: true, created_at: '', metadata: {} },
    { id: '1', name: 'Main Warehouse', warehouse_type: 'OWN' as const, company: '', is_primary: true, is_active: true, created_at: '', metadata: {} },
    { id: '2', name: 'Ozon FF', warehouse_type: 'MARKETPLACE_FF' as const, marketplace: 'OZON' as const, company: '', is_primary: false, is_active: true, created_at: '', metadata: {} },
  ];

  const mockInventory: InventoryItem[] = [
    {
      id: '1',
      sku: 'SKU-001',
      name: 'Product A',
      category: 'Electronics',
      available: 150,
      reserved: 30,
      expected: 100,
      forecast_days: 25,
    },
    {
      id: '2',
      sku: 'SKU-002',
      name: 'Product B',
      category: 'Clothing',
      available: 45,
      reserved: 15,
      expected: 0,
      forecast_days: 5,
    },
  ];

  const columns: ColumnsType<InventoryItem> = [
    {
      title: 'Product',
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
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 150,
    },
    {
      title: 'Available',
      dataIndex: 'available',
      key: 'available',
      width: 100,
      align: 'right',
      render: (value: number) => <Text strong>{value}</Text>,
    },
    {
      title: 'Reserved',
      dataIndex: 'reserved',
      key: 'reserved',
      width: 100,
      align: 'right',
    },
    {
      title: 'Expected',
      dataIndex: 'expected',
      key: 'expected',
      width: 100,
      align: 'right',
      render: (value: number) => value > 0 ? <Text type="success">+{value}</Text> : <Text type="secondary">—</Text>,
    },
    {
      title: 'Total',
      key: 'total',
      width: 100,
      align: 'right',
      render: (_, record) => <Text strong>{record.available + record.reserved}</Text>,
    },
    {
      title: 'Forecast',
      dataIndex: 'forecast_days',
      key: 'forecast',
      width: 140,
      render: (days: number) => <StockBadge daysRemaining={days} />,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: () => (
        <Space>
          <Button type="link" size="small">Adjust</Button>
          <Button type="link" size="small">Transfer</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>Inventory Overview</Title>
        <Space>
          <Button icon={<DownloadOutlined />}>Export</Button>
          <Button type="primary" icon={<ToolOutlined />}>Stock Adjustment</Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Total SKUs" value={mockInventory.length} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Total Stock" value={mockInventory.reduce((sum, item) => sum + item.available, 0)} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Reserved" value={mockInventory.reduce((sum, item) => sum + item.reserved, 0)} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Expected Inbound" value={mockInventory.reduce((sum, item) => sum + item.expected, 0)} />
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
          showTotal: (total) => `Total ${total} items`,
        }}
      />
    </div>
  );
};

export default Inventory;
