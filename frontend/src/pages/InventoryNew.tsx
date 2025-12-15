import React from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Typography, Menu } from 'antd';
import InventoryOverview from './inventory/InventoryOverview';
import InventoryByWarehouse from './inventory/InventoryByWarehouse';
import InventoryAdjust from './inventory/InventoryAdjust';
import InventoryHistory from './inventory/InventoryHistory';

const { Title } = Typography;

const Inventory: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/inventory',
      label: 'Общий обзор',
    },
    {
      key: '/inventory/warehouse',
      label: 'По складам',
    },
    {
      key: '/inventory/adjust',
      label: 'Корректировка остатков',
    },
    {
      key: '/inventory/history',
      label: 'История движений',
    },
  ];

  const selectedKey = location.pathname === '/inventory' 
    ? '/inventory' 
    : location.pathname;

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Управление складом</Title>
      
      <Menu
        mode="horizontal"
        selectedKeys={[selectedKey]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ marginBottom: '24px' }}
      />

      <Routes>
        <Route index element={<InventoryOverview />} />
        <Route path="warehouse" element={<InventoryByWarehouse />} />
        <Route path="adjust" element={<InventoryAdjust />} />
        <Route path="history" element={<InventoryHistory />} />
      </Routes>
    </div>
  );
};

export default Inventory;
