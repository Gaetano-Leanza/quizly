from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Question, Answer
from .services import download_youtube_audio, transcribe_audio, generate_quiz_from_text


class GenerateQuizView(APIView):
    def post(self, request):
        youtube_url = request.data.get('youtube_url')

        if not youtube_url:
            return Response({"error": "Bitte eine YouTube URL übergeben."}, status=status.HTTP_400_BAD_REQUEST)

        audio_path = download_youtube_audio(youtube_url)
        if not audio_path:
            return Response({"error": "Fehler beim Herunterladen des Videos."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        transcribed_text = transcribe_audio(audio_path)
        if not transcribed_text:
            return Response({"error": "Fehler bei der Audio-Transkription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        quiz_data = generate_quiz_from_text(transcribed_text)
        if not quiz_data:
            return Response({"error": "Fehler bei der KI-Generierung."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:

            quiz = Quiz.objects.create(
                title="Neu generiertes KI-Quiz",

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

            return Response({"message": "Quiz erfolgreich generiert!", "quiz_id": quiz.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Datenbank-Fehler: {e}")
            return Response({"error": "Fehler beim Speichern in der Datenbank."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
