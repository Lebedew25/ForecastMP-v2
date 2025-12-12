import React from 'react';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  SwapOutlined,
  EditOutlined,
  SyncOutlined,
  PlusCircleOutlined,
} from '@ant-design/icons';

interface MovementTypeIconProps {
  type: 'INBOUND' | 'OUTBOUND' | 'TRANSFER' | 'ADJUSTMENT' | 'SYNC_UPDATE' | 'INITIAL_LOAD';
  size?: number;
}

const MovementTypeIcon: React.FC<MovementTypeIconProps> = ({ type, size = 16 }) => {
  const iconProps = { style: { fontSize: size } };

  switch (type) {
    case 'INBOUND':
      return <ArrowDownOutlined {...iconProps} style={{ ...iconProps.style, color: '#52C41A' }} />;
    case 'OUTBOUND':
      return <ArrowUpOutlined {...iconProps} style={{ ...iconProps.style, color: '#1890FF' }} />;
    case 'TRANSFER':
      return <SwapOutlined {...iconProps} style={{ ...iconProps.style, color: '#722ED1' }} />;
    case 'ADJUSTMENT':
      return <EditOutlined {...iconProps} style={{ ...iconProps.style, color: '#FA8C16' }} />;
    case 'SYNC_UPDATE':
      return <SyncOutlined {...iconProps} style={{ ...iconProps.style, color: '#8C8C8C' }} />;
    case 'INITIAL_LOAD':
      return <PlusCircleOutlined {...iconProps} style={{ ...iconProps.style, color: '#13C2C2' }} />;
    default:
      return null;
  }
};

export default MovementTypeIcon;
