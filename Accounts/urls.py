from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.Register, name='register'),
    path('profile/', views.Profile, name='profile'),
]