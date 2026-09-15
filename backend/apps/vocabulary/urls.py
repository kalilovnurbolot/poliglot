from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('decks', views.DeckViewSet, basename='deck')
router.register('words', views.WordViewSet, basename='word')

urlpatterns = [
    path('review/queue/', views.ReviewQueueView.as_view(), name='review-queue'),
    path('review/answer/', views.ReviewAnswerView.as_view(), name='review-answer'),
    path('review/favorites/', views.FavoriteWordsView.as_view(), name='review-favorites'),
] + router.urls
