# news_app/apps.py

from django.apps import AppConfig

class NewsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_app'

    def ready(self):
        # Import the signals file to connect the receiver functions
        import temp_beta.signals