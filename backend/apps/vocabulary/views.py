from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Deck, UserWordProgress, Word
from .permissions import IsOwnerOrReadOnly
from .queries import visible_words
from .serializers import (
    DeckSerializer, ProgressSerializer, ReviewCardSerializer, WordSerializer,
)
from .srs import SWIPE_DIRECTIONS, apply_swipe


class DeckViewSet(ModelViewSet):
    serializer_class = DeckSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Deck.objects.all()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(Q(owner__isnull=True) | Q(owner=user))
        else:
            queryset = queryset.filter(owner__isnull=True)

        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language__code=language)

        if self.request.query_params.get('mine') == 'true':
            queryset = queryset.filter(owner=user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReviewQueueView(APIView):
    """Words due for review right now, plus new words to fill up the batch."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.query_params.get('language', 'en')
        level = request.query_params.get('level')
        limit = min(int(request.query_params.get('limit', 20)), 50)
        words = visible_words(request.user, language, level)

        due_progress = list(
            UserWordProgress.objects.filter(
                user=request.user, word__in=words, next_review_at__lte=timezone.now(),
            )
            .select_related('word')
            .order_by('next_review_at')[:limit]
        )
        cards = [{'word': p.word, 'progress': p} for p in due_progress]

        remaining = limit - len(cards)
        if remaining > 0:
            new_words = (
                words.exclude(progress_entries__user=request.user)
                .order_by('text')[:remaining]
            )
            cards += [{'word': word, 'progress': None} for word in new_words]

        serializer = ReviewCardSerializer(cards, many=True)
        return Response(serializer.data)


class ReviewAnswerView(APIView):
    """Record the outcome of one swipe and update the word's SRS progress."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        word_id = request.data.get('word')
        direction = request.data.get('direction')
        if direction not in SWIPE_DIRECTIONS:
            raise ValidationError({'direction': f'must be one of {SWIPE_DIRECTIONS}'})

        word = get_object_or_404(Word, pk=word_id)
        if word.owner_id not in (None, request.user.id):
            raise PermissionDenied('Это слово вам недоступно.')

        progress, _ = UserWordProgress.objects.get_or_create(user=request.user, word=word)
        apply_swipe(progress, direction)
        progress.save()

        return Response(ProgressSerializer(progress).data)


class FavoriteWordsView(APIView):
    """Words the user swiped up on — a side collection for extra practice."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        words = Word.objects.filter(
            progress_entries__user=request.user, progress_entries__is_favorite=True,
        )
        return Response(WordSerializer(words, many=True).data)


class WordViewSet(ModelViewSet):
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Word.objects.all()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(Q(owner__isnull=True) | Q(owner=user))
        else:
            queryset = queryset.filter(owner__isnull=True)

        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language__code=language)

        deck = self.request.query_params.get('deck')
        if deck:
            queryset = queryset.filter(decks__id=deck)

        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)

        if self.request.query_params.get('mine') == 'true':
            queryset = queryset.filter(owner=user)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
