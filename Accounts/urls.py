from django.urls import path
from . import views


urlpatterns = [
    path('checkout/', views.Register, name='checkout'),
    path('profile/', views.Profile, name='profile'),
]