import { Card, Button, Typography, Space, Form, Input, Alert } from 'antd';
import { LoginOutlined, UserOutlined, LockOutlined } from '@ant-design/icons';
import { useState } from 'react';
import api from '@/services/api';

const { Title, Paragraph } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (values: LoginForm) => {
    setLoading(true);
    setError(null);
    
    try {
      // Send login request to Django
      await api.login(values.username, values.password);
      // Reload page to fetch user data
      window.location.reload();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '24px'
    }}>
      <Card style={{ 
        maxWidth: '450px', 
        width: '100%',
        borderRadius: '12px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <UserOutlined style={{ fontSize: '48px', color: '#1890FF', marginBottom: '16px' }} />
          <Title level={2} style={{ marginBottom: '8px' }}>Добро пожаловать в ForecastMP</Title>
          <Paragraph type="secondary">
            Интеллектуальная платформа управления запасами
          </Paragraph>
        </div>

        {error && (
          <Alert
            message="Ошибка входа"
            description={error}
            type="error"
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: '24px' }}
          />
        )}

        <Form
          name="login"
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Пожалуйста, введите email!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Email"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Пароль"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              icon={<LoginOutlined />}
              style={{
                height: '48px',
                fontSize: '16px',
                fontWeight: '500',
                borderRadius: '8px'
              }}
            >
              Войти
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
