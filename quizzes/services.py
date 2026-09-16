"""
Utility functions for the Quizly AI pipeline.
Handles YouTube audio downloading via yt-dlp, local transcription via Whisper AI,
and structured quiz generation via Google Gemini Flash.
"""

import os
import json
import yt_dlp
import whisper
import google.generativeai as genai
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


def download_youtube_audio(youtube_url):
    """
    Downloads a YouTube video as an MP3 file and saves it temporarily in the media folder.
    Returns the file path to the downloaded audio file.
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
        print(f"Error during download: {e}")
        return None


def transcribe_audio(file_path):
    """
    Transcribes an audio file locally into text using OpenAI Whisper.
    Deletes the file afterward to save storage space.
    """
    if not file_path or not os.path.exists(file_path):
        return None

    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        os.remove(file_path)

        return result["text"]

    except Exception as e:
        print(f"Error during transcription: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return None


def generate_quiz_from_text(transcribed_text):
    """
    Takes the transcribed text, sends it to Gemini Flash, and returns a structured quiz.
    """
    if not transcribed_text:
        return None

    model = genai.GenerativeModel('gemini-3.6-flash')

    prompt = f"""
    Based on the following text, create a quiz with exactly 10 questions.
    Each question must have 4 answer options, with exactly one being correct.
    Return the result EXCLUSIVELY as a valid JSON array. No markdown formatting, no introductory text!
    
    Structure example:
    [
        {{
            "question": "What is the capital of France?",
            "options": ["Berlin", "Madrid", "Paris", "Rome"],
            "correct_answer": "Paris"
        }}
    ]
    
    Here is the text to analyze:
    {transcribed_text}
    """

    try:
        response = model.generate_content(prompt)
        clean_text = response.text.strip().removeprefix(
            "```json").removesuffix("```").strip()
        quiz_data = json.loads(clean_text)
        return quiz_data

    except Exception as e:
        print(f"Error during AI generation: {e}")
        return None
