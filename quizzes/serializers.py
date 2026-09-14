from rest_framework import serializers
from .models import Quiz, Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    question_title = serializers.CharField(source='text', read_only=True)
    question_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']

    def get_question_options(self, obj):
        return [answer.text for answer in obj.answer_set.all()]

    def get_answer(self, obj):
        correct_answer = obj.answer_set.filter(is_correct=True).first()
        return correct_answer.text if correct_answer else None


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(
        source='question_set', many=True, read_only=True)

    class Meta:
        model = Quiz

        fields = ['id', 'title', 'description', 'created_at',
                  'updated_at', 'video_url', 'questions']
