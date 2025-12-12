import React from 'react';
import { Select, Space, Typography } from 'antd';
import type { Warehouse } from '@/types';

const { Text } = Typography;

interface WarehouseSelectorProps {
  warehouses: Warehouse[];
  selectedWarehouse?: string;
  onChange: (warehouseId: string) => void;
  showSummary?: boolean;
  loading?: boolean;
}

const WarehouseSelector: React.FC<WarehouseSelectorProps> = ({
  warehouses,
  selectedWarehouse,
  onChange,
  showSummary = false,
  loading = false,
}) => {
  const selected = warehouses.find(w => w.id === selectedWarehouse);

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Select
        value={selectedWarehouse}
        onChange={onChange}
        loading={loading}
        style={{ width: '300px' }}
        placeholder="Select Warehouse"
        options={warehouses.map(w => ({
          value: w.id,
          label: (
            <Space>
              <span>{w.name}</span>
              {w.is_primary && <Text type="secondary">(Primary)</Text>}
            </Space>
          ),
        }))}
      />
      {showSummary && selected && (
        <Space direction="vertical" size="small">
          <Text type="secondary">
            Type: {selected.warehouse_type === 'OWN' ? 'Own Warehouse' : 'Marketplace Fulfillment'}
          </Text>
          {selected.marketplace && (
            <Text type="secondary">Marketplace: {selected.marketplace}</Text>
          )}
        </Space>
      )}
    </Space>
  );
};

export default WarehouseSelector;
