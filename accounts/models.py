from enum import Enum

from django.contrib.auth.models import User
from django.core import serializers
from django.db import models


class WaitingList(models.Model):
    """Waiting list model.
        Represents users who are waiting to create an account."""

    id = models.AutoField(primary_key=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"<WaitingList: {self.id}>"

    def serialize(self, output_format: str = 'json'):
        """Return a serialized representation of the model instance in the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])

class ProfileType(Enum):
    """Enumeration for user profile types."""
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'


class Profile(models.Model):
    """User profile model. 
        Extends the default User model with additional fields through a one-to-one relationship."""

    id = models.AutoField(primary_key=True)
    account_type = models.CharField(max_length=10,
                                    choices=[(tag, tag.value)
                                             for tag in ProfileType])
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    streak_days = models.IntegerField(default=0)

    def __str__(self):
        return f"<Profile: {self.user.username}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class Preferences(models.Model):
    """User preferences model. 
        Extends the default User model with additional fields through a one-to-one relationship."""

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    language = models.CharField(max_length=2, default='en')

    def __str__(self):
        return f"<Preferences: {self.user.username}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class Institution(models.Model):
    """Institution model. 
        Represents an educational institution."""

    id = models.AutoField(primary_key=True)
    short_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"<Institution: {self.name}>"

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class Class(models.Model):
    """Class model. 
        Represents a class or course in an educational institution."""

    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    short_code = models.CharField(max_length=10, unique=True)
    long_name = models.CharField(
        max_length=100)  # e.g., "Principles of Programming Languages"
    short_name = models.CharField(max_length=9, blank=True)  # e.g., "CS 3300"
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"<Class: {self.long_name}>"

    def serialize(self, output_format: str = 'json'):
        """Return a serialized representation of the model instance in the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class Enrollment(models.Model):
    """Enrollment model. 
        Represents a student's enrollment in a class."""

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"<Enrollment: {self.student.username} in {self.class_id.long_name}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Return a serialized representation of the model instance in the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])
