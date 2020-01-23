"""airplant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic.base import TemplateView
from django.urls import include, path
from django.contrib import admin
from decouple import config



urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', include('Accounts.urls')),
    path('', include('Backend.urls')),
    path(config('ADMIN_URL'), admin.site.urls),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('checkout/', TemplateView.as_view(template_name='checkout.html'), name='checkout'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('gift-checkout/', TemplateView.as_view(template_name='gift-checkout.html'), name='gift-checkout'),
    path('gift/', TemplateView.as_view(template_name='gift.html'), name='gift'),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('header/', TemplateView.as_view(template_name='header.html'), name='header'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
]
