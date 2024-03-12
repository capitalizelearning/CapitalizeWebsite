"""`lessons` App URL Configuration"""
from django.urls import path

import lessons.views as lessons_views

urlpatterns = [
    path("",
         lessons_views.ContentView.as_view({
             "get": "list",
             "post": "create"
         }),
         name="content-root"),
    path("<int:content_id>/",
         lessons_views.ContentView.as_view({
             "get": "retrieve",
             "put": "update",
             "delete": "destroy"
         }),
         name="content-detail"),
    path("<int:content_id>/quizzes/",
         lessons_views.LessonQuizzes.as_view({
             "get": "list",
             "post": "create"
         }),
         name="content-quizzes"),
    path("<int:content_id>/quizzes/<int:quiz_id>/",
         lessons_views.LessonQuizzes.as_view({
             "get": "retrieve",
         }),
         name="content-quiz-detail"),
    path("quizzes/manage/<int:quiz_id>/",
         lessons_views.ManageQuizzesView.as_view({
             "get": "list",
             "post": "create"
         }),
         name="quiz-questions"),
    path("quizzes/manage/<int:quiz_id>/<int:question_id>/",
         lessons_views.ManageQuizzesView.as_view({
             "get": "retrieve",
         }),
         name="quiz-question-detail"),
    path("quizzes/<int:quiz_id>/<int:question_id>/",
         lessons_views.StudentQuizView.as_view(),
         name="student-quiz-detail"),
]
