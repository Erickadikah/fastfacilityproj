from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required as django_login_required

def login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirecting to login page
        return view_func(request, *args, **kwargs)
    return wrapped_view

login_required_builtin = django_login_required