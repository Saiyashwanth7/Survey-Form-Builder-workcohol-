# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def index(request):
    return JsonResponse({"message": "Survey API is working!"})
    
urlpatterns = [
    path('', lambda request: JsonResponse({"message": "Backend running"})),
    path('/', index),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/surveys/', include('surveys.urls')),
]
