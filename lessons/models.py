from enum import Enum

from django.core import serializers
from django.db import models

from accounts.models import Class, User


class ContentFormat(Enum):
    """Enumeration for lesson content formats."""
    VIDEO = 'video'
    AUDIO = 'audio'
    TEXT = 'text'
    IMAGE = 'image'
    PDF = 'pdf'


class Content(models.Model):
    """Content model.
        Represents a lesson content."""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    content_uri = models.TextField()  # cloud storage URI for the content file
    content_type = models.CharField(max_length=10,
                                    choices=[(tag, tag.value)
                                             for tag in ContentFormat])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Content: {self.title}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class Quiz(models.Model):
    """Quiz model.
        Represents a lesson quiz."""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<Quiz: {self.title}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class QuizQuestion(models.Model):
    """Quiz question model.
        Represents a question in a lesson quiz."""
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField()
    correct_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<QuizQuestion: {self.question}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])


class QuizProgress(models.Model):
    """Quiz progress model.
        Represents a student's progress in a lesson quiz."""
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField()

    def __str__(self):
        return f"<QuizProgress: {self.student.username} in {self.quiz.title}>"  # pylint: disable=no-member

    def serialize(self, output_format: str = 'json'):
        """Serialize the model instance to the specified format."""
        if output_format not in ['json', 'xml']:
            raise ValueError(f"Unsupported output format: {output_format}")
        return serializers.serialize(output_format, [self])
