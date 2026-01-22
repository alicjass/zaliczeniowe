from django.urls import path
from . import views

urlpatterns = [
    path('welcome/', views.welcome_view, name = 'welcome-view'),
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='user-logout'),
    path('wizyta/<int:pk>/', views.wizyta_detail, name='wizyta-detail'),
    path('wizyta/<int:pk>/zrealizuj_wizyte/', views.zrealizuj_wizyte, name='zrealizuj-wizyte'),
    path('wizyta/<int:pk>/odwolaj/', views.odwolaj_wizyte, name='odwolaj-wizyte'),
    path('opiekun/wizyty/', views.opiekun_wizyty, name='opiekun-wizyty'),
    path('opiekun/dodaj_wizyte/', views.dodaj_wizyte, name='dodaj-wizyte'),
    path('weterynarz/wizyty/', views.weterynarz_wizyty, name='weterynarz-wizyty'),
]