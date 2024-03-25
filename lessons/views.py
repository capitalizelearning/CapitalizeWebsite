"""
    Lesson views
    This module contains the views for the lessons app. 
"""

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lessons import models


class LessonsRoot(APIView):
    """List or create create lesson content."""
    permission_classes = [IsAuthenticated]
    serializer_class = models.ContentSerializer

    @extend_schema(description="List lesson content.",
                   responses={200: models.ContentSerializer(many=True)})
    def get(self, request):
        """Returns the list of all lesson content."""
        content = models.Content.objects.all()  # pylint: disable=no-member
        return Response(
            models.ContentSerializer(content,
                                     many=True,
                                     context={
                                         'request': request
                                     }).data)

    @extend_schema(
        description="Create new lesson content. Requires staff permissions.",
        responses={201: models.ContentSerializer},
        request=models.CreateContentSerializer)
    def post(self, request):
        """Creates new content. Requires staff permissions."""
        if request.user.is_staff:
            content = models.CreateContentSerializer(data=request.data)
            if content.is_valid():
                content.save()
                return Response(content.data, status=status.HTTP_201_CREATED)
            return Response(content.errors, status=status.HTTP_400_BAD_REQUEST)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")


class LessonsDetail(APIView):
    """Retrieve, update or delete content."""
    permission_classes = [IsAdminUser]
    serializer_class = models.ContentSerializer

    @extend_schema(description="Retrieve lesson content by id.",
                   responses={200: models.ContentSerializer})
    def get(self, request, content_id: int):
        """Returns the content by id."""
        content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
        if not content:
            raise exceptions.NotFound("The requested content does not exist.")
        return Response(
            models.ContentSerializer(content, context={
                'request': request
            }).data)

    @extend_schema(description="Update lesson content by id.",
                   responses={200: models.ContentSerializer},
                   request=models.CreateContentSerializer)
    def put(self, request, content_id: int):
        """Updates content. Requires staff permissions."""
        if request.user.is_staff:
            content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
            content = models.CreateContentSerializer(content,
                                                     data=request.data)
            if content.is_valid():
                content.save()
                return Response(content.data, status=status.HTTP_200_OK)
            raise exceptions.ValidationError(content.errors)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")

    @extend_schema(description="Delete lesson content by id.",
                   responses={204: None})
    def delete(self, request, content_id: int):
        """Deletes content. Requires staff permissions."""
        if request.user.is_staff:
            content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
            content.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")


class LessonsDetailQuizzes(APIView):
    """List or create quizzes for a content."""
    permission_classes = [IsAuthenticated]
    serializer_class = models.QuizSerializer

    @extend_schema(description="List quizzes for a content.",
                   responses={200: models.QuizSerializer(many=True)})
    def get(self, request, content_id: int):
        """Returns the list of quizzes for a content."""
        content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
        if not content:
            raise exceptions.NotFound("The requested content does not exist.")
        quizzes = models.Quiz.objects.filter(content_id=content_id)  # pylint: disable=no-member
        return Response(
            models.QuizSerializer(quizzes,
                                  many=True,
                                  context={
                                      'request': request
                                  }).data)

    @extend_schema(description="Create new quiz. Requires staff permissions.",
                   responses={200: models.QuizSerializer},
                   request=models.CreateQuizSerializer)
    def post(self, request, content_id: int):
        """Creates a new quiz. Requires staff permissions."""
        content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
        if not content:
            raise exceptions.NotFound("The requested content does not exist.")
        if request.user.is_staff:
            quiz = models.CreateQuizSerializer(
                data={
                    **request.data, 'content_id': content_id
                })
            if quiz.is_valid():
                quiz.save()
                return Response(quiz.data, status=status.HTTP_200_OK)
            raise exceptions.ValidationError(quiz.errors)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")


class QuizzesRoot(APIView):
    """List all quizzes."""
    permission_classes = [IsAuthenticated]
    serializer_class = models.QuizSerializer

    @extend_schema(description="List all quizzes.",
                   responses={200: models.QuizSerializer(many=True)})
    def get(self, request):
        """Returns the list of all quizzes."""
        quizzes = models.Quiz.objects.all()  # pylint: disable=no-member
        return Response(
            models.QuizSerializer(quizzes,
                                  many=True,
                                  context={
                                      'request': request
                                  }).data)


