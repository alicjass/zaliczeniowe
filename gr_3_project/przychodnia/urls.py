from django.urls import path, include
from . import views

urlpatterns = [
    path('welcome/', views.welcome_view),
]