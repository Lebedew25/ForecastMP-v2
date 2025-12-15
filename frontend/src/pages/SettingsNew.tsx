import React from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Typography, Menu } from 'antd';
import CompanySettings from './settings/CompanySettings';
import WarehousesSettings from './settings/WarehousesSettings';
import IntegrationsSettings from './settings/IntegrationsSettings';
import TeamSettings from './settings/TeamSettings';
import NotificationsSettings from './settings/NotificationsSettings';

const { Title } = Typography;

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/settings/company',
      label: 'Профиль компании',
    },
    {
      key: '/settings/warehouses',
      label: 'Склады',
    },
    {
      key: '/settings/integrations',
      label: 'Интеграции',
    },
    {
      key: '/settings/team',
      label: 'Команда',
    },
    {
      key: '/settings/notifications',
      label: 'Уведомления',
    },
  ];

  const selectedKey = location.pathname.startsWith('/settings') 
    ? location.pathname 
    : '/settings/company';

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Настройки</Title>
      
      <div style={{ display: 'flex', gap: '24px' }}>
        <Menu
          mode="vertical"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ width: 200, borderRadius: '8px' }}
        />

        <div style={{ flex: 1 }}>
          <Routes>
            <Route index element={<CompanySettings />} />
            <Route path="company" element={<CompanySettings />} />
            <Route path="warehouses" element={<WarehousesSettings />} />
            <Route path="integrations" element={<IntegrationsSettings />} />
            <Route path="team" element={<TeamSettings />} />
            <Route path="notifications" element={<NotificationsSettings />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default Settings;
