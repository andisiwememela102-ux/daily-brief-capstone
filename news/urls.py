from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('articles/<int:pk>/', views.article_detail, name='article-detail'),
    path('editor/review/', views.review_articles, name='review-articles'),
    path('editor/approve/<int:pk>/', views.approve_article, name='approve-article'),
    path('newsletters/', views.newsletter_list, name='newsletter-list'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
