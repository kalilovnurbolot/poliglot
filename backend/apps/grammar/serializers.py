from rest_framework import serializers

from .models import GrammarRule


class GrammarRuleSerializer(serializers.ModelSerializer):
    is_learned = serializers.SerializerMethodField()

    class Meta:
        model = GrammarRule
        fields = ['id', 'language', 'title', 'level', 'body', 'order', 'is_learned']

    def get_is_learned(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.progress_entries.filter(user=request.user).exists()
