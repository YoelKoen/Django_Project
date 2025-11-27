# news_app/tests.py (Add to existing content)
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser, Article, Publisher
from django.contrib.auth.models import Group

class SubscriptionAPITestCase(APITestCase):

    def setUp(self):
        # 1. Setup Groups (Journalist and Reader roles)
        self.reader_group = Group.objects.create(name='Reader')
        self.journalist_group = Group.objects.create(name='Journalist')

        # 2. Setup Users
        self.reader_user = CustomUser.objects.create_user(username='reader1', password='testpassword', email='r@r.com')
        self.reader_user.groups.add(self.reader_group) # Assign role
        
        self.journalist_user = CustomUser.objects.create_user(username='journalist1', password='testpassword', email='j@j.com')
        self.journalist_user.groups.add(self.journalist_group) # Assign role
        
        self.publisher1 = Publisher.objects.create(name='The Daily Post')
        self.publisher2 = Publisher.objects.create(name='Tech Trends')
        
        # 3. Setup Articles (Approved and Unapproved)
        # Article 1: Approved, from subscribed publisher (Should appear)
        self.article1 = Article.objects.create(title='Pub1 Approved', content='...', is_approved=True, author=self.journalist_user, publisher=self.publisher1)
        # Article 2: Approved, from non-subscribed publisher (Should NOT appear)
        self.article2 = Article.objects.create(title='Pub2 Approved', content='...', is_approved=True, author=self.journalist_user, publisher=self.publisher2)
        # Article 3: Unapproved, from subscribed publisher (Should NOT appear)
        self.article3 = Article.objects.create(title='Pub1 Unapproved', content='...', is_approved=False, author=self.journalist_user, publisher=self.publisher1)
        
        # 4. Make the reader subscribe to Publisher 1
        self.reader_user.subscriptions_to_publishers.add(self.publisher1)
        
        self.url = reverse('api_subscribed_articles')

    def test_unauthenticated_access_denied(self):
        """Ensure unauthenticated users get 403 Forbidden."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_gets_subscribed_articles_only(self):
        """Test that the user only receives articles based on subscriptions and approval status."""
        
        # Log in the reader user
        self.client.login(username='reader1', password='testpassword')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only receive Article 1
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Pub1 Approved')

    def test_subscription_to_journalist(self):
        """Test filtering logic for journalist subscriptions."""
        
        # Subscribe the reader to the journalist (Article 2 author)
        self.reader_user.subscriptions_to_publishers.clear() # Clear publisher sub
        self.reader_user.subscriptions_to_journalists.add(self.journalist_user)
        
        # Create a new approved article from the subscribed journalist (Article 4)
        Article.objects.create(title='Journalist Approved', content='...', is_approved=True, author=self.journalist_user, publisher=self.publisher2)
        
        self.client.login(username='reader1', password='testpassword')
        response = self.client.get(self.url)
        
        # Should now receive Article 4 (Journalist Approved)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['title'] == 'Journalist Approved' for item in response.data))


# news_app/tests.py (Example addition)
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import CustomUser, Article
from django.contrib.auth.models import Group, Permission
from django.test import Client

class EditorAccessTest(APITestCase):

    def setUp(self):
        # Create roles/groups (assuming they exist from the signal)
        self.editor_group = Group.objects.get(name='Editor')
        self.journalist_group = Group.objects.get(name='Journalist')

        # Create users
        self.editor_user = CustomUser.objects.create_user(username='editor', password='p', is_staff=True)
        self.editor_user.groups.add(self.editor_group)
        
        self.journalist_user = CustomUser.objects.create_user(username='journalist', password='p')
        self.journalist_user.groups.add(self.journalist_group)
        
        self.unapproved_article = Article.objects.create(title='Needs Review', content='...', is_approved=False, author=self.journalist_user)
        self.approve_url = reverse('approve_article', kwargs={'pk': self.unapproved_article.pk})

    def test_editor_can_approve(self):
        """Editor should be able to approve an article."""
        self.client.login(username='editor', password='p')
        response = self.client.post(self.approve_url)
        # Should redirect back to the review list
        self.assertEqual(response.status_code, 302) 
        self.unapproved_article.refresh_from_db()
        self.assertTrue(self.unapproved_article.is_approved)

    def test_journalist_cannot_approve(self):
        """Journalist should be blocked from approval view (Permission Denied)."""
        self.client.login(username='journalist', password='p')
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, 403) # Forbidden
        
    def test_unauthenticated_cannot_approve(self):
        """Unauthenticated user should be redirected to login."""
        response = self.client.post(self.approve_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)