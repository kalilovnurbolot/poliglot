from django.urls import path

from . import admin_views, mission_views, teach_views, views

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

    path('teach/', teach_views.teach, name='teach'),
    path('teach/sessions/new/', teach_views.session_create, name='teach-session-create'),
    path('teach/sessions/<int:pk>/', teach_views.session_detail, name='teach-session'),
    path('teach/sessions/<int:pk>/edit/', teach_views.session_edit, name='teach-session-edit'),
    path('teach/sessions/<int:pk>/delete/', teach_views.session_delete, name='teach-session-delete'),
    path('teach/bookings/<int:pk>/<str:action>/', teach_views.booking_action, name='teach-booking-action'),
    path('teach/bot/', teach_views.bot_settings, name='teach-bot'),
    path('teach/bot/payment-qr/', teach_views.bot_payment_qr, name='teach-bot-payment-qr'),
    path('teach/bot/disconnect/', teach_views.bot_disconnect, name='teach-bot-disconnect'),
    path('club/ticket/<str:token>/', teach_views.ticket, name='club-ticket'),
    path('club/payment-qr/<int:pk>/', teach_views.payment_qr, name='club-payment-qr'),
    path('club/ticket/<str:token>/qr.png', teach_views.ticket_qr, name='club-ticket-qr'),

    path('manage/users/', admin_views.users, name='manage-users'),
    path('manage/users/<int:pk>/reset-link/', admin_views.user_reset_link, name='manage-user-reset-link'),
    path('manage/users/<int:pk>/<str:action>/', admin_views.user_action, name='manage-user-action'),
    path('manage/settings/', admin_views.site_settings, name='manage-settings'),
    path('manage/log/', admin_views.activity, name='manage-log'),
    path('manage/database/', admin_views.database, name='manage-database'),
    path('manage/database/backup/', admin_views.database_backup, name='manage-database-backup'),
    path('manage/database/upload/', admin_views.database_upload, name='manage-database-upload'),
    path('manage/database/<str:name>/restore/', admin_views.database_restore, name='manage-database-restore'),
    path('manage/database/<str:name>/download/', admin_views.database_download, name='manage-database-download'),

    path('manifest.webmanifest', views.manifest, name='manifest'),
    path('sw.js', views.service_worker, name='service-worker'),
]
