import React, { useState } from 'react';
import { Table, Button, Space, Typography, Modal, Form, Input, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface Category {
  id: string;
  name: string;
  description?: string;
  product_count: number;
}

const Categories: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([
    { id: '1', name: 'Электроника', description: 'Электронные товары', product_count: 42 },
    { id: '2', name: 'Одежда', description: 'Одежда и аксессуары', product_count: 128 },
    { id: '3', name: 'Продукты', description: 'Продукты питания', product_count: 87 },
  ]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [form] = Form.useForm();

  const handleCreate = () => {
    setEditingCategory(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Category) => {
    setEditingCategory(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = (id: string) => {
    setCategories(categories.filter(cat => cat.id !== id));
    message.success('Категория удалена');
  };

  const handleSave = async (values: any) => {
    if (editingCategory) {
      // Update existing
      setCategories(categories.map(cat => 
        cat.id === editingCategory.id ? { ...cat, ...values } : cat
      ));
      message.success('Категория обновлена');
    } else {
      // Create new
      const newCategory: Category = {
        id: Date.now().toString(),
        ...values,
        product_count: 0,
      };
      setCategories([...categories, newCategory]);
      message.success('Категория создана');
    }
    setModalVisible(false);
    form.resetFields();
  };

  const columns: ColumnsType<Category> = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Описание',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || <Text type="secondary">—</Text>,
    },
    {
      title: 'Количество товаров',
      dataIndex: 'product_count',
      key: 'product_count',
      align: 'right',
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
          <Popconfirm
            title="Удалить категорию?"
            description="Это действие нельзя отменить"
            onConfirm={() => handleDelete(record.id)}
            okText="Да"
            cancelText="Нет"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Удалить
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>Категории товаров</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Создать категорию
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={categories}
        rowKey="id"
        pagination={{
          showTotal: (total) => `Всего ${total} категорий`,
        }}
      />

      <Modal
        title={editingCategory ? 'Редактировать категорию' : 'Создать категорию'}
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
            rules={[{ required: true, message: 'Введите название категории' }]}
          >
            <Input placeholder="Название категории" />
          </Form.Item>

          <Form.Item
            label="Описание"
            name="description"
          >
            <Input.TextArea rows={3} placeholder="Описание категории (необязательно)" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Categories;
