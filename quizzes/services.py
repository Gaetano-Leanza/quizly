import os
import json
import yt_dlp
import whisper
import google.generativeai as genai
from django.conf import settings
from dotenv import load_dotenv

# Lädt den API-Key aus deiner .env Datei
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


def download_youtube_audio(youtube_url):
    """
    Lädt ein YouTube-Video als mp3 herunter und speichert es temporär im media-Ordner.
    Gibt den Dateipfad zur heruntergeladenen Datei zurück.
    """
    output_path = os.path.join(
        settings.BASE_DIR, 'media', 'temp_audio.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            mp3_filename = filename.rsplit('.', 1)[0] + '.mp3'

            return mp3_filename
    except Exception as e:
        print(f"Fehler beim Download: {e}")
        return None


def transcribe_audio(file_path):
    """
    Transkribiert eine Audio-Datei lokal mit OpenAI Whisper in Text.
    Löscht die Datei anschließend, um Speicherplatz zu sparen.
    """
    if not file_path or not os.path.exists(file_path):
        return None

    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        os.remove(file_path)

        return result["text"]

    except Exception as e:
        print(f"Fehler bei der Transkription: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return None


def generate_quiz_from_text(transcribed_text):
    """
    Nimmt den Text, sendet ihn an Gemini Flash und gibt ein strukturiertes Quiz zurück.
    """
    if not transcribed_text:
        return None

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Erstelle basierend auf dem folgenden Text ein Quiz mit exakt 10 Fragen.
    Jede Frage muss 4 Antwortmöglichkeiten haben, von denen genau eine richtig ist.
    Gib das Ergebnis AUSSCHLIESSLICH als valides JSON-Array zurück. Keine Markdown-Formatierung, kein Begrüßungstext!
    
    Struktur-Beispiel:
    [
        {{
            "question": "Wie heißt die Hauptstadt von Frankreich?",
            "options": ["Berlin", "Madrid", "Paris", "Rom"],
            "correct_answer": "Paris"
        }}
    ]
    
    Hier ist der zu analysierende Text:
    {transcribed_text}
    """

    try:
        response = model.generate_content(prompt)
        clean_text = response.text.strip().removeprefix(
            "```json").removesuffix("```").strip()
        quiz_data = json.loads(clean_text)
        return quiz_data

    except Exception as e:
        print(f"Fehler bei der KI-Generierung: {e}")
        return None
