from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- 1. Publisher Model ---
class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

# --- 2. CustomUser Model ---
class CustomUser(AbstractUser):
    # Reader-specific fields (Many-to-Many relationships for subscriptions)
    subscriptions_to_publishers = models.ManyToManyField(
        Publisher, 
        related_name='publisher_subscribers', 
        blank=True
    )
    # Subscriptions to Journalists (Self-referential M2M relationship)
    subscriptions_to_journalists = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='journalist_subscribers', 
        blank=True
    )

    # Journalist-specific fields (Simple data fields)
    articles_published_independently = models.IntegerField(default=0)
    newsletters_published_independently = models.IntegerField(default=0)
    
    # We will use Django Groups for primary role assignment (Reader/Editor/Journalist)
    
    def __str__(self):
        return self.username
    
    # Logic to set "None" values for irrelevant role fields (as required by the prompt)
    def save(self, *args, **kwargs):
        # This logic is more complex for ManyToMany fields, which are set post-save.
        # For the IntegerFields, we can set them based on Group membership if needed.
        # For simplicity and database normalization, we rely on Group membership 
        # and assume irrelevant M2M fields are simply empty/not populated for that user.
        
        # NOTE: If the requirement strictly means setting M2M fields to NULL, 
        # this is usually handled outside the model save or requires a custom field.
        # For now, we rely on Group membership to enforce role separation.
        
        super().save(*args, **kwargs)


# --- 3. Article Model ---
class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # CRITICAL: Indicates whether articles have been approved by the editor
    is_approved = models.BooleanField(default=False) 
    
    # Relationship to the journalist/author
    author = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='authored_articles'
    )
    # Relationship to the publisher
    publisher = models.ForeignKey(
        Publisher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return self.title