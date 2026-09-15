from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('refresh/', views.TokenRefreshView.as_view(), name='auth-refresh'),
    path('google/', views.GoogleLoginView.as_view(), name='auth-google'),
    path('me/', views.MeView.as_view(), name='auth-me'),
]
