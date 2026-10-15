from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .questions import NotEnoughWords, build_questions
from .serializers import QuizQuestionSerializer


class QuizQuestionsView(APIView):
    """Scoring happens on the client, which then reports the outcome through the
    existing /api/review/answer/ endpoint (right = correct, left = wrong) so quiz
    results feed straight into the same SRS progress as flashcards."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.query_params.get('language', 'en')
        level = request.query_params.get('level')
        limit = min(int(request.query_params.get('limit', 10)), 30)

        try:
            questions = build_questions(request.user, language, level, limit)
        except NotEnoughWords as e:
            return Response({'detail': str(e)}, status=400)

        return Response(QuizQuestionSerializer(questions, many=True).data)
