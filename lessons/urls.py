"""`lessons` App URL Configuration"""
from django.urls import path

import lessons.views as lessons_views

urlpatterns = [
    path("", lessons_views.lessons_root),
    path("<int:content_id>/", lessons_views.lessons_detail),
    path("<int:content_id>/quizzes/", lessons_views.lessons_detail_quizzes),
    path("manage/quizzes/<int:quiz_id>/", lessons_views.manage_quizzes),
    path("manage/quizzes/<int:quiz_id>/<int:question_id>/",
         lessons_views.manage_quiz_question),
    path("quizzes/<int:quiz_id>/<int:question_id>/",
         lessons_views.student_quiz_detail)
]
