# surveys/serializers.py
from rest_framework import serializers
from .models import Survey, Question, Option, Response, Answer

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']



class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        for opt in options_data:
            Option.objects.create(question=question, **opt)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        instance.text = validated_data.get('text', instance.text)
        instance.question_type = validated_data.get('question_type', instance.question_type)
        instance.is_required = validated_data.get('is_required', instance.is_required)
        instance.order = validated_data.get('order', instance.order)
        instance.save()

        instance.options.all().delete()
        for opt in options_data:
            Option.objects.create(question=instance, **opt)

        return instance


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'is_public', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        owner = self.context['request'].user  # from the context

        # Remove 'owner' from validated_data if it exists
        validated_data.pop('owner', None)

        survey = Survey.objects.create(owner=owner, **validated_data)

        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(survey=survey, **question_data)
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)

        return survey


    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.is_public = validated_data.get('is_public', instance.is_public)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        instance.questions.all().delete()
        for q in questions_data:
            QuestionSerializer().create({**q, 'survey': instance})

        return instance


class AnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(many=True, queryset=Option.objects.all(), required=False)

    class Meta:
        model = Answer
        fields = ['question', 'selected_options', 'text_answer']


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'survey', 'user', 'submitted_at', 'answers']
        read_only_fields = ['user', 'submitted_at']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        response = Response.objects.create(user=user, **validated_data)
        for ans_data in answers_data:
            selected_options = ans_data.pop('selected_options', [])
            answer = Answer.objects.create(response=response, **ans_data)
            answer.selected_options.set(selected_options)
        return response
