import React, { useState } from 'react';
import { Card, Upload, Button, Typography, Space, Radio, Checkbox, Select, Divider, message, Progress, Table } from 'antd';
import { UploadOutlined, DownloadOutlined, InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;

const ImportExport: React.FC = () => {
  const [importMode, setImportMode] = useState<'new' | 'update' | 'both'>('both');
  const [matchBy, setMatchBy] = useState<'sku' | 'name' | 'both'>('sku');
  const [importStock, setImportStock] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls,.csv',
    beforeUpload: (file) => {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        || file.type === 'application/vnd.ms-excel'
        || file.type === 'text/csv';
      
      if (!isExcel) {
        message.error('Можно загружать только файлы Excel или CSV!');
        return false;
      }

      const isLt5M = file.size / 1024 / 1024 < 5;
      if (!isLt5M) {
        message.error('Размер файла не должен превышать 5MB!');
        return false;
      }

      return false; // Prevent auto upload
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      setUploading(true);
      setUploadProgress(0);

      // Simulate upload
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setUploading(false);
            message.success('Файл успешно загружен и обработан');
            onSuccess?.(null);
            return 100;
          }
          return prev + 10;
        });
      }, 300);
    },
  };

  const downloadTemplate = () => {
    message.info('Скачивание шаблона...');
    // Implement template download
  };

  const exportProducts = () => {
    message.info('Экспорт товаров...');
    // Implement product export
  };

  const recentImports = [
    { id: '1', filename: 'products_2024_01.xlsx', date: '2024-12-15 14:30', status: 'success', imported: 245 },
    { id: '2', filename: 'inventory_update.csv', date: '2024-12-14 10:15', status: 'success', imported: 128 },
    { id: '3', filename: 'new_products.xlsx', date: '2024-12-13 16:45', status: 'partial', imported: 89 },
  ];

  const importColumns = [
    {
      title: 'Файл',
      dataIndex: 'filename',
      key: 'filename',
    },
    {
      title: 'Дата',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: 'Импортировано',
      dataIndex: 'imported',
      key: 'imported',
      render: (count: number) => <Text>{count} товаров</Text>,
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { text: string; color: string }> = {
          success: { text: 'Успешно', color: '#52c41a' },
          partial: { text: 'Частично', color: '#faad14' },
          error: { text: 'Ошибка', color: '#f5222d' },
        };
        return <Text style={{ color: statusMap[status]?.color }}>{statusMap[status]?.text}</Text>;
      },
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Импорт и экспорт товаров</Title>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Import Section */}
        <Card title="Импорт товаров">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Paragraph>
                Загрузите файл Excel или CSV с данными о товарах. Можно импортировать новые товары, 
                обновить существующие или сделать и то, и другое.
              </Paragraph>
              <Button icon={<DownloadOutlined />} onClick={downloadTemplate}>
                Скачать шаблон файла
              </Button>
            </div>

            <Divider />

            <div>
              <Title level={5}>Настройки импорта</Title>
              
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text strong>Режим импорта:</Text>
                  <Radio.Group 
                    value={importMode} 
                    onChange={(e) => setImportMode(e.target.value)}
                    style={{ marginTop: 8 }}
                  >
                    <Space direction="vertical">
                      <Radio value="new">Только новые товары</Radio>
                      <Radio value="update">Только обновление существующих</Radio>
                      <Radio value="both">Создавать новые и обновлять существующие</Radio>
                    </Space>
                  </Radio.Group>
                </div>

                <div>
                  <Text strong>Идентификация товаров:</Text>
                  <Radio.Group 
                    value={matchBy} 
                    onChange={(e) => setMatchBy(e.target.value)}
                    style={{ marginTop: 8 }}
                  >
                    <Space direction="vertical">
                      <Radio value="sku">По артикулу (SKU)</Radio>
                      <Radio value="name">По названию</Radio>
                      <Radio value="both">По артикулу или названию</Radio>
                    </Space>
                  </Radio.Group>
                </div>

                <Checkbox 
                  checked={importStock} 
                  onChange={(e) => setImportStock(e.target.checked)}
                >
                  Импортировать остатки товаров
                </Checkbox>

                {importStock && (
                  <div style={{ marginLeft: 24 }}>
                    <Text>Целевой склад:</Text>
                    <Select
                      placeholder="Выберите склад"
                      style={{ width: '100%', marginTop: 8 }}
                      value={selectedWarehouse}
                      onChange={setSelectedWarehouse}
                      options={[
                        { value: 'warehouse1', label: 'Основной склад' },
                        { value: 'warehouse2', label: 'Склад Москва' },
                        { value: 'warehouse3', label: 'Склад СПб' },
                      ]}
                    />
                  </div>
                )}
              </Space>
            </div>

            <Divider />

            <Dragger {...uploadProps} style={{ marginTop: 16 }}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">Нажмите или перетащите файл для загрузки</p>
              <p className="ant-upload-hint">
                Поддерживаются форматы: Excel (.xlsx, .xls) и CSV (.csv)
              </p>
            </Dragger>

            {uploading && (
              <Progress percent={uploadProgress} status="active" />
            )}
          </Space>
        </Card>

        {/* Export Section */}
        <Card title="Экспорт товаров">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Paragraph>
              Экспортируйте данные о товарах в файл Excel для редактирования или анализа.
            </Paragraph>
            <Button 
              type="primary" 
              icon={<DownloadOutlined />} 
              onClick={exportProducts}
            >
              Экспортировать все товары
            </Button>
          </Space>
        </Card>

        {/* Recent Imports */}
        <Card title="История импорта">
          <Table
            columns={importColumns}
            dataSource={recentImports}
            rowKey="id"
            pagination={false}
          />
        </Card>
      </Space>
    </div>
  );
};

export default ImportExport;
