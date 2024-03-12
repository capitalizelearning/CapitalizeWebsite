"""
    Lesson views
    This module contains the views for the lessons app. 
"""

from rest_framework import exceptions, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from lessons import models


class ContentView(ViewSet):
    """Lesson content view

    - `list`: /v1/lessons/
    - `create`: /v1/lessons/
    - `retrieve`: /v1/lessons/<int:content_id>/
    - `update`: /v1/lessons/<int:content_id>/
    - `destroy`: /v1/lessons/<int:content_id>/
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Returns the list of all lesson content."""
        content = models.Content.objects.all()  # pylint: disable=no-member
        return Response(
            models.ContentSerializer(content,
                                     many=True,
                                     context={
                                         'request': request
                                     }).data)

    def create(self, request):
        """Creates new content. Requires staff permissions."""
        if request.user.is_staff:
            content = models.ContentSerializer(data=request.data)
            if content.is_valid():
                content.save()
                return Response(content.data, status=status.HTTP_201_CREATED)
            return Response(content.errors, status=status.HTTP_400_BAD_REQUEST)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")

    def retrieve(self, request, content_id: int):
        """Returns the content by id."""
        content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
        if not content:
            raise exceptions.NotFound("The requested content does not exist.")
        return Response(
            models.ContentSerializer(content, context={
                'request': request
            }).data)

    def update(self, request, content_id: int):
        """Updates content. Requires staff permissions."""
        if request.user.is_staff:
            content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
            if not content:
                raise exceptions.NotFound(
                    "The requested content does not exist.")
            content = models.ContentSerializer(content, data=request.data)
            if content.is_valid():
                content.save()
                return Response(content.data, status=status.HTTP_200_OK)
            raise exceptions.ValidationError(content.errors)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")

    def destroy(self, request, content_id: int):
        """Deletes content. Requires staff permissions."""
        if request.user.is_staff:
            content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
            if not content:
                raise exceptions.NotFound(
                    "The requested content does not exist.")
            content.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")


class LessonQuizzes(ViewSet):
    """Lesson quizzes view
    
    - `list`: /v1/lessons/<int:content_id>/quizzes/
    - `create`: /v1/lessons/<int:content_id>/quizzes/
    - `retrieve`: Returns the quiz overview by id.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, content_id: int):
        """Returns the list of quizzes for a content."""
        quizzes = models.Quiz.objects.filter(content_id=content_id)  # pylint: disable=no-member
        return Response(
            models.QuizSerializer(quizzes,
                                  many=True,
                                  context={
                                      'request': request
                                  }).data)

    def create(self, request, content_id: int):
        """Creates a new quiz. Requires staff permissions."""
        if request.user.is_staff:
            quiz = models.QuizSerializer(
                data={
                    **request.data, 'content_id': content_id
                })
            if quiz.is_valid():
                quiz.save()
                return Response(quiz.data, status=status.HTTP_201_CREATED)
            raise exceptions.ValidationError(quiz.errors)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")

    def retrieve(self, request, content_id: int, quiz_id: int):
        """Returns the quiz overview by id."""
        # pylint: disable=no-member
        quiz = models.Quiz.objects.filter(id=quiz_id,
                                          content_id=content_id).first()
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        return Response(
            models.QuizSerializer(quiz, context={
                'request': request
            }).data)


class ManageQuizzesView(ViewSet):
    """Quiz view for staff. 
    
    - `list`: /v1/lessons/quizzes/{quiz_id}/
    - `create`: /v1/lessons/quizzes/{quiz_id}/{question_id}/
    - `retrieve`: /v1/lessons/quizzes/{quiz_id}/{question_id}/
    """
    permission_classes = [IsAdminUser]

    def list(self, request, quiz_id: int):
        """Returns the list of questions for a quiz."""
        questions = models.QuizQuestion.objects.filter(quiz=quiz_id)  # pylint: disable=no-member
        if not questions:
            raise exceptions.NotFound("The requested quiz does not exist.")
        return Response(
            models.QuizQuestionSerializer(questions,
                                          many=True,
                                          context={
                                              'request': request
                                          }).data)

    def retrieve(self, request, quiz_id: int, question_id: int): # pylint: disable=unused-argument
        """Returns the question."""
        question = models.QuizQuestion.objects.filter(id=question_id).first()  # pylint: disable=no-member
        if not question:
            raise exceptions.NotFound("The requested question does not exist.")
        return Response(
            models.QuizQuestionSerializer(question,
                                          context={
                                              'request': request
                                          }).data)

    def create(self, request, quiz_id: int):
        """Creates a new question for a quiz."""
        quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        question = models.CreateQuizQuestionSerializer(data=request.data)
        if question.is_valid():
            question.save()
            return Response(question.data, status=status.HTTP_201_CREATED)
        raise exceptions.ValidationError(question.errors)


class StudentQuizView(APIView):
    """Quiz view for students. 
    
    - `get`: /v1/lessons/<int:content_id>/quizzes/<int:quiz_id>/questions/<int:question_id>/
    - `post`: /v1/lessons/<int:content_id>/quizzes/<int:quiz_id>/questions/<int:question_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id: int, question_id: int):  # pylint: disable=unused-argument
        """Returns the question."""
        quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        question = models.QuizQuestion.objects.filter(id=question_id).first()  # pylint: disable=no-member
        if not question:
            raise exceptions.NotFound("The requested question does not exist.")
        return Response(models.RestrictedQuizQuestionSerializer(question).data)

    def post(self, request, quiz_id: int, question_id: int):
        """Check the answer to a question."""
        quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        question = models.QuizQuestion.objects.filter(id=question_id).first()  # pylint: disable=no-member
        if not question:
            raise exceptions.NotFound("The requested question does not exist.")
        choice = request.data.get('answer')
        if not choice:
            raise exceptions.ValidationError("Answer not provided")
        return Response({"isCorrect": question.check_answer(int(choice))})
