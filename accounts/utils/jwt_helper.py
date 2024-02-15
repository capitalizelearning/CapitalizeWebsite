"""
    This module contains the TokenHelper class for JWT token encoding and decoding.
"""

from datetime import datetime, timedelta
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User
from jwt import decode, encode


class TokenHelper:
    """Helper class for JWT token encoding and decoding."""

    @staticmethod
    def encode_token(user: User) -> tuple:
        """Return a JWT token for the user and its expiration time."""
        expires = int(
            (datetime.utcnow() +
             timedelta(hours=settings.JWT_EXPIRATION_HOURS)).timestamp())
        payload = {
            'sub': user.id,
            'aud': 'admin' if user.is_staff else 'user',
            'iat': int(datetime.utcnow().timestamp()),
            'exp': expires
        }
        return encode(payload, settings.SECRET_KEY, algorithm='HS256'), expires

    @staticmethod
    def decode_token(token: str) -> Optional[User]:
        """Decode a JWT token and returns the associated User object."""
        decoded_token = decode(token,
                               settings.SECRET_KEY,
                               algorithms=['HS256'])

        user_id = decoded_token.get("sub")
        if user_id is not None:
            return User.objects.get(id=user_id)
        return None
