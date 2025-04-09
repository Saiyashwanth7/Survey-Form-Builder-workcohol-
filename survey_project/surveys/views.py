# surveys/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Survey, Question, QuestionOption, Response, Answer
from .serializers import (
    SurveySerializer, 
    QuestionSerializer, 
    QuestionOptionSerializer, 
    ResponseSerializer
)


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the creator
        return obj.creator == request.user


class SurveyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for surveys
    """
    queryset = Survey.objects.all().order_by('-created_at')
    serializer_class = SurveySerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter surveys to return only those created by the current user or all if listing"""
        user = self.request.user
        
        # For list action, return all active surveys
        if self.action == 'list':
            return Survey.objects.filter(is_active=True).order_by('-created_at')
            
        # For other actions by authenticated users
        if user.is_authenticated:
            if user.is_superuser:
                return Survey.objects.all().order_by('-created_at')
            # For detail views, allow seeing active surveys or own surveys
            if self.action == 'retrieve':
                return Survey.objects.filter(
                    Q(is_active=True) | Q(creator=user)
                ).order_by('-created_at')
            # For editing actions, only show own surveys
            return Survey.objects.filter(creator=user).order_by('-created_at')
            
        # For unauthenticated users on detail views
        return Survey.objects.filter(is_active=True).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a survey"""
        survey = self.get_object()
        
        # Check if user is the creator of the survey
        if request.user.is_authenticated and (survey.creator != request.user and not request.user.is_superuser):
            return DRFResponse(
                {"detail": "You do not have permission to view statistics for this survey."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        response_count = Response.objects.filter(survey=survey).count()
        
        # Get question completion rates
        questions = Question.objects.filter(survey=survey)
        question_stats = []
        
        for question in questions:
            answer_count = Answer.objects.filter(
                question=question, 
                response__survey=survey
            ).count()
            
            completion_rate = 0
            if response_count > 0:
                completion_rate = (answer_count / response_count) * 100
                
            question_stats.append({
                'id': question.id,
                'text': question.text,
                'type': question.question_type,
                'answers': answer_count,
                'completion_rate': completion_rate
            })
            
        return DRFResponse({
            'total_responses': response_count,
            'questions': question_stats
        })


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for questions
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter questions by survey if survey_id is provided"""
        survey_id = self.request.query_params.get('survey_id', None)
        if survey_id:
            return Question.objects.filter(survey__id=survey_id).order_by('order')
        return Question.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create a new question"""
        # Get survey from request data
        survey_id = request.data.get('survey')
        if not survey_id:
            return DRFResponse(
                {"survey": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            survey = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return DRFResponse(
                {"survey": ["Survey not found."]},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if user is the creator of the survey
        if request.user.is_authenticated and survey.creator != request.user and not request.user.is_superuser:
            return DRFResponse(
                {"detail": "You do not have permission to add questions to this survey."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(survey=survey)
        headers = self.get_success_headers(serializer.data)
        return DRFResponse(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class QuestionOptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for question options
    """
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter options by question if question_id is provided"""
        question_id = self.request.query_params.get('question_id', None)
        if question_id:
            return QuestionOption.objects.filter(question__id=question_id).order_by('order')
        return QuestionOption.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create a new question option"""
        # Get question from request data
        question_id = request.data.get('question')
        if not question_id:
            return DRFResponse(
                {"question": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return DRFResponse(
                {"question": ["Question not found."]},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if user is the creator of the survey
        if request.user.is_authenticated and question.survey.creator != request.user and not request.user.is_superuser:
            return DRFResponse(
                {"detail": "You do not have permission to add options to this question."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(question=question)
        headers = self.get_success_headers(serializer.data)
        return DRFResponse(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for survey responses
    """
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter responses by survey if survey_id is provided"""
        if not self.request.user.is_authenticated:
            return Response.objects.none()
            
        survey_id = self.request.query_params.get('survey_id', None)
        if survey_id:
            survey = get_object_or_404(Survey, id=survey_id)
            
            # Only allow the survey creator to view responses
            if self.request.user != survey.creator and not self.request.user.is_superuser:
                return Response.objects.none()
                
            return Response.objects.filter(survey__id=survey_id).order_by('-created_at')
            
        # Only superusers can view all responses
        if self.request.user.is_superuser:
            return Response.objects.all().order_by('-created_at')
            
        return Response.objects.filter(survey__creator=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new response"""
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Add IP to request data if it's mutable
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True
            request.data['ip_address'] = ip
            request.data._mutable = False
        else:
            # If using JSON data
            request.data['ip_address'] = ip
        
        return super().create(request, *args, **kwargs)