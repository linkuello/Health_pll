from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('articles/', views.get_articles, name='get_articles'),
    path('articles/<int:id>/', views.get_article_by_id, name='get_article_by_id'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]
