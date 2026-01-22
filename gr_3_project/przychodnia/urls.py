from django.urls import path
from . import views

urlpatterns = [
    path('welcome/', views.welcome_view, name = 'welcome-view'),
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='user-logout'),
    path('opiekun/wizyty/', views.opiekun_wizyty, name='opiekun-wizyty'),
    path('weterynarz/wizyty/', views.weterynarz_wizyty, name='weterynarz-wizyty'),
    path('wizyta/<int:pk>/', views.wizyta_detail, name='wizyta-detail'),
]