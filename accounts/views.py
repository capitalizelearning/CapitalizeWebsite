"""
    This module contains the views for the accounts app.
    It provides the following views:
        - `login_user`: Handles user login
        - `register_user`: Handles user registration
        - `profile`: Returns the user's profile information. * Requires login
        - `logout_user`: Logs out the user
    It also provides the `app_login_required` decorator to protect views that require login.
    The views are mapped in the `accounts/urls.py` file.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render


def app_login_required(view):
    """Decorator to protect views that require login"""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        # Redirect to login page with the current path as the next parameter
        return render(request, 'auth/login.html?next=' + request.path)

    return wrapper


def login_user(request):
    """Login view.
    GET:
        Render the login page
    POST: 
        Handle login form submission"""
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    if request.method == 'POST':
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        remember: bool = request.POST.get('remember', False)
        next_page: str = request.GET.get('next',
                                         '/')  # TODO: Update default next page

        if (not username or not password):
            messages.error(request, "Invalid username or password")
            return redirect('auth/login.html')

        user: User = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            request.session.set_expiry(0 if remember else 1209600)
            messages.success(request, f"Welcome back, {username}!")
            return redirect(next_page)

        messages.error(request,
                       "The email or password does not match our records.")
        return render(request, 'auth/login.html')
    return HttpResponseNotAllowed(['GET', 'POST'])


def register_user(request):
    """Register view.
    GET:
        Render the register page
    POST: 
        Handle register form submission"""
    if request.method == 'GET':
        return render(request, 'auth/register.html')
    if request.method == 'POST':
        username: str = request.POST.get('username')
        first_name: str = request.POST.get('first_name')
        last_name: str = request.POST.get('last_name')
        # institution_short_code: str = request.POST.get('institution_short_code')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if not (username and first_name and last_name and password
                and password_confirm):
            messages.error(request, "Please fill in all the fields")
            return render(request, 'auth/register.html')

        if password != password_confirm:
            messages.error(request, "Passwords do not match")
            return render(request, 'auth/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'auth/register.html')

        user = User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        username=username,
                                        password=password)
        user.save()
        messages.success(request, "Account created successfully")
        return redirect('login')
    return HttpResponseNotAllowed(['GET', 'POST'])


@app_login_required
def profile(request):
    """Profile view.
    GET:
        Render the user's profile page"""
    if request.method == 'GET':
        # Test if the user is authenticated
        user = request.user
        serialized_user = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return JsonResponse(serialized_user)
    return HttpResponseNotAllowed(['GET'])


def logout_user(request):
    """Logout view.
    GET:
        Handle user logout"""
    if request.method == 'GET':
        logout(request)
        messages.success(request, "You have been logged out")
        return render(request, 'auth/login.html')
    return HttpResponseNotAllowed(['GET'])
