# news_app/serializers.py
from rest_framework import serializers
from .models import Article, CustomUser, Publisher

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class JournalistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']

class ArticleSerializer(serializers.ModelSerializer):
    author = JournalistSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'publisher', 'created_at']
        # Note: We do not expose 'is_approved' as the API should only show approved articles.