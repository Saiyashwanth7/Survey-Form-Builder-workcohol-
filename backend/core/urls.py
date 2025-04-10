# core/urls.py
from django.contrib import admin
from django.urls import path, include
def index(request):
    return JsonResponse({"message": "Survey API is working!"})
urlpatterns = [
    path('/', index),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/surveys/', include('surveys.urls')),
]
