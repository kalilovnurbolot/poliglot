from django.db.models import Max
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import GrammarProgress, GrammarRule
from .serializers import GrammarRuleSerializer


class IsAdminOrReadOnly(BasePermission):
    """Rules are shared by everyone; only staff can add, edit or delete them."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff


class GrammarRuleViewSet(ModelViewSet):
    serializer_class = GrammarRuleSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = GrammarRule.objects.all()

        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language__code=language)

        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)

        return queryset

    def perform_create(self, serializer):
        # New rules go to the end of their level instead of jumping ahead of the system ones.
        last_order = GrammarRule.objects.filter(
            language=serializer.validated_data['language'],
            level=serializer.validated_data.get('level', 'A1'),
        ).aggregate(Max('order'))['order__max'] or 0
        serializer.save(order=last_order + 1)

    @action(detail=True, methods=['post'], url_path='toggle-learned', permission_classes=[IsAuthenticated])
    def toggle_learned(self, request, pk=None):
        rule = self.get_object()
        progress, created = GrammarProgress.objects.get_or_create(user=request.user, rule=rule)
        if not created:
            progress.delete()
        return Response({'is_learned': created})
