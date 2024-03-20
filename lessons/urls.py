"""`lessons` App URL Configuration"""
from django.urls import path

import lessons.views as lessons_views

urlpatterns = [
    path("", lessons_views.LessonsRoot.as_view()),
    path("<int:content_id>/", lessons_views.LessonsDetail.as_view()),
    path("<int:content_id>/quizzes/",
         lessons_views.LessonsDetailQuizzes.as_view()),
    path("quizzes/", lessons_views.QuizzesRoot.as_view()),
    path("manage/quizzes/<int:quiz_id>/",
         lessons_views.ManageQuizzes.as_view()),
    path("manage/quizzes/<int:quiz_id>/<int:question_id>/",
         lessons_views.ManageQuizzes.as_view()),
    path("quizzes/<int:quiz_id>/", lessons_views.StudentQuizDetail.as_view()),
    path("quizzes/<int:quiz_id>/<int:question_id>/",
         lessons_views.StudentQuizDetail.as_view()),
]
