"""
API views for managing quizzes.
Provides CRUD operations and the automated AI quiz generation pipeline from YouTube videos.
"""

import re
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Quiz, Question, Answer
from .serializers import QuizSerializer
from .services import download_youtube_audio, transcribe_audio, generate_quiz_from_text


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a quiz to access or modify it.
    """
    message = "Access denied - Quiz does not belong to the user."

    def has_object_permission(self, request, view, obj):
        """
        Checks if the request user matches the owner of the quiz object.
        """
        return obj.user == request.user


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing, creating, updating, and deleting quizzes.
    Integrates the full AI generation pipeline for new quiz creation.
    """
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Restricts the queryset to quizzes owned by the authenticated user 
        when fetching the list view.
        """
        if self.action == 'list':
            return Quiz.objects.filter(user=self.request.user)

        return Quiz.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new quiz. Delegates the heavy lifting 
        to helper methods for processing and database saving.
        """
        youtube_url = request.data.get('url')

        if not youtube_url:
            return Response({"detail": "Invalid URL or request data."}, status=status.HTTP_400_BAD_REQUEST)

        match = re.search(r'(?:youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\/shorts\/)([a-zA-Z0-9_-]{11})', youtube_url)
        if match:
            youtube_url = f"https://www.youtube.com/watch?v={match.group(1)}"

        quiz_data = self._process_quiz_pipeline(youtube_url)
        
        if isinstance(quiz_data, Response):
            return quiz_data

        try:
            quiz = self._save_quiz_data(request.user, youtube_url, quiz_data)
            serializer = self.get_serializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({"detail": "Internal server error during database save."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_quiz_pipeline(self, youtube_url):
        """
        Helper method to run the external AI pipeline.
        Returns the quiz_data list or a 400 Response object on error.
        """
        audio_path = download_youtube_audio(youtube_url)
        if not audio_path:
            return Response({"detail": "Error downloading the video. Please check the URL."}, status=status.HTTP_400_BAD_REQUEST)

        transcribed_text = transcribe_audio(audio_path)
        if not transcribed_text:
            return Response({"detail": "Error during audio transcription."}, status=status.HTTP_400_BAD_REQUEST)

        quiz_data = generate_quiz_from_text(transcribed_text)
        if not quiz_data:
            return Response({"detail": "Error during AI generation."}, status=status.HTTP_400_BAD_REQUEST)

        return quiz_data

    def _save_quiz_data(self, user, youtube_url, quiz_data):
        """
        Helper method to save the generated quiz, questions, and answers to the database.
        """
        quiz = Quiz.objects.create(
            user=user,
            title="Newly generated AI quiz",
            description="Automatically generated quiz from YouTube video.",
            video_url=youtube_url
        )

        for item in quiz_data:
            question = Question.objects.create(
                quiz=quiz,
                text=item['question']
            )

            for option in item['options']:
                is_correct = (option == item['correct_answer'])
                Answer.objects.create(
                    question=question,
                    text=option,
                    is_correct=is_correct
                )
        
        return quiz