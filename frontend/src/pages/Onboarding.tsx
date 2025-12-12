import React from 'react';
import { Card, Steps, Button, Typography } from 'antd';

const { Title } = Typography;

const Onboarding: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: '#f0f2f5',
      padding: '24px'
    }}>
      <Card style={{ maxWidth: '800px', width: '100%' }}>
        <Title level={2}>Welcome to ForecastMP!</Title>
        <p>Let's set up your account. This wizard will guide you through initial setup.</p>
        <Steps
          current={0}
          items={[
            { title: 'Company' },
            { title: 'Warehouse' },
            { title: 'Products' },
            { title: 'Integration' },
          ]}
        />
        <div style={{ marginTop: '24px' }}>
          <Button type="primary">Start Setup</Button>
        </div>
      </Card>
    </div>
  );
};

export default Onboarding;
