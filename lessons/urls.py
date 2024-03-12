"""`lessons` App URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

import lessons.views as lessons_views

urlpatterns = [
    path('lessons/', lessons_views.ContentView.as_view(), name='content'),
    path('lessons/quiz/<int:pk>',
         lessons_views.QuizOverview.as_view(),
         name='quiz_overview'),
    path('lessons/quiz/<int:quiz_pk>/<int:question_pk>',
         lessons_views.StudentQuizView.as_view(),
         name='student_quiz'),
]
