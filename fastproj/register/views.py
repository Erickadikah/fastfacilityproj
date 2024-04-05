from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as django_logout


@csrf_exempt
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # You don't need to authenticate the user after registration,
            # because the user is already created and authenticated by the save() method
            login(request, user)
            return redirect("/login/")  # Redirect to login page or any other page after registration
        else:
            # Display error messages if the form is invalid
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/host/")
    return render(request, "login.html")
# user logout view
@login_required
def logout_view(request):
    django_logout(request)
    return redirect("/")
    

def user_list(request):
    users = User.objects.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            # Add more fields as needed
        }
        user_list.append(user_data)
    return JsonResponse(user_list, safe=False)

# user with user id
def user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            # Add more fields as needed
        }
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)