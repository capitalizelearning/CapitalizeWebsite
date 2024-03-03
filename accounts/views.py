"""
    This module contains the views for the accounts app.
"""

import re

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from accounts.models import UserSerializer, WaitingList, WaitListSerializer


class ProfileView(APIView):
    """Profile view."""
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns the user's profile information."""
        user: User = request.user
        return Response(UserSerializer(user).data)


class WaitListView(APIView):
    """Wait-list view."""

    def post(self, request):
        """Adds a user to the wait-list"""
        email: str = request.data.get('email')
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({"error": "Please provide a valid email address"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if user is already in the wait-list
        user = WaitingList.objects.filter(email=email).first()  # pylint: disable=no-member
        if user is not None:
            return Response({"message": "You are already in the wait-list"},
                            status=status.HTTP_200_OK)
        WaitingList.objects.create(email=email)  # pylint: disable=no-member

        return Response({"message": "You have been added to the wait-list"},
                        status=status.HTTP_201_CREATED)

    def get(self, request):
        """Returns the wait-list"""
        if not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to view this resource"},
                status=status.HTTP_403_FORBIDDEN)
        waiting_list = WaitingList.objects.all()  # pylint: disable=no-member
        return Response(WaitListSerializer(waiting_list, many=True).data)
