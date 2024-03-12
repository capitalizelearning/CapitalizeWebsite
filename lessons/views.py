"""
    Lesson views
    This module contains the views for the lessons app.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from lessons.models import (Content, ContentSerializer, Quiz, QuizQuestion,
                            QuizQuestionSerializer, QuizSerializer)


class ContentView(APIView):
    """Content view."""
    authentication_classes = [authentication.JWTAuthentication]

    def get(self, _):
        """Returns the lesson content."""
        # TODO: filter only the user's registered classes
        content = Content.objects.all()  # pylint: disable=no-member
        return Response(ContentSerializer(content, many=True).data)

    def post(self, request):
        """Creates a new content. Requires staff permissions."""
        if not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to create content"},
                status=status.HTTP_403_FORBIDDEN)
        content = ContentSerializer(data=request.data)
        if content.is_valid():
            content.save()
            return Response(content.data, status=status.HTTP_201_CREATED)
        return Response(content.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizOverview(APIView):
    """Quiz overview."""
    authentication_classes = [authentication.JWTAuthentication]

    def get(self, request, pk: int):
        """Returns the quiz overview by id."""
        quiz = Quiz.objects.filter(id=pk).first()  # pylint: disable=no-member
        if not quiz:
            return Response({"error": "Quiz not found"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(
            QuizSerializer(quiz, context={
                'request': request
            }).data)


class StudentQuizView(APIView):
    """Quiz view for students. Handles quiz lifecycle."""
    authentication_classes = [authentication.JWTAuthentication]

    def get(self, _, quiz_pk: int, question_pk: int):
        """Returns the quiz question."""
        quiz = Quiz.objects.filter(id=quiz_pk).first()  # pylint: disable=no-member
        if not quiz:
            return Response({"error": "Quiz not found"},
                            status=status.HTTP_404_NOT_FOUND)
        question = QuizQuestion.objects.filter(id=question_pk).first()  # pylint: disable=no-member
        if not question:
            return Response({"error": "Question not found"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(QuizQuestionSerializer(question, ).data)

    def post(self, request, quiz_pk: int, question_pk: int):
        """ Submits the answer for the question."""
        quiz = Quiz.objects.filter(id=quiz_pk).first()  # pylint: disable=no-member
        if not quiz:
            return Response({"error": "Quiz not found"},
                            status=status.HTTP_404_NOT_FOUND)
        question = QuizQuestion.objects.filter(id=question_pk).first()  # pylint: disable=no-member
        if not question:
            return Response({"error": "Question not found"},
                            status=status.HTTP_404_NOT_FOUND)
        if not request.data.get('answer'):
            return Response({"error": "Answer not provided"},
                            status=status.HTTP_400_BAD_REQUEST)
        answer = request.data.get('answer')
        return Response({"isCorrect": question.check_answer(answer)})
