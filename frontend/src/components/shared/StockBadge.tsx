import React from 'react';
import { Tag } from 'antd';
import type { StockStatus } from '@/types';

interface StockBadgeProps {
  daysRemaining?: number;
  status?: StockStatus;
  size?: 'small' | 'default' | 'large';
}

const StockBadge: React.FC<StockBadgeProps> = ({ daysRemaining, status, size = 'default' }) => {
  // Determine status from days if not provided
  let badgeStatus: StockStatus = status || 'NO_DATA';
  if (daysRemaining !== undefined) {
    if (daysRemaining > 30) badgeStatus = 'ADEQUATE';
    else if (daysRemaining >= 7) badgeStatus = 'WARNING';
    else badgeStatus = 'CRITICAL';
  }

  // Color mapping
  const colorMap: Record<StockStatus, string> = {
    ADEQUATE: 'success',  // Green
    WARNING: 'warning',   // Orange
    CRITICAL: 'error',    // Red
    NO_DATA: 'default',   // Gray
  };

  // Text mapping
  const getLabel = (): string => {
    if (daysRemaining !== undefined) {
      if (daysRemaining === 0) return 'Нет на складе';
      if (daysRemaining === 1) return '1 день';
      if (daysRemaining < 5) return `${daysRemaining} дня`;
      return `${daysRemaining} дней`;
    }
    
    switch (badgeStatus) {
      case 'ADEQUATE': return '> 30 дней';
      case 'WARNING': return '7-30 дней';
      case 'CRITICAL': return '< 7 дней';
      default: return 'Нет данных';
    }
  };

  return (
    <Tag color={colorMap[badgeStatus]} style={{ fontSize: size === 'small' ? '11px' : '12px' }}>
      {getLabel()}
    </Tag>
  );
};

export default StockBadge;
