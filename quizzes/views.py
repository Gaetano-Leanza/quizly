from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer
from .services import download_youtube_audio, transcribe_audio, generate_quiz_from_text


class IsOwner(permissions.BasePermission):
    message = "Zugriff verweigert - Quiz gehört nicht dem Benutzer."

    def has_object_permission(self, request, view, obj):

        return obj.user == request.user


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):

        if self.action == 'list':
            return Quiz.objects.filter(user=self.request.user)

        return Quiz.objects.all()

    def create(self, request, *args, **kwargs):
        youtube_url = request.data.get('url')

        if not youtube_url:
            return Response({"detail": "Ungültige URL oder Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST)

        audio_path = download_youtube_audio(youtube_url)
        if not audio_path:
            return Response({"detail": "Fehler beim Herunterladen des Videos."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        transcribed_text = transcribe_audio(audio_path)
        if not transcribed_text:
            return Response({"detail": "Fehler bei der Audio-Transkription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        quiz_data = generate_quiz_from_text(transcribed_text)
        if not quiz_data:
            return Response({"detail": "Fehler bei der KI-Generierung."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            quiz = Quiz.objects.create(
                user=request.user,
                title="Neu generiertes KI-Quiz",
                description="Automatisch generiertes Quiz aus YouTube-Video.",
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
            print(f"Datenbank-Fehler: {e}")
            return Response({"detail": "Interner Serverfehler."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
