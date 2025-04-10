
# surveys/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.SurveyListCreateView.as_view(), name='survey-list-create'),
    path('<int:pk>/', views.SurveyDetailView.as_view(), name='survey-detail'),
    path('<int:pk>/responses/', views.SurveyResponsesView.as_view(), name='survey-responses'),
    path('<int:pk>/stats/', views.SurveyStatsView.as_view(), name='survey-stats'),
    path('responses/submit_response/', views.SubmitResponseView.as_view(), name='submit-response'),
    path('<int:pk>/stats/', views.SurveyStatsView.as_view(), name='survey-stats'),

]
