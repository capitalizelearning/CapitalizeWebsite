"""
    This module contains the views for the accounts app.
"""

import re

from django.contrib.auth.models import User
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import models


class ApiRoot(APIView):
    """API root view. Redirects to the swagger documentation."""
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, _):
        """Redirects to the swagger documentation."""
        return redirect('/v1/schema/swagger/')


class ProfileView(APIView):
    """Profile view."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Returns the user's profile information."""
        user: User = request.user
        return Response(models.UserSerializer(user).data)


class WaitListView(APIView):
    """Wait-list view."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Adds a user to the wait-list"""
        email: str = request.data.get('email')
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({"error": "Please provide a valid email address"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if user is already in the wait-list
        user = models.WaitingList.objects.filter(email=email).first()  # pylint: disable=no-member
        if user is not None:
            return Response({"message": "You are already in the wait-list"},
                            status=status.HTTP_200_OK)
        models.WaitingList.objects.create(email=email)  # pylint: disable=no-member

        return Response({"message": "You have been added to the wait-list"},
                        status=status.HTTP_201_CREATED)

    def get(self, request):
        """Returns the wait-list."""
        if request.user.is_staff:
            wait_list = models.WaitingList.objects.all()  # pylint: disable=no-member
            return Response(
                models.WaitListSerializer(wait_list, many=True).data)
        raise exceptions.PermissionDenied(
            "You do not have permission to access this resource")


class CreateTestUserView(APIView):
    """Converts a wait-list member to a test user"""
    permission_classes = [IsAdminUser]

    @extend_schema(request=models.CreateTestUserSerializer)
    def post(self, request):
        """Creates a test user"""
        serializer = models.CreateTestUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # pylint: disable=no-member
        return Response(
            {"registration_token": serializer.instance.registration_token},
            status=status.HTTP_201_CREATED)


class SetTestUserPassword(APIView):
    """Sets the password for a test user"""
    permission_classes = [AllowAny]

    @extend_schema(request=models.SetTestUserPasswordSerializer,
                   responses={200: None})
    def post(self, request, registration_token: str):
        """Sets the password for a test user"""
        user = models.Profile.get_user_by_activation_token(registration_token)
        if user is None:
            raise exceptions.NotFound("Invalid token")
        new_password = request.data.get('password')
        if not new_password:
            raise exceptions.ValidationError("Password is required")
        if len(new_password) < 8:
            raise exceptions.ValidationError(
                "Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', new_password):
            raise exceptions.ValidationError(
                "Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', new_password):
            raise exceptions.ValidationError(
                "Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', new_password):
            raise exceptions.ValidationError(
                "Password must contain at least one digit")
        user.set_password(new_password)
        user.is_active = True
        user.profile.registration_token = None
        user.profile.save()
        user.save()
        return Response({"message": "Password updated successfully"},
                        status=status.HTTP_200_OK)
