from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import GrammarProgress, GrammarRule
from .serializers import GrammarRuleSerializer


class GrammarRuleViewSet(ReadOnlyModelViewSet):
    serializer_class = GrammarRuleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = GrammarRule.objects.all()

        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language__code=language)

        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)

        return queryset

    @action(detail=True, methods=['post'], url_path='toggle-learned', permission_classes=[IsAuthenticated])
    def toggle_learned(self, request, pk=None):
        rule = self.get_object()
        progress, created = GrammarProgress.objects.get_or_create(user=request.user, rule=rule)
        if not created:
            progress.delete()
        return Response({'is_learned': created})
