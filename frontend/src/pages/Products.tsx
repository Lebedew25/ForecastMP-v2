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
      title: 'Product Name',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      ellipsis: true,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 150,
      render: (category: string) => category || <Text type="secondary">—</Text>,
    },
    {
      title: 'Total Stock',
      key: 'total_stock',
      width: 120,
      align: 'right',
      render: () => Math.floor(Math.random() * 500), // Mock data
    },
    {
      title: 'My Warehouse',
      key: 'my_stock',
      width: 120,
      align: 'right',
      render: () => Math.floor(Math.random() * 200), // Mock data
    },
    {
      title: 'Forecast Depletion',
      key: 'forecast',
      width: 140,
      render: () => {
        const days = Math.floor(Math.random() * 60);
        return <StockBadge daysRemaining={days} />;
      },
    },
    {
      title: 'Cost Price',
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
      title: 'Selling Price',
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
      title: 'Status',
      dataIndex: 'is_active',
      key: 'status',
      width: 100,
      render: (active: boolean) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>Products</Title>
        <Space>
          <Button icon={<DownloadOutlined />}>Export</Button>
          <Button type="primary" icon={<PlusOutlined />}>Import Products</Button>
        </Space>
      </div>

      {/* Filters */}
      <Space style={{ marginBottom: '16px', width: '100%' }} wrap>
        <Search
          placeholder="Search by SKU or name"
          onSearch={handleSearch}
          style={{ width: 300 }}
          enterButton={<SearchOutlined />}
        />
        <Select
          placeholder="Stock Status"
          style={{ width: 150 }}
          onChange={handleStockFilter}
          allowClear
          options={[
            { value: 'all', label: 'All Products' },
            { value: 'low_stock', label: 'Low Stock' },
            { value: 'out_of_stock', label: 'Out of Stock' },
            { value: 'no_movement', label: 'No Movement' },
          ]}
        />
        <Select
          placeholder="Category"
          style={{ width: 150 }}
          allowClear
          options={[
            { value: 'electronics', label: 'Electronics' },
            { value: 'clothing', label: 'Clothing' },
            { value: 'food', label: 'Food' },
          ]}
        />
        <Button icon={<FilterOutlined />}>More Filters</Button>
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
          showTotal: (total) => `Total ${total} products`,
        }}
      />

      {/* Product Detail Modal */}
      <Modal
        title="Product Details"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            Close
          </Button>,
          <Button key="edit" type="primary">
            Edit Product
          </Button>,
        ]}
      >
        {selectedProduct && (
          <Tabs
            items={[
              {
                key: 'overview',
                label: 'Overview',
                children: (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>SKU:</Text> <Text>{selectedProduct.sku}</Text>
                    </div>
                    <div>
                      <Text strong>Name:</Text> <Text>{selectedProduct.name}</Text>
                    </div>
                    <div>
                      <Text strong>Category:</Text> <Text>{selectedProduct.category || '—'}</Text>
                    </div>
                    <div>
                      <Text strong>Description:</Text> <Text>{selectedProduct.description || '—'}</Text>
                    </div>
                    <div>
                      <Text strong>Cost Price:</Text> <Text>₽{selectedProduct.attributes?.cost_price || 0}</Text>
                    </div>
                    <div>
                      <Text strong>Selling Price:</Text> <Text>₽{selectedProduct.attributes?.selling_price || 0}</Text>
                    </div>
                    <div>
                      <Text strong>Status:</Text>{' '}
                      <Tag color={selectedProduct.is_active ? 'success' : 'default'}>
                        {selectedProduct.is_active ? 'Active' : 'Inactive'}
                      </Tag>
                    </div>
                  </Space>
                ),
              },
              {
                key: 'sales',
                label: 'Sales History',
                children: <div>Sales history chart will be displayed here</div>,
              },
              {
                key: 'movement',
                label: 'Stock Movement',
                children: <div>Stock movement history will be displayed here</div>,
              },
              {
                key: 'forecast',
                label: 'Forecast & Orders',
                children: <div>Forecast data and purchase orders will be displayed here</div>,
              },
            ]}
          />
        )}
      </Modal>
    </div>
  );
};

export default Products;
