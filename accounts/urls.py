from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('me/', views.current_user, name='current-user'),
    path('logout/', views.logout_view, name='logout'),
]
