"""
Database models for the Quizly app.
Defines the structure for Quizzes, Questions, and Answers linked to users.
"""

from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """
    Represents a quiz created by a user, containing a YouTube video URL,
    title, description, and timestamps.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='quizzes')
    video_url = models.URLField()  
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Question(models.Model):
    """
    Represents a question associated with a specific quiz.
    """
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text


class Answer(models.Model):
    """
    Represents an answer option for a specific question, 
    indicating whether it is the correct choice or not.
    """
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text