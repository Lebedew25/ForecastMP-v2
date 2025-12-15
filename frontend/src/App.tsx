import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import { Provider } from 'react-redux';
import { store } from './store';
import { useAppDispatch, useAppSelector } from './store/hooks';
import { fetchCurrentUser } from './store/slices/authSlice';
import ErrorBoundary from './components/shared/ErrorBoundary';
import { useNotifications } from './utils/notifications';
import dayjs from 'dayjs';
import 'dayjs/locale/ru';

dayjs.locale('ru');

// Layouts
import MainLayout from './components/layout/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import Settings from './pages/Settings';
import Onboarding from './pages/Onboarding';
import NoCompany from './pages/NoCompany';
import Login from './pages/Login';

// Theme configuration
const theme = {
  token: {
    colorPrimary: '#1890FF',
    colorSuccess: '#52C41A',
    colorWarning: '#FA8C16',
    colorError: '#F5222D',
    colorInfo: '#1890FF',
    colorBgBase: '#FFFFFF',
    colorBgContainer: '#F5F5F5',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
};

function AppRoutes() {
  const dispatch = useAppDispatch();
  const { user, initialized } = useAppSelector(state => state.auth);
  useNotifications(); // Enable toast notifications

  useEffect(() => {
    dispatch(fetchCurrentUser());
  }, [dispatch]);

  if (!initialized) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        Загрузка...
      </div>
    );
  }

  // If user is not authenticated, show login page
  if (!user) {
    return <Login />;
  }

  // If user has no company, redirect to appropriate page
  const hasCompany = user?.company !== null;

  return (
    <Routes>
      {/* Onboarding route - for users without company */}
      <Route path="/onboarding" element={
        !hasCompany ? <Onboarding /> : <Navigate to="/" replace />
      } />

      {/* No company error page */}
      <Route path="/no-company" element={
        !hasCompany ? <NoCompany /> : <Navigate to="/" replace />
      } />

      {/* Main application routes - require company */}
      <Route element={hasCompany ? <MainLayout /> : <Navigate to="/no-company" replace />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/inventory" element={<Inventory />} />
        <Route path="/settings/*" element={<Settings />} />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <ConfigProvider theme={theme} locale={ruRU}>
          <AntApp>
            <BrowserRouter>
              <AppRoutes />
            </BrowserRouter>
          </AntApp>
        </ConfigProvider>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;
