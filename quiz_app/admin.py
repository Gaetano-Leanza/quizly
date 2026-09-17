"""
Django admin configuration for the Quizly app.
Registers Quiz, Question, and Answer models to make them manageable via the Django admin interface.
"""

from django.contrib import admin
from .models import Quiz, Question, Answer

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)