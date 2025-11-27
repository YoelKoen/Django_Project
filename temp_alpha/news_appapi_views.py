# news_app/api_views.py
from rest_framework import generics, permissions
from .models import Article, CustomUser
from .serializers import ArticleSerializer
from django.db.models import Q # Used for complex OR conditions

class SubscriberArticleListView(generics.ListAPIView):
    """
    API endpoint that returns a list of approved articles 
    based on the authenticated user's subscriptions.
    """
    serializer_class = ArticleSerializer
    # Only allow authenticated users to access this endpoint
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        # 1. Get the authenticated user (API Client is treated as a CustomUser)
        user = self.request.user
        
        # 2. Find all publishers and journalists the user is subscribed to
        subscribed_publishers = user.subscriptions_to_publishers.all()
        subscribed_journalists = user.subscriptions_to_journalists.all()
        
        # 3. Construct the complex Q object filter:
        # The article must be approved AND (match a subscribed publisher OR match a subscribed journalist)
        
        article_filter = Q(is_approved=True) & (
            Q(publisher__in=subscribed_publishers) |
            Q(author__in=subscribed_journalists)
        )
        
        # 4. Filter and return the unique articles
        queryset = Article.objects.filter(article_filter).distinct()
        
        return queryset.order_by('-created_at')