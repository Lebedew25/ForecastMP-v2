import React from 'react';
import { Tabs, Card, Form, Input, Select, Button, Switch, Typography, Space, Divider } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const Settings: React.FC = () => {
  const [form] = Form.useForm();

  const handleSave = (values: any) => {
    console.log('Saving settings:', values);
  };

  const companyTab = (
    <Card>
      <Title level={4}>Company Information</Title>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          company_name: 'My Company',
          tax_id: '1234567890',
          currency: 'RUB',
          timezone: 'Europe/Moscow',
        }}
      >
        <Form.Item
          label="Company Name"
          name="company_name"
          rules={[{ required: true, message: 'Please enter company name' }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="Tax ID (INN)"
          name="tax_id"
          rules={[{ required: true, message: 'Please enter tax ID' }]}
        >
          <Input />
        </Form.Item>

        <Form.Item label="Primary Currency" name="currency">
          <Select
            options={[
              { value: 'RUB', label: 'Russian Ruble (₽)' },
              { value: 'USD', label: 'US Dollar ($)' },
              { value: 'EUR', label: 'Euro (€)' },
            ]}
          />
        </Form.Item>

        <Form.Item label="Time Zone" name="timezone">
          <Select
            options={[
              { value: 'Europe/Moscow', label: 'Moscow (UTC+3)' },
              { value: 'Europe/Samara', label: 'Samara (UTC+4)' },
              { value: 'Asia/Yekaterinburg', label: 'Yekaterinburg (UTC+5)' },
            ]}
          />
        </Form.Item>

        <Divider />

        <Title level={5}>Inventory Management Rules</Title>
        
        <Form.Item label="Automatic Reservation" name="auto_reserve" valuePropName="checked">
          <Switch />
          <Text type="secondary" style={{ marginLeft: '8px' }}>
            Reserve stock when order is created
          </Text>
        </Form.Item>

        <Form.Item label="Stockout Threshold (days)" name="stockout_threshold">
          <Input type="number" placeholder="7" style={{ width: '200px' }} />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
            Save Changes
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );

  const warehousesTab = (
    <Card>
      <Title level={4}>Warehouse Management</Title>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Text>Warehouse management interface will be displayed here.</Text>
        <Button type="primary">Add New Warehouse</Button>
      </Space>
    </Card>
  );

  const integrationsTab = (
    <Card>
      <Title level={4}>Sales Channel Integrations</Title>
      <Space direction="vertical" style={{ width: '100%', marginTop: '16px' }} size="large">
        <Card size="small" title="Ozon" extra={<Button>Connect</Button>}>
          <Text type="secondary">Not connected</Text>
        </Card>
        <Card size="small" title="Wildberries" extra={<Button>Connect</Button>}>
          <Text type="secondary">Not connected</Text>
        </Card>
        <Card size="small" title="Custom Website" extra={<Button>Configure</Button>}>
          <Text type="secondary">Not configured</Text>
        </Card>
      </Space>
    </Card>
  );

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Settings</Title>
      <Tabs
        defaultActiveKey="company"
        items={[
          {
            key: 'company',
            label: 'Company Profile',
            children: companyTab,
          },
          {
            key: 'warehouses',
            label: 'Warehouses',
            children: warehousesTab,
          },
          {
            key: 'integrations',
            label: 'Integrations',
            children: integrationsTab,
          },
          {
            key: 'team',
            label: 'Team',
            children: <Card><Text>Team management will be displayed here.</Text></Card>,
          },
          {
            key: 'notifications',
            label: 'Notifications',
            children: <Card><Text>Notification settings will be displayed here.</Text></Card>,
          },
        ]}
      />
    </div>
  );
};

export default Settings;
