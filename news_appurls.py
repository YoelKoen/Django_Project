# news_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Editor Review Panel URLs
    path('editor/review/', views.editor_review_list, name='editor_review_list'),
    path('editor/approve/<int:pk>/', views.approve_article, name='approve_article'),
    # ... other app URLs
]

# news_app/urls.py (Add to existing urlpatterns)
from django.urls import path
from . import api_views
from . import views # Keep existing views

urlpatterns = [
    # Editor Review Panel URLs
    # ... existing paths for editor views ...

    # API Endpoint for Subscribers
    path('api/articles/subscribed/', api_views.SubscriberArticleListView.as_view(), name='api_subscribed_articles'),
]