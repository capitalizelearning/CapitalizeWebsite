"""
    Account models for the application.
    Contains account related models and their serializers.
"""
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the user model."""

    profile = serializers.HyperlinkedRelatedField(view_name='profile-detail',
                                                  read_only=True)
    preferences = serializers.HyperlinkedRelatedField(
        view_name='preferences-detail', read_only=True)
    enrollment = serializers.HyperlinkedRelatedField(
        view_name='enrollment-detail', read_only=True)

    class Meta:
        """Meta class for the user serializer."""
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'is_staff',
            'is_active', 'date_joined', 'profile', 'preferences', 'enrollment'
        ]


class WaitingList(models.Model):
    """Waiting list model.
        Represents users who are waiting to create an account."""

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"<WaitingList: {self.id}>"


class WaitListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the waiting list model."""

    class Meta:
        """Meta class for the waiting list serializer."""
        model = WaitingList
        fields = ['id', 'email', 'date_joined', 'is_registered']


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


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the user profile model."""

    class Meta:
        """Meta class for the user profile serializer."""
        model = Profile
        fields = [
            'id', 'account_type', 'user', 'phone_number', 'is_2fa_enabled',
            'streak_days'
        ]


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


class PreferencesSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the user preferences model."""

    class Meta:
        """Meta class for the user preferences serializer."""
        model = Preferences
        fields = [
            'id', 'user', 'email_notifications', 'sms_notifications',
            'language'
        ]


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


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the institution model."""

    class Meta:
        """Meta class for the institution serializer."""
        model = Institution
        fields = [
            'id', 'short_code', 'name', 'street_address', 'city', 'state',
            'postal_code', 'country', 'phone_number', 'contact_person'
        ]


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


class ClassSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the class model."""
    institution = serializers.HyperlinkedRelatedField(
        view_name='institution-detail', read_only=True)
    instructor = serializers.HyperlinkedRelatedField(
        view_name='profile-detail', read_only=True)

    class Meta:
        """Meta class for the class serializer."""
        model = Class
        fields = [
            'id', 'institution', 'short_code', 'long_name', 'short_name',
            'description', 'instructor'
        ]


class Enrollment(models.Model):
    """Enrollment model. 
        Represents a student's enrollment in a class."""

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"<Enrollment: {self.student.username} in {self.class_id.long_name}>"  # pylint: disable=no-member


class EnrollmentSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the enrollment model."""

    class Meta:
        """Meta class for the enrollment serializer."""
        model = Enrollment
        fields = ['id', 'student', 'class_id', 'date_enrolled']
