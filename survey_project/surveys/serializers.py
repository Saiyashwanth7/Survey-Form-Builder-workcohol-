# surveys/serializers.py
from rest_framework import serializers
from .models import Survey, Question, QuestionOption, Response, Answer


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    survey = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'survey', 'text', 'question_type', 'required', 'order', 'options']


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator_name = serializers.ReadOnlyField(source='creator.username')
    creator = serializers.PrimaryKeyRelatedField(
        read_only=True, 
        default=serializers.CurrentUserDefault()
    )
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'creator', 'creator_name', 
                  'created_at', 'updated_at', 'is_active', 'questions']
        read_only_fields = ['creator', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Make sure the request exists and user is authenticated
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['creator'] = request.user
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text_answer', 'selected_options']


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    
    class Meta:
        model = Response
        fields = ['id', 'survey', 'respondent_email', 'ip_address', 'created_at', 'answers']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        response = Response.objects.create(**validated_data)
        
        for answer_data in answers_data:
            selected_options = answer_data.pop('selected_options', [])
            answer = Answer.objects.create(response=response, **answer_data)
            answer.selected_options.set(selected_options)
            
        return response