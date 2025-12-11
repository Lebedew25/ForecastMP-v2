"""
URL configuration for onboarding app
"""
from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('', views.onboarding_wizard, name='wizard'),
    path('api/onboarding/submit/', views.submit_onboarding, name='submit'),
]