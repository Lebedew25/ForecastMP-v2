# ForecastMP Frontend

React + TypeScript frontend application for ForecastMP inventory management system.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Ant Design 5
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form
- **Date Manipulation**: Day.js

## Project Structure

```
src/
├── components/          # Reusable React components
│   ├── layout/         # Layout components (MainLayout, Sidebar, etc.)
│   └── shared/         # Shared UI components (StockBadge, DataTable, etc.)
├── pages/              # Page components for routes
│   ├── Dashboard.tsx
│   ├── Products.tsx
│   ├── Inventory.tsx
│   ├── Settings.tsx
│   ├── Onboarding.tsx
│   └── NoCompany.tsx
├── store/              # Redux store configuration
│   ├── slices/         # Redux slices
│   │   ├── authSlice.ts
│   │   ├── productsSlice.ts
│   │   └── uiSlice.ts
│   ├── index.ts        # Store configuration
│   └── hooks.ts        # Typed Redux hooks
├── services/           # API services
│   └── api.ts          # Axios API client
├── types/              # TypeScript type definitions
│   └── index.ts
├── utils/              # Utility functions
├── assets/             # Static assets
├── App.tsx             # Main App component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## Development

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The build output will be in `../static/frontend` directory, ready to be served by Django.

## Features

### Implemented

- ✅ Project structure and configuration
- ✅ Redux store with authentication, products, and UI slices
- ✅ API service layer with Axios
- ✅ Main layout with sidebar navigation
- ✅ Route guards based on company assignment
- ✅ Onboarding wizard placeholder
- ✅ No Company error page
- ✅ TypeScript type definitions for all Django models

### In Progress

- 🔨 Dashboard page with KPI widgets and charts
- 🔨 Products catalog page with filters
- 🔨 Inventory management pages
- 🔨 Settings pages
- 🔨 Shared components library

## API Integration

The frontend communicates with the Django backend via REST API at `/api/*` endpoints.

### Authentication

- Session-based authentication using Django sessions
- CSRF token handling via Axios interceptors
- Automatic redirect to login on 401 responses

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/me/` | GET | Get current user |
| `/api/dashboard/metrics/` | GET | Dashboard KPIs |
| `/api/products/` | GET | List products |
| `/api/inventory/adjust/` | POST | Adjust stock |
| `/api/warehouses/` | GET | List warehouses |

## Theme Customization

The application uses a custom Ant Design theme defined in `App.tsx`:

- Primary Color: #1890FF
- Success Color: #52C41A (adequate stock)
- Warning Color: #FA8C16 (low stock)
- Error Color: #F5222D (critical stock)
- Font: Inter

## Routing

| Route | Component | Auth Required | Company Required |
|-------|-----------|---------------|------------------|
| `/` | Dashboard | Yes | Yes |
| `/products` | Products | Yes | Yes |
| `/inventory` | Inventory | Yes | Yes |
| `/settings/*` | Settings | Yes | Yes |
| `/onboarding` | Onboarding | Yes | No (redirects if has company) |
| `/no-company` | NoCompany | Yes | No (redirects if has company) |

## State Management

Redux store structure:

- **auth**: User authentication state, company info
- **products**: Product catalog, filters, selected product
- **ui**: Sidebar state, notifications, loading states

## Development Workflow

1. Make changes to components/pages
2. Test in development mode (`npm run dev`)
3. Build for production (`npm run build`)
4. Django serves built files from `static/frontend`

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Notes

- The application assumes Django backend is running on `http://localhost:8000`
- Vite dev server proxies `/api` requests to Django backend
- Production build outputs to `../static/frontend` for Django static files
