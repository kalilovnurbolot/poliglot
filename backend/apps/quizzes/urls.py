from django.urls import path

from . import views

urlpatterns = [
    path('questions/', views.QuizQuestionsView.as_view(), name='quiz-questions'),
]
