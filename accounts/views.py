from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render


def user_login(request):
    """Login view.
    GET:
        Render the login page
    POST: 
        Handle login form submission"""
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    if request.method == 'POST':
        pass


def register_user(request):
    """Register view.
    GET:
        Render the register page
    POST: 
        Handle register form submission"""
    if request.method == 'GET':
        return render(request, 'auth/register.html')
    if request.method == 'POST':
        pass
