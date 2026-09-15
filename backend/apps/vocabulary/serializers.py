from rest_framework import serializers

from .models import Deck, UserWordProgress, Word


class DeckSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Deck
        fields = ['id', 'language', 'owner', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWordProgress
        fields = [
            'box_level', 'next_review_at', 'correct_count',
            'wrong_count', 'last_result', 'is_favorite',
        ]


class WordSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Word
        fields = [
            'id', 'language', 'owner', 'decks', 'text', 'translation',
            'transcription', 'example_sentence', 'part_of_speech', 'level', 'created_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at']


class ReviewCardSerializer(serializers.Serializer):
    word = WordSerializer()
    progress = ProgressSerializer(allow_null=True)
