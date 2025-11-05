# news_app/signals.py

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Article, Publisher  # Import your models

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Only run for your news_app
    if sender.name != 'news_app':
        return

    # 1. Get ContentType for the Article model
    article_ct = ContentType.objects.get_for_model(Article)
    
    # Get all permissions for the Article model
    view_perm = Permission.objects.get(codename='view_article', content_type=article_ct)
    add_perm = Permission.objects.get(codename='add_article', content_type=article_ct)
    change_perm = Permission.objects.get(codename='change_article', content_type=article_ct)
    delete_perm = Permission.objects.get(codename='delete_article', content_type=article_ct)

    # --- 2. Define Permissions per Role ---

    # A. Reader: Can only view articles
    reader_group, created = Group.objects.get_or_create(name='Reader')
    if created or not reader_group.permissions.exists():
        reader_group.permissions.add(view_perm)
        print("Set up Reader Group.")
        
    # B. Editor: Can view, update, and delete articles (for approval/review)
    editor_group, created = Group.objects.get_or_create(name='Editor')
    if created or not editor_group.permissions.exists():
        editor_group.permissions.add(view_perm, change_perm, delete_perm)
        # Editors should also have a specific permission for the 'is_approved' field
        # This often requires a custom permission in the Article Meta class, but
        # for simplicity here, we assume change_perm covers the ability to change the Article object.
        print("Set up Editor Group.")

    # C. Journalist: Can create, view, update, and delete articles/newsletters (CRUD)
    journalist_group, created = Group.objects.get_or_create(name='Journalist')
    if created or not journalist_group.permissions.exists():
        journalist_group.permissions.add(add_perm, view_perm, change_perm, delete_perm)
        # Note: 'newsletters' would require similar permissions on a separate Newsletter model.
        print("Set up Journalist Group.")

    # news_app/signals.py (Add to existing content)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Article, CustomUser
# from requests import post # You'll need to pip install requests and configure X API keys

# --- Signal Receiver 1: Send Email to Subscribers ---
@receiver(post_save, sender=Article)
def notify_subscribers_on_approval(sender, instance, created, **kwargs):
    """Sends email notifications when an article is first approved."""
    
    # We only act if the article was NOT newly created and is now approved
    if not created and instance.is_approved and 'is_approved' in instance.get_dirty_fields(): 
        # Note: 'get_dirty_fields()' is not standard Django, a pre_save check is safer.
        # For simplicity, we check if it was recently approved.
        
        # 1. Get the list of subscriber emails
        subscriber_emails = set()
        
        # Add readers subscribed to the article's publisher
        if instance.publisher:
            publisher_subscribers = CustomUser.objects.filter(
                subscriptions_to_publishers=instance.publisher
            ).values_list('email', flat=True)
            subscriber_emails.update(publisher_subscribers)
            
        # Add readers subscribed to the article's author (journalist)
        if instance.author:
            author_subscribers = CustomUser.objects.filter(
                subscriptions_to_journalists=instance.author
            ).values_list('email', flat=True)
            subscriber_emails.update(author_subscribers)

        # 2. Send the email
        if subscriber_emails:
            subject = f"New Approved Article: {instance.title}"
            message = f"Read the latest article by {instance.author.username} at [Link to Article]\n\n{instance.content[:200]}..."
            send_mail(
                subject,
                message,
                'noreply@yournewsapp.com', # Use a valid sender email
                list(subscriber_emails),
                fail_silently=False,
            )
            print(f"Sent approval email for {instance.title} to {len(subscriber_emails)} users.")


# --- Signal Receiver 2: Post to X (formerly Twitter) API ---
@receiver(post_save, sender=Article)
def post_to_x_on_approval(sender, instance, created, **kwargs):
    """Posts a brief update to X using its HTTP API."""
    
    if not created and instance.is_approved: # Simple check for approval
        try:
            # Note: This requires a complex setup including obtaining Bearer/OAuth tokens.
            # This is a conceptual implementation.
            
            # API_ENDPOINT = "https://api.twitter.com/2/tweets"
            # HEADERS = {"Authorization": "Bearer YOUR_BEARER_TOKEN"}
            # payload = {
            #     "text": f"Article Approved: '{instance.title}' by @{instance.author.username}! #NewsApp #Approved"
            # }
            # response = post(API_ENDPOINT, headers=HEADERS, json=payload)
            # response.raise_for_status() # Raise an exception for bad status codes
            print(f"Successfully simulated posting article {instance.title} to X.")

        except Exception as e:
            # Log the error instead of crashing the app
            print(f"ERROR: Failed to post to X for article {instance.pk}: {e}")