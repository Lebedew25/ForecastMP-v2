import React, { useEffect, useState } from 'react';
import { Table, Input, Select, Button, Space, Tag, Typography, Modal, Tabs } from 'antd';
import { SearchOutlined, FilterOutlined, DownloadOutlined, PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Product } from '@/types';
import StockBadge from '@/components/shared/StockBadge';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchProducts, setFilters } from '@/store/slices/productsSlice';

const { Title, Text } = Typography;
const { Search } = Input;

const Products: React.FC = () => {
  const dispatch = useAppDispatch();
  const { products, loading, filters } = useAppSelector(state => state.products);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  useEffect(() => {
    dispatch(fetchProducts(filters));
  }, [dispatch, filters]);

  const handleSearch = (value: string) => {
    dispatch(setFilters({ ...filters, search: value }));
  };

  const handleStockFilter = (value: string) => {
    dispatch(setFilters({ ...filters, stock_status: value as any }));
  };

  const handleRowClick = (record: Product) => {
    setSelectedProduct(record);
    setDetailModalVisible(true);
  };

  const columns: ColumnsType<Product> = [
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      width: 120,
      fixed: 'left',
      render: (sku: string) => <Text strong>{sku}</Text>,
    },
    {
      title: 'Название товара',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      ellipsis: true,
    },
    {
      title: 'Категория',
      dataIndex: 'category',
      key: 'category',
      width: 150,
      render: (category: string) => category || <Text type="secondary">—</Text>,
    },
    {
      title: 'Всего на складе',
      key: 'total_stock',
      width: 120,
      align: 'right',
      render: () => Math.floor(Math.random() * 500), // Mock data
    },
    {
      title: 'Мой склад',
      key: 'my_stock',
      width: 120,
      align: 'right',
      render: () => Math.floor(Math.random() * 200), // Mock data
    },
    {
      title: 'Прогноз истощения',
      key: 'forecast',
      width: 140,
      render: () => {
        const days = Math.floor(Math.random() * 60);
        return <StockBadge daysRemaining={days} />;
      },
    },
    {
      title: 'Себестоимость',
      key: 'cost_price',
      width: 120,
      align: 'right',
      render: (_, record) => (
        record.attributes?.cost_price 
          ? `₽${record.attributes.cost_price.toFixed(2)}`
          : <Text type="secondary">—</Text>
      ),
    },
    {
      title: 'Цена продажи',
      key: 'selling_price',
      width: 120,
      align: 'right',
      render: (_, record) => (
        record.attributes?.selling_price
          ? `₽${record.attributes.selling_price.toFixed(2)}`
          : <Text type="secondary">—</Text>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'status',
      width: 100,
      render: (active: boolean) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? 'Активен' : 'Неактивен'}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>Товары</Title>
        <Space>
          <Button icon={<DownloadOutlined />}>Экспорт</Button>
          <Button type="primary" icon={<PlusOutlined />}>Импорт товаров</Button>
        </Space>
      </div>

      {/* Filters */}
      <Space style={{ marginBottom: '16px', width: '100%' }} wrap>
        <Search
          placeholder="Поиск по SKU или названию"
          onSearch={handleSearch}
          style={{ width: 300 }}
          enterButton={<SearchOutlined />}
        />
        <Select
          placeholder="Статус остатков"
          style={{ width: 150 }}
          onChange={handleStockFilter}
          allowClear
          options={[
            { value: 'all', label: 'Все товары' },
            { value: 'low_stock', label: 'Низкий остаток' },
            { value: 'out_of_stock', label: 'Нет на складе' },
            { value: 'no_movement', label: 'Нет движения' },
          ]}
        />
        <Select
          placeholder="Категория"
          style={{ width: 150 }}
          allowClear
          options={[
            { value: 'electronics', label: 'Электроника' },
            { value: 'clothing', label: 'Одежда' },
            { value: 'food', label: 'Продукты' },
          ]}
        />
        <Button icon={<FilterOutlined />}>Больше фильтров</Button>
      </Space>

      {/* Products Table */}
      <Table
        columns={columns}
        dataSource={products}
        loading={loading}
        rowKey="id"
        scroll={{ x: 1200 }}
        onRow={(record) => ({
          onClick: () => handleRowClick(record),
          style: { cursor: 'pointer' },
        })}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `Всего ${total} товаров`,
        }}
      />

      {/* Product Detail Modal */}
      <Modal
        title="Подробности товара"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            Закрыть
          </Button>,
          <Button key="edit" type="primary">
            Редактировать
          </Button>,
        ]}
      >
        {selectedProduct && (
          <Tabs
            items={[
              {
                key: 'overview',
                label: 'Общий обзор',
                children: (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>SKU:</Text> <Text>{selectedProduct.sku}</Text>
                    </div>
                    <div>
                      <Text strong>Название:</Text> <Text>{selectedProduct.name}</Text>
                    </div>
                    <div>
                      <Text strong>Категория:</Text> <Text>{selectedProduct.category || '—'}</Text>
                    </div>
                    <div>
                      <Text strong>Описание:</Text> <Text>{selectedProduct.description || '—'}</Text>
                    </div>
                    <div>
                      <Text strong>Себестоимость:</Text> <Text>₽{selectedProduct.attributes?.cost_price || 0}</Text>
                    </div>
                    <div>
                      <Text strong>Цена продажи:</Text> <Text>₽{selectedProduct.attributes?.selling_price || 0}</Text>
                    </div>
                    <div>
                      <Text strong>Статус:</Text>{' '}
                      <Tag color={selectedProduct.is_active ? 'success' : 'default'}>
                        {selectedProduct.is_active ? 'Активен' : 'Неактивен'}
                      </Tag>
                    </div>
                  </Space>
                ),
              },
              {
                key: 'sales',
                label: 'История продаж',
                children: <div>Здесь будет отображен график продаж</div>,
              },
              {
                key: 'movement',
                label: 'Движение товара',
                children: <div>Здесь будет отображена история движения товара</div>,
              },
              {
                key: 'forecast',
                label: 'Прогноз и заказы',
                children: <div>Здесь будут отображены прогнозы и заказы на пополнение</div>,
              },
            ]}
          />
        )}
      </Modal>
    </div>
  );
};

export default Products;
