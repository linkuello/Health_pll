from django.contrib import admin
from django.urls import path
from . import views 
from .views import register, verify_email


urlpatterns = [

    path('articles/', views.get_articles, name='get_articles'),
    path('articles/<int:id>/', views.get_article_by_id, name='get_article_by_id'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('register/', register, name='register'),
    path('verify/<uidb64>/<token>/', verify_email, name='verify_email'),


    
]
