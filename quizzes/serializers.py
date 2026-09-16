"""
Serializers for the Quizly app.
Handles the serialization of Quiz, Question, and Answer objects, including custom field mappings.
"""

from rest_framework import serializers
from .models import Quiz, Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for individual quiz questions.
    Maps question text and custom methods to retrieve options and the correct answer.
    """
    question_title = serializers.CharField(source='text', read_only=True)
    question_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']

    def get_question_options(self, obj):
        """
        Retrieves a list of text strings for all answer options associated with the question.
        """
        return [answer.text for answer in obj.answers.all()]

    def get_answer(self, obj):
        """
        Retrieves the text of the correct answer for the question.
        """
        correct_answer = obj.answers.filter(is_correct=True).first()
        return correct_answer.text if correct_answer else None


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for Quiz objects, including nested question details.
    """
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions',
        ]
