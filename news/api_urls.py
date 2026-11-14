from django.urls import path
from .api_views import (
    ArticleListCreateView, ArticleDetailView, SubscribedArticleListView,
    NewsletterListView, NewsletterDetailView, PublisherListView, UserListView,
    ApproveArticleView, ApprovedArticleLogView,
)

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='api-articles'),
    path('articles/subscribed/', SubscribedArticleListView.as_view(), name='api-subscribed-articles'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='api-article-detail'),
    path('articles/<int:pk>/approve/', ApproveArticleView.as_view(), name='api-article-approve'),
    path('newsletters/', NewsletterListView.as_view(), name='api-newsletters'),
    path('newsletters/<int:pk>/', NewsletterDetailView.as_view(), name='api-newsletter-detail'),
    path('publishers/', PublisherListView.as_view(), name='api-publishers'),
    path('users/', UserListView.as_view(), name='api-users'),
    path('approved/', ApprovedArticleLogView.as_view(), name='api-approved-log'),
]
