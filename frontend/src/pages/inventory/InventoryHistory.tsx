import React from 'react';
import { Table, Card, Tag, Typography, Space, DatePicker } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

interface MovementRecord {
  id: string;
  date: string;
  sku: string;
  product_name: string;
  warehouse: string;
  movement_type: string;
  quantity: number;
  reason: string;
  user: string;
}

const InventoryHistory: React.FC = () => {
  const mockData: MovementRecord[] = [
    {
      id: '1',
      date: '2024-12-15 14:30',
      sku: 'SKU-001',
      product_name: 'Товар A',
      warehouse: 'Основной склад',
      movement_type: 'adjustment_in',
      quantity: 50,
      reason: 'Инвентаризация',
      user: 'Иван Иванов',
    },
    {
      id: '2',
      date: '2024-12-15 10:15',
      sku: 'SKU-002',
      product_name: 'Товар B',
      warehouse: 'Склад Москва',
      movement_type: 'sale',
      quantity: -15,
      reason: 'Продажа',
      user: 'Система',
    },
    {
      id: '3',
      date: '2024-12-14 16:45',
      sku: 'SKU-003',
      product_name: 'Товар C',
      warehouse: 'Основной склад',
      movement_type: 'purchase',
      quantity: 100,
      reason: 'Закупка',
      user: 'Система',
    },
  ];

  const movementTypeLabels: Record<string, { label: string; color: string }> = {
    sale: { label: 'Продажа', color: 'red' },
    purchase: { label: 'Закупка', color: 'green' },
    adjustment_in: { label: 'Увеличение', color: 'blue' },
    adjustment_out: { label: 'Уменьшение', color: 'orange' },
    transfer_in: { label: 'Перемещение (вход)', color: 'cyan' },
    transfer_out: { label: 'Перемещение (выход)', color: 'purple' },
  };

  const columns: ColumnsType<MovementRecord> = [
    {
      title: 'Дата',
      dataIndex: 'date',
      key: 'date',
      width: 150,
      render: (text: string) => dayjs(text).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'Товар',
      key: 'product',
      width: 200,
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Text strong>{record.product_name}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.sku}</Text>
        </Space>
      ),
    },
    {
      title: 'Склад',
      dataIndex: 'warehouse',
      key: 'warehouse',
      width: 150,
    },
    {
      title: 'Тип операции',
      dataIndex: 'movement_type',
      key: 'movement_type',
      width: 150,
      render: (type: string) => {
        const config = movementTypeLabels[type] || { label: type, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: 'Количество',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      align: 'right',
      render: (value: number) => (
        <Text style={{ color: value > 0 ? '#52c41a' : '#f5222d' }} strong>
          {value > 0 ? `+${value}` : value}
        </Text>
      ),
    },
    {
      title: 'Причина',
      dataIndex: 'reason',
      key: 'reason',
      width: 150,
    },
    {
      title: 'Пользователь',
      dataIndex: 'user',
      key: 'user',
      width: 120,
    },
  ];

  return (
    <Card
      extra={
        <RangePicker
          format="DD.MM.YYYY"
          placeholder={['Начало', 'Конец']}
        />
      }
    >
      <Table
        columns={columns}
        dataSource={mockData}
        rowKey="id"
        pagination={{
          showTotal: (total) => `Всего ${total} записей`,
        }}
      />
    </Card>
  );
};

export default InventoryHistory;
