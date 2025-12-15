import React, { useState } from 'react';
import { Card, Table, Button, Space, Typography, Modal, Form, Input, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface Warehouse {
  id: string;
  name: string;
  address: string;
  is_default: boolean;
}

const WarehousesSettings: React.FC = () => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([
    { id: '1', name: 'Основной склад', address: 'г. Москва, ул. Примерная, д. 1', is_default: true },
    { id: '2', name: 'Склад Санкт-Петербург', address: 'г. Санкт-Петербург, пр. Невский, д. 10', is_default: false },
  ]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState<Warehouse | null>(null);
  const [form] = Form.useForm();

  const handleCreate = () => {
    setEditingWarehouse(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Warehouse) => {
    setEditingWarehouse(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = (id: string) => {
    setWarehouses(warehouses.filter(w => w.id !== id));
    message.success('Склад удален');
  };

  const handleSave = async (values: any) => {
    if (editingWarehouse) {
      setWarehouses(warehouses.map(w => 
        w.id === editingWarehouse.id ? { ...w, ...values } : w
      ));
      message.success('Склад обновлен');
    } else {
      const newWarehouse: Warehouse = {
        id: Date.now().toString(),
        ...values,
        is_default: false,
      };
      setWarehouses([...warehouses, newWarehouse]);
      message.success('Склад создан');
    }
    setModalVisible(false);
    form.resetFields();
  };

  const columns: ColumnsType<Warehouse> = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record) => (
        <Space>
          <Text strong>{text}</Text>
          {record.is_default && <Text type="secondary">(по умолчанию)</Text>}
        </Space>
      ),
    },
    {
      title: 'Адрес',
      dataIndex: 'address',
      key: 'address',
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Изменить
          </Button>
          {!record.is_default && (
            <Popconfirm
              title="Удалить склад?"
              description="Это действие нельзя отменить"
              onConfirm={() => handleDelete(record.id)}
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
        <Title level={4} style={{ margin: 0 }}>Управление складами</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Добавить склад
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={warehouses}
        rowKey="id"
        pagination={false}
      />

      <Modal
        title={editingWarehouse ? 'Редактировать склад' : 'Добавить склад'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Сохранить"
        cancelText="Отмена"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            label="Название"
            name="name"
            rules={[{ required: true, message: 'Введите название склада' }]}
          >
            <Input placeholder="Название склада" />
          </Form.Item>

          <Form.Item
            label="Адрес"
            name="address"
            rules={[{ required: true, message: 'Введите адрес склада' }]}
          >
            <Input.TextArea rows={3} placeholder="Адрес склада" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default WarehousesSettings;
