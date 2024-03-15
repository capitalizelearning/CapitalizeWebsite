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


# Model Definitions
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

    @property
    def quiz_id_list(self):
        """Returns the list of quiz ids for the content."""
        return [quiz.id for quiz in self.quiz_set.all()]  # pylint: disable=no-member

    def get_quiz_list(self):
        """Returns the list of quizzes for the content."""
        return set(self.quiz_id_list)  # pylint: disable=no-member

    def __str__(self):
        return f"<Content: {self.title}>"  # pylint: disable=no-member


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
    weight = models.IntegerField(null=False, default=1)
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
        return answer == self.correct_index


class QuizResponse(models.Model):
    """Quiz response model.
        Represents a student's response to a quiz question."""
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    responses = models.ManyToManyField(QuizQuestion, related_name='responses')

    def __str__(self):
        return f"<QuizResponse: {self.id}>"  # pylint: disable=no-member

    class Meta:
        """Constrain the QuizResponse to be unique for each student, quiz and question."""
        unique_together = ['quiz', 'question', 'student']


# Serializers Definitions
class ContentSerializer(serializers.ModelSerializer):
    """Serializer for the lesson content model."""

    class Meta:
        """Content serializer meta class."""
        model = Content
        fields = [
            'id', 'title', 'description', 'content_uri', 'content_type',
            'created_at', 'updated_at', 'quiz_id_list'
        ]


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for the lesson quiz model."""

    def get_question_list(self, obj):
        """Returns the list of questions for the quiz."""
        return RestrictedQuizQuestionSerializer(obj.questions, many=True).data

    question_list = serializers.SerializerMethodField()

    class Meta:
        """Quiz serializer meta class."""
        model = Quiz
        fields = '__all__'


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for the lesson quiz question model. Includes the correct answer."""

    def get_responses(self, obj):
        """Returns the list of responses for the question."""
        return [response.id for response in obj.responses.all()]  # pylint: disable=no-member

    responses = serializers.SerializerMethodField()

    class Meta:
        """Quiz question serializer meta class."""
        model = QuizQuestion
        fields = [
            'id', 'quiz', 'question', 'options', 'weight', 'correct_index',
            'responses'
        ]


class RestrictedQuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for the lesson quiz question model. Excludes the correct answer."""

    class Meta:
        """Restricted quiz question serializer meta class."""
        model = QuizQuestion
        fields = ['id', 'quiz', 'question', 'options', 'weight']


class CreateQuizQuestionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for creating a lesson quiz question."""
    quiz_id = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())  # pylint: disable=no-member

    class Meta:
        """Meta class for the lesson quiz question serializer."""
        model = QuizQuestion
        fields = ['id', 'quiz_id', 'question', 'options', 'correct_index']


class QuizResponseSerializer(serializers.ModelSerializer):
    """Serializer for the lesson quiz response model."""

    class Meta:
        """Quiz response serializer meta class."""
        model = QuizResponse
        fields = '__all__'
