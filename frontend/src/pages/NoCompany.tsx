import React from 'react';
import { Card, Button, Space, Result } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';

const NoCompany: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAppSelector(state => state.auth);

  const isSuperuser = user?.is_superuser || false;

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: '#f0f2f5',
      padding: '24px'
    }}>
      <Card style={{ maxWidth: '600px', width: '100%', textAlign: 'center' }}>
        <Result
          icon={<InfoCircleOutlined style={{ color: '#1890FF' }} />}
          title="No Company Assigned"
          subTitle="Your account is not currently associated with a company. Please contact your administrator to grant access, or create a new company to get started."
        />
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          {isSuperuser && (
            <Button
              type="primary"
              size="large"
              onClick={() => navigate('/onboarding')}
            >
              Create New Company
            </Button>
          )}
          <Button size="large">Contact Support</Button>
          <Button type="link" onClick={() => window.location.href = '/admin/logout'}>
            Logout
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default NoCompany;
