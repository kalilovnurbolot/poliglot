from rest_framework import serializers

from apps.vocabulary.serializers import WordSerializer


class QuizQuestionSerializer(serializers.Serializer):
    word = WordSerializer()
    options = serializers.ListField(child=serializers.CharField())
