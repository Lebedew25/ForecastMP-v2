import React, { useState } from 'react';
import { Card, Table, Button, Space, Typography, Modal, Form, Input, Select, Tag, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, MailOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface TeamMember {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'manager' | 'viewer';
  status: 'active' | 'pending';
}

const TeamSettings: React.FC = () => {
  const [members, setMembers] = useState<TeamMember[]>([
    { 
      id: '1', 
      email: 'admin@company.ru', 
      first_name: 'Иван', 
      last_name: 'Иванов', 
      role: 'admin',
      status: 'active'
    },
    { 
      id: '2', 
      email: 'manager@company.ru', 
      first_name: 'Петр', 
      last_name: 'Петров', 
      role: 'manager',
      status: 'active'
    },
  ]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const handleInvite = () => {
    form.resetFields();
    setModalVisible(true);
  };

  const handleSendInvite = async (values: any) => {
    const newMember: TeamMember = {
      id: Date.now().toString(),
      ...values,
      status: 'pending' as const,
      first_name: '',
      last_name: '',
    };
    setMembers([...members, newMember]);
    message.success('Приглашение отправлено');
    setModalVisible(false);
    form.resetFields();
  };

  const handleRemove = (id: string) => {
    setMembers(members.filter(m => m.id !== id));
    message.success('Пользователь удален');
  };

  const roleLabels: Record<string, string> = {
    admin: 'Администратор',
    manager: 'Менеджер',
    viewer: 'Наблюдатель',
  };

  const roleColors: Record<string, string> = {
    admin: 'red',
    manager: 'blue',
    viewer: 'default',
  };

  const columns: ColumnsType<TeamMember> = [
    {
      title: 'Имя',
      key: 'name',
      render: (_, record) => (
        <Space>
          {record.first_name || record.last_name ? (
            <Text strong>{record.first_name} {record.last_name}</Text>
          ) : (
            <Text type="secondary">Приглашение отправлено</Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={roleColors[role]}>{roleLabels[role]}</Tag>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'warning'}>
          {status === 'active' ? 'Активен' : 'Ожидает'}
        </Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Space>
          {record.role !== 'admin' && (
            <Popconfirm
              title="Удалить пользователя?"
              description="Это действие нельзя отменить"
              onConfirm={() => handleRemove(record.id)}
              okText="Да"
              cancelText="Нет"
            >
              <Button type="link" danger icon={<DeleteOutlined />}>
                Удалить
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <Title level={4} style={{ margin: 0 }}>Команда</Title>
        <Button type="primary" icon={<MailOutlined />} onClick={handleInvite}>
          Пригласить пользователя
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={members}
        rowKey="id"
        pagination={false}
      />

      <Modal
        title="Пригласить пользователя"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Отправить приглашение"
        cancelText="Отмена"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSendInvite}
        >
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Введите корректный email' }
            ]}
          >
            <Input placeholder="user@example.com" />
          </Form.Item>

          <Form.Item
            label="Роль"
            name="role"
            rules={[{ required: true, message: 'Выберите роль' }]}
          >
            <Select
              placeholder="Выберите роль"
              options={[
                { value: 'admin', label: 'Администратор - полный доступ' },
                { value: 'manager', label: 'Менеджер - управление товарами и заказами' },
                { value: 'viewer', label: 'Наблюдатель - только просмотр' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default TeamSettings;
