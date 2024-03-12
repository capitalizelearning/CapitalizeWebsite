"""
    Lesson models.
    Contains the models and serializer for lesson content and quizzes.
"""

import json
from enum import Enum
from typing import List

from django.db import models
from rest_framework import serializers

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


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the lesson content model."""

    class Meta:
        """Meta class for the lesson content serializer."""
        model = Content
        fields = [
            'id', 'title', 'description', 'content_uri', 'content_type',
            'created_at', 'updated_at'
        ]


class Quiz(models.Model):
    """Quiz model.
        Represents a lesson quiz."""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    class_id = models.ForeignKey(Class,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    content_id = models.ForeignKey(Content, on_delete=models.CASCADE)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def questions(self):
        """Returns the quiz questions."""
        return QuizQuestion.objects.filter(quiz=self)  # pylint: disable=no-member

    def __str__(self):
        return f"<Quiz: {self.title}>"  # pylint: disable=no-member


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

    def dump_options(self, options: List[str]):
        """Dumps the options list to a JSON field."""
        self.options = json.dumps(options)

    def check_answer(self, answer: int) -> bool:
        """Checks if the answer is correct."""
        print(answer, self.options[self.correct_index])
        return answer == self.correct_index


class QuizQuestionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the lesson quiz question model."""

    class Meta:
        """Meta class for the lesson quiz question serializer."""
        model = QuizQuestion
        fields = ['id', 'question', 'options', 'created_at']


class QuizSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the lesson quiz model."""
    content_id = serializers.PrimaryKeyRelatedField(
        queryset=Content.objects.all())  # pylint: disable=no-member
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # pylint: disable=no-member
    class_id = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())  # pylint: disable=no-member
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for the lesson quiz serializer."""
        model = Quiz
        fields = [
            'id', 'title', 'class_id', 'content_id', 'owner_id', 'description',
            'questions', 'created_at'
        ]


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


class QuizProgressSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the lesson quiz progress model."""

    class Meta:
        """Meta class for the lesson quiz progress serializer."""
        model = QuizProgress
        fields = [
            'id', 'quiz', 'student', 'score', 'is_completed', 'started_at',
            'completed_at'
        ]
