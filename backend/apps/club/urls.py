from django.urls import path

from . import views

app_name = 'club'

urlpatterns = [
    path('instagram/webhook/<str:key>/', views.instagram_webhook, name='instagram-webhook'),
]
