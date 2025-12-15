import React from 'react';
import { Layout, Menu, Avatar, Dropdown } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  ShoppingOutlined,
  DatabaseOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { toggleSidebar } from '@/store/slices/uiSlice';
import { logout } from '@/store/slices/authSlice';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { sidebarCollapsed } = useAppSelector(state => state.ui);
  const { user } = useAppSelector(state => state.auth);

  const menuItems: MenuProps['items'] = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Главная',
      onClick: () => navigate('/'),
    },
    {
      key: '/products',
      icon: <ShoppingOutlined />,
      label: 'Товары',
      children: [
        {
          key: '/products/all',
          label: 'Все товары',
          onClick: () => navigate('/products'),
        },
        {
          key: '/products/categories',
          label: 'Категории',
          onClick: () => navigate('/products/categories'),
        },
        {
          key: '/products/import',
          label: 'Импорт/Экспорт',
          onClick: () => navigate('/settings/import'),
        },
      ],
    },
    {
      key: '/inventory',
      icon: <DatabaseOutlined />,
      label: 'Склад',
      children: [
        {
          key: '/inventory/overview',
          label: 'Общий обзор',
          onClick: () => navigate('/inventory'),
        },
        {
          key: '/inventory/warehouse',
          label: 'По складам',
          onClick: () => navigate('/inventory/warehouse'),
        },
        {
          key: '/inventory/adjust',
          label: 'Корректировка остатков',
          onClick: () => navigate('/inventory/adjust'),
        },
        {
          key: '/inventory/history',
          label: 'История движений',
          onClick: () => navigate('/inventory/history'),
        },
      ],
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Настройки',
      children: [
        {
          key: '/settings/company',
          label: 'Профиль компании',
          onClick: () => navigate('/settings/company'),
        },
        {
          key: '/settings/warehouses',
          label: 'Склады',
          onClick: () => navigate('/settings/warehouses'),
        },
        {
          key: '/settings/integrations',
          label: 'Каналы продаж',
          onClick: () => navigate('/settings/integrations'),
        },
      ],
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Профиль',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Выйти',
      onClick: () => dispatch(logout()),
    },
  ];

  // Get selected keys from current location
  const selectedKeys = [location.pathname];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={sidebarCollapsed}
        onCollapse={() => dispatch(toggleSidebar())}
        width={250}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: sidebarCollapsed ? '16px' : '20px',
          fontWeight: 'bold',
          padding: '0 16px'
        }}>
          {sidebarCollapsed ? 'FM' : 'ForecastMP'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          items={menuItems}
        />
      </Sider>
      <Layout style={{ marginLeft: sidebarCollapsed ? 80 : 250, transition: 'margin-left 0.2s' }}>
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,21,41,.08)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {React.createElement(sidebarCollapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              style: { fontSize: '18px', cursor: 'pointer' },
              onClick: () => dispatch(toggleSidebar()),
            })}
            <h2 style={{ margin: 0 }}>{user?.company?.name || 'ForecastMP'}</h2>
          </div>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.first_name || user?.email}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{
          margin: '24px 16px',
          padding: 24,
          minHeight: 280,
          background: '#fff',
          borderRadius: '8px'
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
