import React from 'react';
import { Card, Form, Input, Select, Button, Switch, Typography, Space, Divider } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const CompanySettings: React.FC = () => {
  const [form] = Form.useForm();

  const handleSave = (values: any) => {
    console.log('Saving company settings:', values);
  };

  return (
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
};

export default CompanySettings;
