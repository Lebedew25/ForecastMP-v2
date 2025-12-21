import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from accounts.models import User, Company

# Создаем компанию, если её нет
company, created = Company.objects.get_or_create(
    name='Demo Company',
    defaults={
        'settings': {'timezone': 'UTC'}
    }
)

if created:
    print(f'✓ Создана компания: {company.name}')
else:
    print(f'✓ Компания уже существует: {company.name}')

# Создаем суперпользователя, если его нет
if not User.objects.filter(email='admin@example.com').exists():
    user = User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        company=company,
        first_name='Admin',
        last_name='User'
    )
    print(f'✓ Создан суперпользователь: {user.email}')
    print(f'  Пароль: admin123')
else:
    print('✓ Суперпользователь уже существует')

print('\n' + '='*50)
print('Для входа в админку используйте:')
print('Email: admin@example.com')
print('Пароль: admin123')
print('URL: http://127.0.0.1:8000/admin/')
print('='*50)
