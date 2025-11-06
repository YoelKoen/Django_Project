# config/settings.py (Ensure this reflects your actual credentials)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',       # e.g., news_capstone_db
        'USER': 'your_db_username',        
        'PASSWORD': 'your_db_password',    
        'HOST': '127.0.0.1',               
        'PORT': '3306',                   
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}