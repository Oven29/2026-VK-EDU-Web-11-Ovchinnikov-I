from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter(name='name')
def name_filter(user):
    """
    Returns formatted user name: 'FirstName L.' or 'Username'
    """
    if not user:
        return ""
        
    if not isinstance(user, User):
        if hasattr(user, 'user'):
            user = user.user
        else:
            return str(user)
            
    if not user.first_name:
        return user.username
        
    res = user.first_name
    if user.last_name:
        res += f' {user.last_name[0]}.'
    return res
