from django.urls import path

from . import views

app_name = 'web'

urlpatterns = [
    path('', views.home, name='home'),
    path('language/', views.set_language, name='set-language'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/google/', views.google_login, name='google-login'),

    path('learn/', views.learn, name='learn'),
    path('learn/<str:level>/', views.learn_session, name='learn-session'),
    path('quiz/', views.quiz, name='quiz'),
    path('voice/recognize/', views.voice_recognize, name='voice-recognize'),
    path('words/', views.words, name='words'),
    path('words/<int:pk>/delete/', views.word_delete, name='word-delete'),

    path('grammar/', views.grammar_list, name='grammar'),
    path('grammar/new/', views.grammar_create, name='grammar-create'),
    path('grammar/preview/', views.grammar_preview, name='grammar-preview'),
    path('grammar/<int:pk>/', views.grammar_detail, name='grammar-detail'),
    path('grammar/<int:pk>/edit/', views.grammar_edit, name='grammar-edit'),
    path('grammar/<int:pk>/delete/', views.grammar_delete, name='grammar-delete'),
    path('grammar/<int:pk>/toggle-learned/', views.grammar_toggle_learned, name='grammar-toggle-learned'),

    path('manifest.webmanifest', views.manifest, name='manifest'),
    path('sw.js', views.service_worker, name='service-worker'),
]
