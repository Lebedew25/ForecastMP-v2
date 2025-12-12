import React from 'react';
import { Card, Space, Typography, Button, Dropdown } from 'antd';
import { MoreOutlined } from '@ant-design/icons';
import type { Product } from '@/types';
import StockBadge from './StockBadge';
import type { MenuProps } from 'antd';

const { Text, Title } = Typography;

interface ProductCardProps {
  product: Product;
  currentStock?: number;
  forecastDays?: number;
  onClick?: () => void;
  onAction?: (action: string) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  currentStock = 0,
  forecastDays,
  onClick,
  onAction,
}) => {
  const menuItems: MenuProps['items'] = [
    { key: 'view', label: 'View Details' },
    { key: 'edit', label: 'Edit Product' },
    { key: 'adjust', label: 'Adjust Stock' },
    { key: 'transfer', label: 'Transfer' },
  ];

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    onAction?.(key);
  };

  return (
    <Card
      hoverable
      onClick={onClick}
      style={{ height: '100%' }}
      extra={
        <Dropdown menu={{ items: menuItems, onClick: handleMenuClick }} trigger={['click']}>
          <Button type="text" icon={<MoreOutlined />} onClick={(e) => e.stopPropagation()} />
        </Dropdown>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Text type="secondary" style={{ fontSize: '12px' }}>{product.sku}</Text>
            <Title level={5} style={{ margin: '4px 0' }}>{product.name}</Title>
          </div>
          <StockBadge daysRemaining={forecastDays} />
        </div>
        
        <Space split="|">
          <Text>Stock: <strong>{currentStock}</strong></Text>
          {product.attributes?.cost_price && (
            <Text>Cost: ₽{product.attributes.cost_price}</Text>
          )}
          {product.attributes?.selling_price && (
            <Text>Price: ₽{product.attributes.selling_price}</Text>
          )}
        </Space>
        
        {product.category && (
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Category: {product.category}
          </Text>
        )}
      </Space>
    </Card>
  );
};

export default ProductCard;
