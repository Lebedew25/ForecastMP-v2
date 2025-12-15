import React from 'react';
import { Card, Form, Select, InputNumber, Input, Button, message, Space, Typography } from 'antd';

const { Title } = Typography;

const InventoryAdjust: React.FC = () => {
  const [form] = Form.useForm();

  const handleAdjust = (values: any) => {
    console.log('Adjusting inventory:', values);
    message.success('Остатки скорректированы');
    form.resetFields();
  };

  return (
    <Card>
      <Title level={4}>Корректировка остатков</Title>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleAdjust}
        style={{ maxWidth: 600 }}
      >
        <Form.Item
          label="Товар"
          name="product_id"
          rules={[{ required: true, message: 'Выберите товар' }]}
        >
          <Select
            showSearch
            placeholder="Поиск товара по SKU или названию"
            options={[
              { value: '1', label: 'SKU-001 - Товар A' },
              { value: '2', label: 'SKU-002 - Товар B' },
              { value: '3', label: 'SKU-003 - Товар C' },
            ]}
          />
        </Form.Item>

        <Form.Item
          label="Склад"
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

        <Form.Item
          label="Тип операции"
          name="movement_type"
          rules={[{ required: true, message: 'Выберите тип операции' }]}
        >
          <Select
            placeholder="Выберите тип"
            options={[
              { value: 'adjustment_in', label: 'Увеличение остатка' },
              { value: 'adjustment_out', label: 'Уменьшение остатка' },
              { value: 'correction', label: 'Корректировка (установить точное значение)' },
            ]}
          />
        </Form.Item>

        <Form.Item
          label="Количество"
          name="quantity"
          rules={[{ required: true, message: 'Введите количество' }]}
        >
          <InputNumber min={1} style={{ width: '100%' }} placeholder="Количество единиц" />
        </Form.Item>

        <Form.Item
          label="Причина"
          name="reason"
          rules={[{ required: true, message: 'Укажите причину' }]}
        >
          <Select
            placeholder="Выберите причину"
            options={[
              { value: 'inventory_check', label: 'Инвентаризация' },
              { value: 'damage', label: 'Повреждение/Брак' },
              { value: 'lost', label: 'Потеря' },
              { value: 'found', label: 'Излишки' },
              { value: 'other', label: 'Другое' },
            ]}
          />
        </Form.Item>

        <Form.Item
          label="Примечание"
          name="notes"
        >
          <Input.TextArea rows={3} placeholder="Дополнительная информация (необязательно)" />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              Применить корректировку
            </Button>
            <Button onClick={() => form.resetFields()}>
              Очистить
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default InventoryAdjust;
