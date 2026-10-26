from django.urls import path

from . import admin_views, mission_views, views

app_name = 'web'

urlpatterns = [
    path('', views.home, name='home'),
    path('language/', views.set_language, name='set-language'),
    path('appearance/', views.appearance, name='appearance'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('reset/<str:uidb64>/<str:token>/', views.password_reset, name='password-reset'),
    path('auth/google/', views.google_login, name='google-login'),

    path('learn/', views.learn, name='learn'),
    path('learn/<str:level>/', views.learn_session, name='learn-session'),
    path('learn/group/<int:pk>/', views.learn_deck, name='learn-deck'),
    path('quiz/', views.quiz, name='quiz'),
    path('voice/recognize/', views.voice_recognize, name='voice-recognize'),
    path('missions/', mission_views.missions, name='missions'),
    path('missions/<int:pk>/', mission_views.mission_play, name='mission-play'),
    path('missions/<int:pk>/step/', mission_views.mission_step, name='mission-step'),
    path('missions/attempt/<int:pk>/', mission_views.mission_attempt, name='mission-attempt'),
    path('verbs/', views.verbs, name='verbs'),
    path('verbs/play/', views.verbs_play, name='verbs-play'),
    path('dictionary/', views.dictionary, name='dictionary'),
    path('words/', views.words, name='words'),
    path('words/list/', views.words_list, name='words-list'),
    path('words/<int:pk>/delete/', views.word_delete, name='word-delete'),
    path('words/groups/new/', views.group_create, name='group-create'),

    path('grammar/', views.grammar_list, name='grammar'),
    path('grammar/new/', views.grammar_create, name='grammar-create'),
    path('grammar/preview/', views.grammar_preview, name='grammar-preview'),
    path('grammar/<int:pk>/', views.grammar_detail, name='grammar-detail'),
    path('grammar/<int:pk>/edit/', views.grammar_edit, name='grammar-edit'),
    path('grammar/<int:pk>/delete/', views.grammar_delete, name='grammar-delete'),
    path('grammar/<int:pk>/toggle-learned/', views.grammar_toggle_learned, name='grammar-toggle-learned'),

    path('manage/users/', admin_views.users, name='manage-users'),
    path('manage/users/<int:pk>/reset-link/', admin_views.user_reset_link, name='manage-user-reset-link'),
    path('manage/users/<int:pk>/<str:action>/', admin_views.user_action, name='manage-user-action'),
    path('manage/log/', admin_views.activity, name='manage-log'),
    path('manage/database/', admin_views.database, name='manage-database'),
    path('manage/database/backup/', admin_views.database_backup, name='manage-database-backup'),
    path('manage/database/upload/', admin_views.database_upload, name='manage-database-upload'),
    path('manage/database/<str:name>/restore/', admin_views.database_restore, name='manage-database-restore'),
    path('manage/database/<str:name>/download/', admin_views.database_download, name='manage-database-download'),

    path('manifest.webmanifest', views.manifest, name='manifest'),
    path('sw.js', views.service_worker, name='service-worker'),
]
