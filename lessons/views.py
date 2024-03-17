"""
    Lesson views
    This module contains the views for the lessons app. 
"""

from django.db import IntegrityError
from rest_framework import exceptions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from lessons import models


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lessons_root(request):
    """List or create create lesson content.
    
    * `GET`: Returns the list of all lesson content.
    * `POST`: Creates new content. Requires staff permissions.
    """
    if request.method == 'GET':
        content = models.Content.objects.all()  # pylint: disable=no-member
        return Response(
            models.ContentSerializer(content,
                                     many=True,
                                     context={
                                         'request': request
                                     }).data)
    if request.method == 'POST':
        if request.user.is_staff:
            content = models.ContentSerializer(data=request.data)
            if content.is_valid():
                content.save()
                return Response(content.data, status=status.HTTP_201_CREATED)
            return Response(content.errors, status=status.HTTP_400_BAD_REQUEST)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")
    raise exceptions.MethodNotAllowed(request.method)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def lessons_detail(request, content_id: int):
    """/v1/lessons/<int:content_id>/
    
    * `GET`: Returns the content by id.
    * `PUT`: Updates content. Requires staff permissions.
    * `DELETE`: Deletes content. Requires staff permissions.
    """
    content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
    if not content:
        raise exceptions.NotFound("The requested content does not exist.")
    if request.method == 'GET':
        return Response(
            models.ContentSerializer(content, context={
                'request': request
            }).data)
    if request.method == 'PUT':
        if request.user.is_staff:
            content = models.ContentSerializer(content, data=request.data)
            if content.is_valid():
                content.save()
                return Response(content.data, status=status.HTTP_200_OK)
            raise exceptions.ValidationError(content.errors)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")
    if request.method == 'DELETE':
        if request.user.is_staff:
            content.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.PermissionDenied(
            "You do not have permission to perform this action.")
    raise exceptions.MethodNotAllowed(request.method)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lessons_detail_quizzes(request, content_id: int):
    """List or create quizzes for a content.
    
    * `GET`: Returns the list of quizzes for a content.
    * `POST`: Creates a new quiz. Requires staff permissions.
    """
    content = models.Content.objects.filter(id=content_id).first()  # pylint: disable=no-member
    if not content:
        raise exceptions.NotFound("The requested content does not exist.")
    if request.method == 'GET':
        quizzes = models.Quiz.objects.filter(content_id=content_id)  # pylint: disable=no-member
        return Response(
            models.QuizSerializer(quizzes,
                                  many=True,
                                  context={
                                      'request': request
                                  }).data)
    if request.method == 'POST':
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
    raise exceptions.MethodNotAllowed(request.method)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quizzes_root(request):
    """List all quizzes.
    
    * `GET`: Returns the list of all quizzes.
    """
    quizzes = models.Quiz.objects.all()  # pylint: disable=no-member
    return Response(
        models.QuizSerializer(quizzes, many=True, context={
            'request': request
        }).data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def manage_quizzes(request, quiz_id: int):
    """Retrieve, update or delete a quiz. 
    
    Requires staff permissions.
    
    * `GET`: Returns the quiz by id.
    * `PUT`: Updates a quiz.
    * `DELETE`: Deletes a quiz.
    """
    quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
    if not quiz:
        raise exceptions.NotFound("The requested quiz does not exist.")
    if request.method == 'GET':
        return Response(
            models.QuizSerializer(quiz, context={
                'request': request
            }).data)
    if request.method == 'PUT':
        quiz = models.QuizSerializer(quiz, data=request.data)
        if quiz.is_valid():
            quiz.save()
            return Response(quiz.data, status=status.HTTP_200_OK)
        raise exceptions.ValidationError(quiz.errors)
    if request.method == 'DELETE':
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    raise exceptions.MethodNotAllowed(request.method)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def manage_quiz_question(request, quiz_id: int, question_id: int):
    """Retrieve, update or delete a question.
    
    Requires staff permissions.
    
    * `GET`: Returns the question by id with correct answer.
    * `PUT`: Updates a question.
    * `DELETE`: Deletes a question.
    """
    question = models.QuizQuestion.objects.filter(id=question_id).first()  # pylint: disable=no-member
    if not question:
        raise exceptions.NotFound("The requested question does not exist.")
    if question.quiz != quiz_id:
        raise exceptions.NotFound("The requested question does not exist.")
    if request.method == 'GET':
        return Response(models.QuizQuestionSerializer(question).data)
    if request.method == 'PUT':
        question = models.QuizQuestionSerializer(question, data=request.data)
        if question.is_valid():
            question.save()
            return Response(question.data, status=status.HTTP_200_OK)
        raise exceptions.ValidationError(question.errors)
    if request.method == 'DELETE':
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    raise exceptions.MethodNotAllowed(request.method)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_quiz_questions(request, quiz_id: int):
    """Retrieve all questions for a quiz.
    
    * `GET`: Returns the list of questions for a quiz.
    """
    quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_quiz_detail(request, quiz_id: int, question_id: int):
    """Retrieve or submit a question.
    
    * `GET`: Returns the question by id with correct answer excluded.
    * `POST`: Submits an answer to a question.
    """
    quiz = models.Quiz.objects.filter(id=quiz_id).first()  # pylint: disable=no-member
    if not quiz:
        raise exceptions.NotFound("The requested quiz does not exist.")
    question = quiz.questions.filter(id=question_id).first()  # pylint: disable=no-member
    if not question:
        raise exceptions.NotFound("The requested question does not exist.")
    if request.method == 'GET':
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
    if request.method == 'POST':
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
        return Response(
            {
                'is_correct': is_correct,
                'score': response.score,
                "correct_index": question.correct_index
            },
            status=status.HTTP_201_CREATED)
    raise exceptions.MethodNotAllowed(request.method)