class ManageQuizzes(APIView):
    """Retrieve, update or delete a quiz."""
    permission_classes = [IsAdminUser]
    serializer_class = models.QuizSerializer

    @extend_schema(description="Retrieve a quiz by id.",
                   responses={200: models.QuizSerializer})
    def get(self, request, quiz_id: int):
        """Returns the quiz by id."""
        quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        return Response(
            models.QuizSerializer(quiz, context={
                'request': request
            }).data)

    @extend_schema(description="Update a quiz by id.",
                   responses={200: models.QuizSerializer},
                   request=models.CreateQuizSerializer)
    def put(self, request, quiz_id: int):
        """Updates a quiz. Requires staff permissions."""
        quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        quiz = models.CreateQuizSerializer(quiz, data=request.data)
        if quiz.is_valid():
            quiz.save()
            return Response(quiz.data, status=status.HTTP_200_OK)
        raise exceptions.ValidationError(quiz.errors)

    @extend_schema(description="Delete a quiz by id.", responses={204: None})
    def delete(self, _, quiz_id: int):
        """Deletes a quiz. Requires staff permissions."""
        quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageQuizQuestions(APIView):
    """Retrieve, update or delete a question."""
    permission_classes = [IsAdminUser]
    serializer_class = models.QuizQuestionSerializer

    @extend_schema(description="Retrieve a question by id.",
                   responses={200: models.QuizQuestionSerializer})
    def get(self, _, quiz_id: int, question_id: int):
        """Returns the question by id with correct answer."""
        question = models.QuizQuestion.objects.filter(id=question_id).first()  # pylint: disable=no-member
        if not question:
            raise exceptions.NotFound("The requested question does not exist.")
        if question.quiz != quiz_id:
            raise exceptions.NotFound("The requested question does not exist.")
        return Response(models.QuizQuestionSerializer(question).data)

    @extend_schema(description="Updates a question.",
                   request=models.CreateQuizQuestionSerializer,
                   responses={200: models.QuizQuestionSerializer})
    def put(self, request, quiz_id: int, question_id: int):
        """Updates a question."""
        # pylint: disable=no-member
        question = models.QuizQuestion.objects.filter(id=question_id).first()
        if not question or question.quiz != quiz_id:
            raise exceptions.NotFound("The requested question does not exist.")
        question = models.CreateQuizQuestionSerializer(question,
                                                       data=request.data)
        if question.is_valid():
            question.save()
            return Response(question.data, status=status.HTTP_200_OK)
        raise exceptions.ValidationError(question.errors)

    @extend_schema(description="Deletes a question.", responses={204: None})
    def delete(self, _, quiz_id: int, question_id: int):
        """Deletes a question. Requires staff permissions."""
        question = models.QuizQuestion.objects.filter(id=question_id).first()  # pylint: disable=no-member
        if not question or question.quiz != quiz_id:
            raise exceptions.NotFound("The requested question does not exist.")
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentQuizQuestions(APIView):
    """Retrieve all questions for a quiz or submit a question."""
    permission_classes = [IsAuthenticated]
    serializer_class = models.RestrictedQuizQuestionSerializer

    @extend_schema(
        description="Retrieve all questions for a quiz.",
        responses={200: models.RestrictedQuizQuestionSerializer(many=True)})
    def get(self, request, quiz_id: int):
        """Returns the list of questions for a quiz."""
        # pylint: disable=no-member
        quiz = models.Quiz.objects.filter(id=quiz_id).first()
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        questions = quiz.questions.all()
        for question in questions:
            # pylint: disable=no-member
            response = models.QuizResponse.objects.filter(
                quiz=quiz, question=question, student=request.user).first()
            if response:
                question.response = response.score
        return Response(
            models.RestrictedQuizQuestionSerializer(questions,
                                                    many=True,
                                                    context={
                                                        'request': request
                                                    }).data)


class StudentQuizDetail(APIView):
    """Retrieve or submit a question."""
    permission_classes = [IsAuthenticated]
    serializer_class = models.QuizResponseSerializer

    @extend_schema(
        description="Retrieve a question by id with correct answer excluded.",
        responses={200: models.RestrictedQuizQuestionSerializer})
    def get(self, request, quiz_id: int, question_id: int):
        """Returns the question by id with correct answer excluded."""
        # pylint: disable=no-member
        quiz = models.Quiz.objects.filter(id=quiz_id).first()
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        question = quiz.questions.filter(id=question_id).first()
        if not question:
            raise exceptions.NotFound("The requested question does not exist.")
        # pylint: disable=no-member
        response = models.QuizResponse.objects.filter(
            quiz=quiz, question=question, student=request.user).first()
        if response:
            return Response(
                models.QuizResponseSerializer(response,
                                              context={
                                                  'request': request
                                              }).data)
        return Response(
            models.RestrictedQuizQuestionSerializer(question,
                                                    context={
                                                        'request': request
                                                    }).data)

    @extend_schema(description="Submits an answer to a question.",
                   request=models.QuizResponseSerializer,
                   responses={201: models.QuizResponseSerializer})
    def post(self, request, quiz_id: int, question_id: int):
        """Submits an answer to a question."""
        # pylint: disable=no-member
        quiz = models.Quiz.objects.filter(id=quiz_id).first()
        if not quiz:
            raise exceptions.NotFound("The requested quiz does not exist.")
        question = quiz.questions.filter(id=question_id).first()
        if not question:
            raise exceptions.NotFound("The requested question does not exist.")
        selected_answer = request.data.get('response')
        if selected_answer is None:
            raise exceptions.ValidationError(
                "The response field is required to submit an answer.")
        is_correct = question.check_answer(int(selected_answer))
        try:
            response = models.QuizResponse(quiz=quiz,
                                           question=question,
                                           score=int(is_correct *
                                                     question.weight),
                                           student=request.user)
            response.save()
        except IntegrityError as ie:
            raise exceptions.ValidationError(
                "You have already submitted a response to this question."
            ) from ie
        except Exception as e:
            print(e)
            raise exceptions.APIException(
                "An error occurred while processing your request.") from e
        return Response(models.QuizResponseSerializer(response,
                                                      context={
                                                          'request': request
                                                      }).data,
                        status=status.HTTP_201_CREATED)
