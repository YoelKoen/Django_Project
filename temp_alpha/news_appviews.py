# news_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Article
from .decorators import editor_required # Import the custom decorator

# View 1: List articles waiting for approval
@login_required
@editor_required
def editor_review_list(request):
    """Lists all articles where is_approved is False."""
    unapproved_articles = Article.objects.filter(is_approved=False).select_related('author', 'publisher')
    context = {'articles': unapproved_articles}
    return render(request, 'news_app/editor_review_list.html', context)

# View 2: Handle the approval action
@login_required
@editor_required
def approve_article(request, pk):
    """Sets an article's is_approved field to True."""
    article = get_object_or_404(Article, pk=pk)
    
    # We only change the field here. The post-approval logic (email/X post)
    # will be handled by the Django Signal when article.save() is called.
    if not article.is_approved:
        article.is_approved = True
        article.save()
    
    return redirect(reverse('editor_review_list')) 
    # Redirect back to the review list