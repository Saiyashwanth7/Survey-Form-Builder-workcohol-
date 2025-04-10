# surveys/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Survey, Response as SurveyResponse
from .serializers import SurveySerializer, ResponseSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Survey
from django.shortcuts import get_object_or_404
class SurveyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        results = []

        for question in survey.questions.all():
            q_data = {
                "id": question.id,
                "text": question.text,
                "stats": []
            }

            if question.question_type in ["radio", "checkbox", "dropdown"]:
                for option in question.options.all():
                    count = question.answers.filter(selected_options__id=option.id).count()
                    q_data["stats"].append({
                        "option": option.text,
                        "count": count
                    })

            results.append(q_data)

        return Response({"questions": results})


class SurveyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = SurveySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Survey.objects.filter(owner=self.request.user)
        return Survey.objects.filter(is_public=True, is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = SurveySerializer


class SubmitResponseView(generics.CreateAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.AllowAny]


class SurveyResponsesView(generics.ListAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SurveyResponse.objects.filter(survey_id=self.kwargs['pk'])


class SurveyStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        total_responses = SurveyResponse.objects.filter(survey_id=pk).count()
        return Response({"total_responses": total_responses})
