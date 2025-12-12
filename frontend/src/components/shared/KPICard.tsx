import React from 'react';
import { Card, Statistic, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

interface KPICardProps {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: string;
  precision?: number;
  trend?: {
    value: number;
    isPositive?: boolean;
  };
  loading?: boolean;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  prefix,
  suffix,
  precision = 0,
  trend,
  loading = false,
}) => {
  return (
    <Card loading={loading}>
      <Statistic
        title={title}
        value={value}
        precision={precision}
        prefix={prefix}
        suffix={suffix}
      />
      {trend && (
        <Space style={{ marginTop: '8px' }}>
          {trend.isPositive !== false ? (
            <ArrowUpOutlined style={{ color: '#52C41A' }} />
          ) : (
            <ArrowDownOutlined style={{ color: '#F5222D' }} />
          )}
          <span style={{ color: trend.isPositive !== false ? '#52C41A' : '#F5222D' }}>
            {Math.abs(trend.value)}%
          </span>
        </Space>
      )}
    </Card>
  );
};

export default KPICard;
