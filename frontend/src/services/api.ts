import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  ApiResponse,
  PaginatedResponse,
  Product,
  Warehouse,
  InventoryMovement,
  DashboardMetrics,
  UrgentProduct,
  RecentActivity,
  User,
  Company
} from '@/types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // For Django session authentication
    });

    // Request interceptor for CSRF token
    this.client.interceptors.request.use(
      (config) => {
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // For 401 errors, don't redirect automatically
        // Let the component handle it (will show login prompt or redirect)
        return Promise.reject(error);
      }
    );
  }

  private getCsrfToken(): string | null {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) {
        return decodeURIComponent(value);
      }
    }
    return null;
  }

  // Authentication
  async login(username: string, password: string): Promise<void> {
    await this.client.post('/auth/login/', { username, password });
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me/');
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout/');
  }

  // Dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await this.client.get<ApiResponse<DashboardMetrics>>('/dashboard/metrics/');
    return response.data.data!;
  }

  async getUrgentProducts(limit: number = 15): Promise<UrgentProduct[]> {
    const response = await this.client.get<ApiResponse<UrgentProduct[]>>('/dashboard/urgent-products/', {
      params: { limit }
    });
    return response.data.data!;
  }

  async getRecentActivities(limit: number = 10): Promise<RecentActivity[]> {
    const response = await this.client.get<ApiResponse<RecentActivity[]>>('/dashboard/recent-activities/', {
      params: { limit }
    });
    return response.data.data!;
  }

  // Products
  async getProducts(params?: any): Promise<PaginatedResponse<Product>> {
    const response = await this.client.get('/products/', { params });
    const data = response.data;
    
    // Handle both Django response format and standard paginated format
    if (data.success && data.products) {
      return {
        count: data.total_count || 0,
        next: null,
        previous: null,
        results: data.products.map((p: any) => ({
          id: p.id,
          sku: p.sku,
          name: p.name,
          description: p.description,
          category: p.category,
          is_active: true,
          attributes: {
            cost_price: p.cost,
            selling_price: p.price,
          },
        })),
      };
    }
    
    return response.data;
  }

  async getProduct(id: string): Promise<Product> {
    const response = await this.client.get<Product>(`/products/${id}/`);
    return response.data;
  }

  async createProduct(data: Partial<Product>): Promise<Product> {
    const response = await this.client.post<Product>('/products/', data);
    return response.data;
  }

  async updateProduct(id: string, data: Partial<Product>): Promise<Product> {
    const response = await this.client.patch<Product>(`/products/${id}/`, data);
    return response.data;
  }

  async deleteProduct(id: string): Promise<void> {
    await this.client.delete(`/products/${id}/`);
  }

  // Warehouses
  async getWarehouses(): Promise<Warehouse[]> {
    const response = await this.client.get<Warehouse[]>('/warehouses/');
    return response.data;
  }

  async getWarehouse(id: string): Promise<Warehouse> {
    const response = await this.client.get<Warehouse>(`/warehouses/${id}/`);
    return response.data;
  }

  async createWarehouse(data: Partial<Warehouse>): Promise<Warehouse> {
    const response = await this.client.post<Warehouse>('/warehouses/', data);
    return response.data;
  }

  async updateWarehouse(id: string, data: Partial<Warehouse>): Promise<Warehouse> {
    const response = await this.client.patch<Warehouse>(`/warehouses/${id}/`, data);
    return response.data;
  }

  async deleteWarehouse(id: string): Promise<void> {
    await this.client.delete(`/warehouses/${id}/`);
  }

  // Inventory
  async adjustInventory(data: {
    product_id: string;
    warehouse_id: string;
    quantity: number;
    movement_type: string;
    reason: string;
    notes?: string;
  }): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/inventory/adjust/', data);
    return response.data;
  }

  async getInventoryMovements(params?: any): Promise<PaginatedResponse<InventoryMovement>> {
    const response = await this.client.get<PaginatedResponse<InventoryMovement>>('/inventory/movements/', { params });
    return response.data;
  }

  async transferInventory(data: {
    product_id: string;
    source_warehouse_id: string;
    destination_warehouse_id: string;
    quantity: number;
    notes?: string;
  }): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/inventory/transfer/', data);
    return response.data;
  }

  // Import
  async importProducts(file: File, options: {
    create_new: boolean;
    update_existing: boolean;
    match_by: 'sku' | 'name' | 'both';
    import_stock: boolean;
    target_warehouse?: string;
  }): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await this.client.post<ApiResponse>('/import/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Company
  async updateCompany(id: string, data: Partial<Company>): Promise<Company> {
    const response = await this.client.patch<Company>(`/companies/${id}/`, data);
    return response.data;
  }

  // Integrations
  async syncMarketplace(marketplace: string): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/integrations/sync/', { marketplace });
    return response.data;
  }
}

export default new ApiService();
