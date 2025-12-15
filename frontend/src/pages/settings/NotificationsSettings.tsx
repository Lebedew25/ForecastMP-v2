import React from 'react';
import { Card, Form, Switch, Typography, Space, Divider, Select, Button } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

const NotificationsSettings: React.FC = () => {
  const [form] = Form.useForm();

  const handleSave = (values: any) => {
    console.log('Saving notification settings:', values);
  };

  return (
    <Card>
      <Title level={4}>Настройки уведомлений</Title>
      <Paragraph type="secondary">
        Настройте, какие уведомления вы хотите получать и каким способом
      </Paragraph>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          email_enabled: true,
          telegram_enabled: false,
          low_stock_alert: true,
          new_order: true,
          forecast_alert: true,
          daily_report: false,
          notification_time: '09:00',
        }}
      >
        <Divider>Каналы уведомлений</Divider>

        <Form.Item 
          label="Email уведомления" 
          name="email_enabled" 
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item 
          label="Telegram уведомления" 
          name="telegram_enabled" 
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Divider>Типы уведомлений</Divider>

        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Form.Item 
            label="Низкий остаток товара" 
            name="low_stock_alert" 
            valuePropName="checked"
          >
            <Space>
              <Switch />
              <Text type="secondary">Уведомлять когда товар заканчивается</Text>
            </Space>
          </Form.Item>

          <Form.Item 
            label="Новые заказы" 
            name="new_order" 
            valuePropName="checked"
          >
            <Space>
              <Switch />
              <Text type="secondary">Уведомлять о новых заказах</Text>
            </Space>
          </Form.Item>

          <Form.Item 
            label="Прогноз истощения запасов" 
            name="forecast_alert" 
            valuePropName="checked"
          >
            <Space>
              <Switch />
              <Text type="secondary">Предупреждать о возможной нехватке товара</Text>
            </Space>
          </Form.Item>

          <Form.Item 
            label="Ежедневный отчет" 
            name="daily_report" 
            valuePropName="checked"
          >
            <Space>
              <Switch />
              <Text type="secondary">Получать сводку по продажам и остаткам</Text>
            </Space>
          </Form.Item>
        </Space>

        <Divider>Расписание</Divider>

        <Form.Item 
          label="Время отправки ежедневных отчетов" 
          name="notification_time"
        >
          <Select
            style={{ width: 200 }}
            options={[
              { value: '08:00', label: '08:00' },
              { value: '09:00', label: '09:00' },
              { value: '10:00', label: '10:00' },
              { value: '18:00', label: '18:00' },
            ]}
          />
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

export default NotificationsSettings;
