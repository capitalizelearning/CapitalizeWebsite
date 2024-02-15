"""
    This module contains the views for the accounts app.
"""
from functools import wraps

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserSerializer
from accounts.utils.jwt_helper import TokenHelper


def jwt_required(f):
    """Decorator for views that require JWT authentication.
        
        Sets the `request.user` attribute to the authenticated user.
        @example:
        ```python
        class MyView(APIView):
            @jwt_required
            def get(self, request):
                user: User = request.user
                return JsonResponse({"message": f"Hello, {user.username}!"})
        ```
    """

    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            return Response({"error": "Missing authorization header"},
                            status=status.HTTP_401_UNAUTHORIZED,
                            headers={"WWW-Authenticate": "Bearer"})

        token = token.split(" ")[1]
        user = TokenHelper.decode_token(token)
        if user is None:
            return Response({"error": "Invalid token"},
                            status=status.HTTP_401_UNAUTHORIZED,
                            headers={"WWW-Authenticate": "Bearer"})
        request.user = user
        return f(request, *args, **kwargs)

    return decorated_function


class LoginView(APIView):
    """Login view."""

    def post(self, request):
        """Verifies username and password, and returns a JWT auth token" """
        if request.content_type != 'application/x-www-form-urlencoded':
            return Response({"error": "Invalid content type"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Request body
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        grant_type: str = request.POST.get('grant_type')

        # Validate grant type
        if grant_type != 'password':
            return Response({"error": "Invalid grant type"},
                            status=status.HTTP_400_BAD_REQUEST,
                            headers={"WWW-Authenticate": "Bearer"})

        # Validate username and password
        if (not username or not password):
            return Response(
                {"error": "Both username and password are required fields"},
                status=status.HTTP_400_BAD_REQUEST,
                headers={"WWW-Authenticate": "Bearer"})

        # Authenticate user
        user: User = User.objects.filter(username=username).first()
        if user is not None and user.check_password(password):
            # Generate token
            (token, expires) = TokenHelper.encode_token(user)
            return Response({
                "access_token": token,
                "expires_in": expires,
                "token_type": "Bearer"
            })
        return Response({"error": "Invalid username or password"},
                        status=status.HTTP_401_UNAUTHORIZED,
                        headers={"WWW-Authenticate": "Bearer"})


class RegisterView(APIView):
    """Register view"""

    def post(self, request):
        """Registers a new user."""
        if request.content_type != 'application/x-www-form-urlencoded':
            return Response({"error": "Invalid content type"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Request body
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        email: str = request.POST.get('email')
        first_name: str = request.POST.get('first_name')
        last_name: str = request.POST.get('last_name')

        # Validate username and password
        if (not username or not password):
            return Response(
                {"error": "Both username and password are required fields"},
                status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user: User = User.objects.create_user(username=username,
                                              email=email,
                                              password=password,
                                              first_name=first_name,
                                              last_name=last_name)
        user.save()
        return Response({"message": "User created successfully"},
                        status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    """Profile view."""

    @jwt_required
    def get(self):
        """Returns the user's profile information."""
        user: User = self.request.user
        return Response(UserSerializer(user).data)
