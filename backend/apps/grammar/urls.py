from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('grammar-rules', views.GrammarRuleViewSet, basename='grammar-rule')

urlpatterns = router.urls
