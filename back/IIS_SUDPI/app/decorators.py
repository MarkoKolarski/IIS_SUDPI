from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_func(request, *args, **kwargs):
            if request.user.tip_k in allowed_roles:
                return view_func(request, *args, **kwargs)
            return Response(
                {'error': 'Nemate dozvolu za pristup ovoj stranici.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return wrapped_func
    return decorator
