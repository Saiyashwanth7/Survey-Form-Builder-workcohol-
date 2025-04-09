# surveys/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'surveys', views.SurveyViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'options', views.QuestionOptionViewSet)
router.register(r'responses', views.ResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]