from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('welcome/', views.welcome_view, name = 'welcome-view'),
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='user-logout'),
    path('user/profil/', views.user_profil, name='user-profil'),
    path('user/profil/edytuj/', views.edytuj_profil, name='edytuj-profil'),
    path('user/profil/zmien-haslo/', 
         auth_views.PasswordChangeView.as_view(
             template_name='przychodnia/user/zmien_haslo.html', 
             success_url='/przychodnia/user/profil/'
         ), 
         name='zmien-haslo'),
    path('wizyty/lista/', views.lista_wizyt, name='lista-wizyt'),
    path('wizyty/dzisiejsze/', views.dzisiejsze_wizyty, name='dzisiejsze-wizyty'),
    path('wizyty/historia/', views.historia_wizyt, name='historia-wizyt'),
    path('wizyty/<int:pk>/', views.wizyta_detail, name='wizyta-detail'),
    path('wizyty/dodaj/', views.dodaj_wizyte, name='dodaj-wizyte'),
    path('wizyty/<int:pk>/przeloz/', views.przeloz_wizyte, name='przeloz-wizyte'),
    path('wizyty/<int:pk>/odwolaj/', views.odwolaj_wizyte, name='odwolaj-wizyte'),
    path('wizyty/<int:pk>/zrealizuj/', views.zrealizuj_wizyte, name='zrealizuj-wizyte'),
    path('zwierzeta/lista/', views.lista_zwierzat, name='lista-zwierzat'),
    path('zwierzeta/<int:pk>/', views.zwierze_detail, name='zwierze-detail'),
    path('zwierzeta/<int:pk>/historia/', views.historia_zwierzaka, name='historia-zwierzaka'),
    path('zwierzeta/dodaj/', views.dodaj_zwierze, name='dodaj-zwierze'),
]