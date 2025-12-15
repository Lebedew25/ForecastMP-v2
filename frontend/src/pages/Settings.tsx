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
      <Title level={4}>Информация о компании</Title>
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
          label="Название компании"
          name="company_name"
          rules={[{ required: true, message: 'Пожалуйста, введите название компании' }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="ИНН"
          name="tax_id"
          rules={[{ required: true, message: 'Пожалуйста, введите ИНН' }]}
        >
          <Input />
        </Form.Item>

        <Form.Item label="Основная валюта" name="currency">
          <Select
            options={[
              { value: 'RUB', label: 'Российский рубль (₽)' },
              { value: 'USD', label: 'Доллар США ($)' },
              { value: 'EUR', label: 'Евро (€)' },
            ]}
          />
        </Form.Item>

        <Form.Item label="Часовой пояс" name="timezone">
          <Select
            options={[
              { value: 'Europe/Moscow', label: 'Москва (UTC+3)' },
              { value: 'Europe/Samara', label: 'Самара (UTC+4)' },
              { value: 'Asia/Yekaterinburg', label: 'Екатеринбург (UTC+5)' },
            ]}
          />
        </Form.Item>

        <Divider />

        <Title level={5}>Правила управления запасами</Title>
        
        <Form.Item label="Автоматическое резервирование" name="auto_reserve" valuePropName="checked">
          <Switch />
          <Text type="secondary" style={{ marginLeft: '8px' }}>
            Резервировать товар при создании заказа
          </Text>
        </Form.Item>

        <Form.Item label="Порог нехватки товара (дни)" name="stockout_threshold">
          <Input type="number" placeholder="7" style={{ width: '200px' }} />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
            Сохранить изменения
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );

  const warehousesTab = (
    <Card>
      <Title level={4}>Управление складами</Title>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Text>Здесь будет отображен интерфейс управления складами.</Text>
        <Button type="primary">Добавить новый склад</Button>
      </Space>
    </Card>
  );

  const integrationsTab = (
    <Card>
      <Title level={4}>Интеграции с каналами продаж</Title>
      <Space direction="vertical" style={{ width: '100%', marginTop: '16px' }} size="large">
        <Card size="small" title="Ozon" extra={<Button>Подключить</Button>}>
          <Text type="secondary">Не подключено</Text>
        </Card>
        <Card size="small" title="Wildberries" extra={<Button>Подключить</Button>}>
          <Text type="secondary">Не подключено</Text>
        </Card>
        <Card size="small" title="Свой сайт" extra={<Button>Настроить</Button>}>
          <Text type="secondary">Не настроено</Text>
        </Card>
      </Space>
    </Card>
  );

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Настройки</Title>
      <Tabs
        defaultActiveKey="company"
        items={[
          {
            key: 'company',
            label: 'Профиль компании',
            children: companyTab,
          },
          {
            key: 'warehouses',
            label: 'Склады',
            children: warehousesTab,
          },
          {
            key: 'integrations',
            label: 'Интеграции',
            children: integrationsTab,
          },
          {
            key: 'team',
            label: 'Команда',
            children: <Card><Text>Здесь будет отображено управление командой.</Text></Card>,
          },
          {
            key: 'notifications',
            label: 'Уведомления',
            children: <Card><Text>Здесь будут отображены настройки уведомлений.</Text></Card>,
          },
        ]}
      />
    </div>
  );
};

export default Settings;
