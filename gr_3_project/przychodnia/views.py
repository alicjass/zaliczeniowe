from django.shortcuts import render, redirect
from django.http import HttpResponse
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def welcome_view(request):
    now = datetime.datetime.now()
    html = f"""
        <html><body>
        Witaj użytkowniku! </br>
        Aktualna data i czas na serwerze: {now}.
        </body></html>"""
    return HttpResponse(html)


# LOGOWANIE I WYLOGOWANIE UŻYTKOWNIKA
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect('/admin/')

            elif hasattr(user, 'weterynarz'):
                return redirect('welcome-view')

            elif hasattr(user, 'opiekun'):
                return redirect('welcome-view')

            else:
                return redirect('welcome-view')

            return redirect('welcome-view')
        else:
            return render(request, 'przychodnia/login.html', {'error': 'Nieprawidłowe dane'})
    return render(request, 'przychodnia/login.html')

def user_logout(request):
    logout(request)
    return redirect('user-login')


def drf_token_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            request.session['token'] = token.key
            request.session['user_id'] = user.id
            return redirect('welcome-view')
        else:
            return render(request, 'przychodnia/login.html', {'error': 'Nieprawidłowe dane'})
    return render(request, 'przychodnia/login.html')

def drf_token_logout(request):
    request.session.flush()
    return redirect('drf-token-login')