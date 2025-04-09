# surveys/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('short_text', 'Short Text'),
        ('long_text', 'Long Text'),
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating'),
        ('date', 'Date'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.text[:30]}... ({self.question_type})"
    
    class Meta:
        ordering = ['order']


class QuestionOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['order']


class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent_email = models.EmailField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to {self.survey.title} at {self.created_at}"


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text_answer = models.TextField(blank=True, null=True)
    selected_options = models.ManyToManyField(QuestionOption, blank=True, related_name='answers')
    
    def __str__(self):
        return f"Answer to: {self.question.text[:30]}..."