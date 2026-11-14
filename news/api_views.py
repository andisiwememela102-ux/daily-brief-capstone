import secrets
from django.conf import settings
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article, ApprovedArticleLog, Newsletter, Publisher
from .permissions import ArticleRolePermission, IsEditor
from .serializers import ArticleSerializer, NewsletterSerializer, PublisherSerializer, UserSerializer

class ArticleListCreateView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [ArticleRolePermission]

    def get_queryset(self):
        return Article.objects.filter(approved=True).select_related('author', 'publisher')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, publisher=None)

class SubscribedArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or user.role != 'reader':
            return Article.objects.none()
        return Article.objects.filter(approved=True).filter(
            Q(publisher__in=user.subscribed_publishers.all()) |
            Q(author__in=user.subscribed_journalists.all())
        ).select_related('author', 'publisher').distinct()

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [ArticleRolePermission]

    def get_queryset(self):
        queryset = Article.objects.select_related('author', 'publisher')
        if self.request.user.role == 'editor':
            return queryset
        if self.request.user.role == 'journalist':
            return queryset.filter(Q(approved=True) | Q(author=self.request.user))
        return queryset.filter(approved=True)

class NewsletterListView(generics.ListCreateAPIView):
    serializer_class = NewsletterSerializer

    def get_queryset(self):
        return Newsletter.objects.filter(articles__approved=True).distinct() | Newsletter.objects.filter(articles__isnull=True)

    def perform_create(self, serializer):
        if self.request.user.role not in ('journalist', 'editor'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only journalists and editors may create newsletters.')
        serializer.save(author=self.request.user)

class NewsletterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsEditorOrNewsletterAuthor()]

class IsEditorOrNewsletterAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'editor' or obj.author_id == request.user.id

class PublisherListView(generics.ListAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

class UserListView(generics.ListAPIView):
    from django.contrib.auth import get_user_model
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class ApproveArticleView(APIView):
    permission_classes = [IsEditor]

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({'detail': 'Article not found.'}, status=status.HTTP_404_NOT_FOUND)
        article.approved = True
        article.save(update_fields=['approved'])
        return Response(ArticleSerializer(article).data)

class ApprovedArticleLogView(APIView):
    """Internal endpoint called by the approval signal using a shared secret."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        supplied = request.headers.get('X-Approval-Secret', '')
        if not secrets.compare_digest(supplied, settings.APPROVED_API_SECRET):
            return Response({'detail': 'Invalid integration secret.'}, status=status.HTTP_403_FORBIDDEN)
        article_id = request.data.get('article_id')
        try:
            article = Article.objects.get(pk=article_id, approved=True)
        except (Article.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Approved article not found.'}, status=status.HTTP_404_NOT_FOUND)
        log, _ = ApprovedArticleLog.objects.get_or_create(article=article, defaults={'title': article.title})
        return Response({'id': log.id, 'article_id': article.id, 'title': log.title}, status=status.HTTP_201_CREATED)
