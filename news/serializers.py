from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Article, Newsletter, Publisher

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name', 'description')

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'author', 'publisher', 'created_at', 'approved')
        read_only_fields = ('id', 'author', 'publisher', 'created_at', 'approved')

    def validate(self, attrs):
        # Article ownership is assigned by the view and cannot be transferred via the API.
        if self.instance and bool(self.instance.author_id) == bool(self.instance.publisher_id):
            raise serializers.ValidationError('The article must have exactly one source.')
        return attrs

class NewsletterSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    articles = serializers.PrimaryKeyRelatedField(many=True, queryset=Article.objects.filter(approved=True), required=False)

    class Meta:
        model = Newsletter
        fields = ('id', 'title', 'description', 'created_at', 'author', 'articles')
        read_only_fields = ('id', 'created_at', 'author')
