"""
    Account models for the application.
    Contains account related models and their serializers.
"""
from enum import Enum
from secrets import token_urlsafe

from django.contrib.auth.models import User
from django.db import models
from django.db.utils import IntegrityError
from rest_framework import exceptions, serializers

from accounts.messaging import EmailService


class WaitingList(models.Model):
    """Waiting list model.
        Represents users who are waiting to create an account."""

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"<WaitingList: {self.id}>"


class CreateWaitingListSerializer(serializers.Serializer):
    """Serializer for adding a user to the waiting list."""

    email = serializers.EmailField()

    class Meta:
        """Meta class for the waiting list serializer."""
        model = WaitingList
        fields = ['id', 'email', 'date_joined']

    def create(self, validated_data):
        """Create and return a new WaitingList instance."""
        return WaitingList.objects.create(**validated_data)  # pylint: disable=no-member

    def update(self, instance, validated_data):
        """Update and return an existing WaitingList instance."""
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class WaitListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the waiting list model."""

    class Meta:
        """Meta class for the waiting list serializer."""
        model = WaitingList
        fields = ['id', 'email', 'date_joined', 'is_registered']


class ProfileType(Enum):
    """Enumeration for user profile types."""
    TESTER = 'tester'
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'


class Profile(models.Model):
    """User profile model. 
        Extends the default User model with additional fields through a one-to-one relationship."""

    id = models.AutoField(primary_key=True)
    account_type = models.CharField(max_length=10)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_token = models.CharField(max_length=255,
                                          unique=True,
                                          blank=True,
                                          null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    streak_days = models.IntegerField(default=0)

    def __init__(self, *args, set_token: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        if set_token:
            self.generate_registration_token()

    def __str__(self):
        return f"<Profile: {self.user.username}>"  # pylint: disable=no-member

    def generate_registration_token(self) -> str:
        """Generates a unique token for account activation."""
        token = token_urlsafe(128)
        # pylint: disable=no-member
        while Profile.objects.filter(registration_token=token).exists():
            token = token_urlsafe(128)
        self.registration_token = token
        return token

    @classmethod
    def get_user_by_activation_token(cls, token: str) -> User | None:
        """Get the user associated with the given activation token."""
        # pylint: disable=no-member
        profile = cls.objects.filter(registration_token=token).first()
        return profile.user if profile else None


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the user model."""

    class Meta:
        """Meta class for the user serializer."""
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class CreateTestUserSerializer(serializers.Serializer):
    """Serializer for creating a test user."""
    waiting_list_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    def create(self, validated_data):
        """Create and return a new User instance."""
        # pylint: disable=no-member
        wl = WaitingList.objects.get(id=validated_data['waiting_list_id'])
        if wl is None:
            raise ValueError("Invalid waiting list id")

        user: User = None
        profile: Profile = None
        try:
            user = User.objects.create_user(
                username=wl.email,
                email=wl.email,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
            )
            profile = Profile(user=user,
                              account_type=ProfileType.TESTER.value,
                              set_token=True)
            profile.save()
            EmailService().send_invite_email(user)
            wl.is_registered = True
            wl.save()
            return profile
        except IntegrityError as ie:
            raise exceptions.ValidationError("User already exists") from ie
        except Exception as e:
            print(e)
            if user.id:
                user.delete()
            if profile.id:
                profile.delete()
            raise exceptions.APIException(
                "An error occurred while creating the test user") from e

    def update(self, instance, validated_data):
        """Update and return an existing User instance."""
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.save()
        return instance


class RegistrationTokenSerializer(serializers.Serializer):
    """Serializer for the registration token."""
    registration_token = serializers.CharField(max_length=255)

    def create(self, validated_data):
        """Create and return a new User instance."""
        pass  # pylint: disable=unnecessary-pass

    def update(self, instance, validated_data):
        """Update and return an existing User instance."""
        pass  # pylint: disable=unnecessary-pass


class SetTestUserPasswordSerializer(serializers.Serializer):
    """Serializer for setting the password for a test user."""
    password = serializers.CharField(max_length=128, min_length=8)

    def create(self, validated_data):
        """Create and return a new User instance."""
        pass  # pylint: disable=unnecessary-pass

    def update(self, instance, validated_data):
        """Update and return an existing User instance."""
        pass  # pylint: disable=unnecessary-pass


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
