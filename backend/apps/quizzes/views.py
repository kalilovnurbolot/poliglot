import random

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.vocabulary.models import UserWordProgress
from apps.vocabulary.queries import visible_words

from .serializers import QuizQuestionSerializer

OPTION_COUNT = 4


class QuizQuestionsView(APIView):
    """Multiple-choice questions: a word plus a shuffled list of translation
    options (one correct, the rest random distractors). Scoring happens on the
    client, which then reports the outcome through the existing
    /api/review/answer/ endpoint (right = correct, left = wrong) so quiz
    results feed straight into the same SRS progress as flashcards."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.query_params.get('language', 'en')
        level = request.query_params.get('level')
        limit = min(int(request.query_params.get('limit', 10)), 30)

        pool = list(visible_words(request.user, language, level))
        if len(pool) < OPTION_COUNT:
            return Response(
                {'detail': 'Недостаточно слов для квиза — сначала выучите ещё немного.'},
                status=400,
            )

        introduced_ids = set(
            UserWordProgress.objects.filter(user=request.user, word__in=pool)
            .values_list('word_id', flat=True)
        )
        introduced = [w for w in pool if w.id in introduced_ids]
        candidates = introduced if len(introduced) >= OPTION_COUNT else pool

        words = random.sample(candidates, k=min(limit, len(candidates)))

        questions = []
        for word in words:
            distractor_pool = [w for w in pool if w.id != word.id]
            distractors = random.sample(distractor_pool, k=min(OPTION_COUNT - 1, len(distractor_pool)))
            options = [word.translation] + [d.translation for d in distractors]
            random.shuffle(options)
            questions.append({'word': word, 'options': options})

        return Response(QuizQuestionSerializer(questions, many=True).data)
