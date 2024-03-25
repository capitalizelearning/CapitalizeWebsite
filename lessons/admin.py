from django.contrib import admin

from .models import Content, Quiz, QuizQuestion, QuizResponse

admin.site.register(Content)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizResponse)
