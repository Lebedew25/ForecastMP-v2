import React, { useState } from 'react';
import { Card, Select, Table, Typography, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface WarehouseInventory {
  id: string;
  sku: string;
  name: string;
  available: number;
  reserved: number;
}

const InventoryByWarehouse: React.FC = () => {
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('1');

  const warehouses = [
    { value: '1', label: 'Основной склад' },
    { value: '2', label: 'Склад Москва' },
    { value: '3', label: 'Склад СПб' },
  ];

  const mockData: WarehouseInventory[] = [
    { id: '1', sku: 'SKU-001', name: 'Товар A', available: 150, reserved: 30 },
    { id: '2', sku: 'SKU-002', name: 'Товар B', available: 45, reserved: 15 },
    { id: '3', sku: 'SKU-003', name: 'Товар C', available: 220, reserved: 50 },
  ];

  const columns: ColumnsType<WarehouseInventory> = [
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      width: 120,
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Доступно',
      dataIndex: 'available',
      key: 'available',
      align: 'right',
      render: (value: number) => <Text strong>{value}</Text>,
    },
    {
      title: 'Зарезервировано',
      dataIndex: 'reserved',
      key: 'reserved',
      align: 'right',
    },
    {
      title: 'Всего',
      key: 'total',
      align: 'right',
      render: (_, record) => <Text>{record.available + record.reserved}</Text>,
    },
  ];

  return (
    <Card>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={4}>Выберите склад</Title>
          <Select
            style={{ width: 300 }}
            value={selectedWarehouse}
            onChange={setSelectedWarehouse}
            options={warehouses}
          />
        </div>

        <Table
          columns={columns}
          dataSource={mockData}
          rowKey="id"
          pagination={{
            showTotal: (total) => `Всего ${total} позиций`,
          }}
        />
      </Space>
    </Card>
  );
};

export default InventoryByWarehouse;
