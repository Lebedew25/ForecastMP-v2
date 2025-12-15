import React, { useState } from 'react';
import { Card, Typography, Space, Button, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined, CheckCircleOutlined, CloseCircleOutlined, SettingOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface Integration {
  id: string;
  name: string;
  type: string;
  status: 'connected' | 'disconnected';
  config?: any;
}

const IntegrationsSettings: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([
    { id: 'ozon', name: 'Ozon', type: 'marketplace', status: 'disconnected' },
    { id: 'wb', name: 'Wildberries', type: 'marketplace', status: 'disconnected' },
    { id: 'yandex', name: 'Яндекс.Маркет', type: 'marketplace', status: 'disconnected' },
  ]);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [form] = Form.useForm();

  const handleConnect = (integration: Integration) => {
    setSelectedIntegration(integration);
    form.resetFields();
    setModalVisible(true);
  };

  const handleDisconnect = (id: string) => {
    setIntegrations(integrations.map(int => 
      int.id === id ? { ...int, status: 'disconnected' as const } : int
    ));
    message.success('Интеграция отключена');
  };

  const handleSave = async (values: any) => {
    if (selectedIntegration) {
      setIntegrations(integrations.map(int => 
        int.id === selectedIntegration.id 
          ? { ...int, status: 'connected' as const, config: values } 
          : int
      ));
      message.success('Интеграция подключена');
    }
    setModalVisible(false);
    form.resetFields();
  };

  return (
    <Card>
      <Title level={4}>Интеграции с каналами продаж</Title>
      <Paragraph type="secondary">
        Подключите торговые площадки для автоматической синхронизации заказов и остатков
      </Paragraph>

      <Space direction="vertical" style={{ width: '100%', marginTop: '16px' }} size="large">
        {integrations.map((integration) => (
          <Card 
            key={integration.id}
            size="small"
            extra={
              <Space>
                {integration.status === 'connected' ? (
                  <>
                    <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    <Text type="success">Подключено</Text>
                    <Button 
                      icon={<SettingOutlined />}
                      onClick={() => handleConnect(integration)}
                    >
                      Настроить
                    </Button>
                    <Button 
                      danger
                      onClick={() => handleDisconnect(integration.id)}
                    >
                      Отключить
                    </Button>
                  </>
                ) : (
                  <>
                    <CloseCircleOutlined style={{ color: '#d9d9d9' }} />
                    <Text type="secondary">Не подключено</Text>
                    <Button 
                      type="primary"
                      onClick={() => handleConnect(integration)}
                    >
                      Подключить
                    </Button>
                  </>
                )}
              </Space>
            }
          >
            <Title level={5} style={{ margin: 0 }}>{integration.name}</Title>
          </Card>
        ))}
      </Space>

      <Modal
        title={`Настройка ${selectedIntegration?.name}`}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Сохранить"
        cancelText="Отмена"
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            label="Client ID"
            name="client_id"
            rules={[{ required: true, message: 'Введите Client ID' }]}
          >
            <Input placeholder="Client ID из личного кабинета" />
          </Form.Item>

          <Form.Item
            label="API Key"
            name="api_key"
            rules={[{ required: true, message: 'Введите API Key' }]}
          >
            <Input.Password placeholder="API Key из личного кабинета" />
          </Form.Item>

          <Form.Item
            label="Склад для синхронизации"
            name="warehouse_id"
            rules={[{ required: true, message: 'Выберите склад' }]}
          >
            <Select
              placeholder="Выберите склад"
              options={[
                { value: '1', label: 'Основной склад' },
                { value: '2', label: 'Склад Москва' },
                { value: '3', label: 'Склад СПб' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default IntegrationsSettings;
