from django.urls import path, include
from . import views

urlpatterns = [
    path('welcome/', views.welcome_view, name = 'welcome-view'),
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='user-logout'),
    path('token/login/', views.drf_token_login, name='drf-token-login'),
    path('token/logout/', views.drf_token_logout, name='drf-token-logout'),
    path('weterynarz/wizyty/', views.weterynarz_wizyty, name='weterynarz-wizyty'),
    path('opiekun/wizyty/', views.opiekun_wizyty, name='opiekun-wizyty'),
]