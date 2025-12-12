// Core entity types based on Django models

export interface Company {
  id: string;
  name: string;
  tax_id: string;
  logo?: string;
  currency: string;
  timezone: string;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company: Company | null;
  is_superuser: boolean;
}

export interface Product {
  id: string;
  company: string;
  sku: string;
  name: string;
  category: string;
  description: string;
  is_active: boolean;
  attributes?: ProductAttributes;
  created_at: string;
  updated_at: string;
}

export interface ProductAttributes {
  cost_price?: number;
  selling_price?: number;
  brand?: string;
  weight?: number;
  reorder_threshold_days: number;
  lead_time_days: number;
  safety_stock_days: number;
  minimum_order_quantity: number;
}

export interface Warehouse {
  id: string;
  company: string;
  name: string;
  warehouse_type: 'OWN' | 'MARKETPLACE_FF';
  marketplace?: 'WILDBERRIES' | 'OZON' | 'WEBSITE';
  is_primary: boolean;
  is_active: boolean;
  metadata: Record<string, any>;
  created_at: string;
}

export interface InventorySnapshot {
  id: string;
  product: string;
  warehouse: string;
  snapshot_date: string;
  quantity_available: number;
  quantity_reserved: number;
}

export interface InventoryMovement {
  id: string;
  product: Product;
  warehouse: Warehouse;
  movement_type: 'INBOUND' | 'OUTBOUND' | 'TRANSFER' | 'ADJUSTMENT' | 'SYNC_UPDATE' | 'INITIAL_LOAD';
  quantity: number;
  movement_date: string;
  reference_type?: string;
  reference_id?: string;
  notes: string;
  created_by?: string;
}

export interface SalesTransaction {
  id: string;
  product: string;
  marketplace: 'WILDBERRIES' | 'OZON' | 'WEBSITE';
  sale_date: string;
  quantity: number;
  revenue: number;
}

export interface ForecastResult {
  id: string;
  product: string;
  forecast_date: string;
  predicted_quantity: number;
  confidence_lower: number;
  confidence_upper: number;
  created_at: string;
}

export interface ProcurementRecommendation {
  id: string;
  product: Product;
  status: 'ORDER_TODAY' | 'ALREADY_ORDERED' | 'ATTENTION_REQUIRED' | 'NORMAL';
  current_stock: number;
  daily_burn_rate: number;
  runway_days: number;
  recommended_quantity: number;
  stockout_date?: string;
  created_at: string;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  field_errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Dashboard types
export interface DashboardMetrics {
  total_inventory_value: number;
  average_turnover: number;
  low_stock_count: number;
  dead_stock_count: number;
  today_sales: number;
  weekly_sales: number;
}

export interface UrgentProduct {
  product: Product;
  issue_type: 'NEGATIVE_STOCK' | 'LOW_STOCK' | 'NO_MOVEMENT';
  current_stock: number;
  forecast_depletion_date?: string;
  days_remaining?: number;
}

export interface RecentActivity {
  id: string;
  timestamp: string;
  operation_type: string;
  product_sku: string;
  product_name: string;
  quantity: number;
  warehouse_name: string;
  user_name?: string;
}

// Stock badge types
export type StockStatus = 'ADEQUATE' | 'WARNING' | 'CRITICAL' | 'NO_DATA';

export interface StockBadgeData {
  days_remaining?: number;
  status: StockStatus;
}

// Filter types
export interface ProductFilters {
  search?: string;
  category?: string;
  stock_status?: 'all' | 'low_stock' | 'out_of_stock' | 'no_movement';
  warehouse?: string;
}

export interface MovementFilters {
  date_start?: string;
  date_end?: string;
  movement_type?: string[];
  warehouse?: string[];
  product?: string;
  category?: string;
  user?: string[];
  min_quantity?: number;
}
