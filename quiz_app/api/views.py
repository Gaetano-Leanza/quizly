"""
API views for managing quizzes.
Provides CRUD operations and the automated AI quiz generation pipeline from YouTube videos.
"""

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
        Handles the creation of a new quiz by downloading a YouTube video,
        transcribing its audio, generating quiz questions via AI, and saving them.
        """
        youtube_url = request.data.get('url')

        if not youtube_url:
            return Response({"detail": "Invalid URL or request data."}, status=status.HTTP_400_BAD_REQUEST)

        audio_path = download_youtube_audio(youtube_url)
        if not audio_path:
            return Response({"detail": "Error downloading the video."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        transcribed_text = transcribe_audio(audio_path)
        if not transcribed_text:
            return Response({"detail": "Error during audio transcription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        quiz_data = generate_quiz_from_text(transcribed_text)
        if not quiz_data:
            return Response({"detail": "Error during AI generation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            quiz = Quiz.objects.create(
                user=request.user,
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

            serializer = self.get_serializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Database error: {e}")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
