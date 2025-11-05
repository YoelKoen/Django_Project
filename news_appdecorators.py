# news_app/decorators.py
from django.core.exceptions import PermissionDenied

def editor_required(function):
    """
    Decorator for views that checks if the user is logged in AND is a member of the 'Editor' group.
    """
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated and belongs to the 'Editor' group
        if request.user.is_authenticated and request.user.groups.filter(name='Editor').exists():
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper