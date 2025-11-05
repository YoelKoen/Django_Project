# config/settings.py

INSTALLED_APPS = [
    # ... default apps
    'news_app',
    'sticky_app', # Include your sticky app too
    'rest_framework', # Required for API design
    # ...
]

# Configure the Custom User Model
AUTH_USER_MODEL = 'news_app.CustomUser'