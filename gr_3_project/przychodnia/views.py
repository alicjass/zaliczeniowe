from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Opiekun, Zwierze, Weterynarz, Wizyta, STATUS_WIZYTA
from .forms import ZwierzeForm, WizytaForm, NotatkaForm
from datetime import date, datetime


# WELCOME VIEW
def welcome_view(request):
    now = datetime.datetime.now()
    html = f"""
        <html><body>
        Witaj użytkowniku! </br>
        Aktualna data i czas na serwerze: {now}.
        </body></html>"""
    return HttpResponse(html)


# LOGOWANIE/WYLOGOWANIE UŻYTKOWNIKA
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect('/admin/')

            elif hasattr(user, 'weterynarz') or hasattr(user, 'opiekun'):
                return redirect('lista-wizyt')

        else:
            return render(request, 'przychodnia/login.html', {'error': 'Nieprawidłowe dane'})
    
    return render(request, 'przychodnia/login.html')

def user_logout(request):
    logout(request)
    return redirect('user-login')


# LISTA WIZYT DLA OPIEKUNA/WETERYNARZA
@login_required
def lista_wizyt(request):
    user = request.user

    if hasattr(user, "opiekun"):
        wizyty = Wizyta.objects.filter(
            zwierze__opiekun=user.opiekun,
            data_wizyty__gte=date.today()  # wyswietlamy tylko wizyty dzisiejsze i przyszłe
        )

    elif hasattr(user, "weterynarz"):
        wizyty = Wizyta.objects.filter(
            weterynarz=user.weterynarz,
            data_wizyty__gte=date.today()
        )

    else:
        return HttpResponseForbidden()
    
    return render(request, 'przychodnia/wizyty/lista_wizyt.html', {'wizyty': wizyty})


# SZCZEGÓŁY WIZYTY
@login_required
def wizyta_detail(request, pk):
    user = request.user
    
    try:
        wizyta = Wizyta.objects.get(id=pk)
    except Wizyta.DoesNotExist:
        return HttpResponse("Wizyta nie istnieje", status=404)

    if hasattr(user, 'opiekun'):
        if wizyta.zwierze.opiekun != user.opiekun:
            return HttpResponse("Brak dostępu", status=403)

    elif hasattr(user, 'weterynarz'):
        pass

    else:
        return HttpResponse("Brak roli użytkownika", status=403)

    return render(request, 'przychodnia/wizyty/wizyta_detail.html', {'wizyta': wizyta})


# DODAWANIE WIZYTY PRZEZ OPIEKUNA
@login_required
def dodaj_wizyte(request):
    user = request.user
    
    if not hasattr(user, 'opiekun'):
        return HttpResponse("Brak dostępu", status=403)

    if request.method == "POST":
        form = WizytaForm(request.POST, opiekun=user.opiekun)
        if form.is_valid():
            wizyta = form.save()
            return redirect('lista-wizyt')
    else:
        form = WizytaForm(opiekun=user.opiekun)

    return render(request, 'przychodnia/wizyty/dodaj_wizyte.html', {'form': form})


# FUNKCJA POMOCNICZA -> sprawdzamy, czy wizytę można zmienić (przełożyć/odwołać)
def sprawdz_czy_mozna_zmienic(user, wizyta):
    if not hasattr(user, 'opiekun') or wizyta.zwierze.opiekun != user.opiekun:
        return False, HttpResponse("Brak dostępu", status=403)
    
    if wizyta.status != STATUS_WIZYTA.Zaplanowana:
        return False, HttpResponseForbidden("Ta wizyta już się odbyła lub została odwołana.")
    
    if datetime.combine(wizyta.data_wizyty, wizyta.godzina_wizyty) <= datetime.now():
        return False, HttpResponseForbidden("Nie można zmienić wizyty, która już się rozpoczęła lub minęła.")
    
    return True, None


# PRZEŁOŻENIE WIZYTY PRZEZ OPIEKUNA
@login_required
def przeloz_wizyte(request, pk):
    user = request.user
    
    try:
        wizyta = Wizyta.objects.get(id=pk)
    except Wizyta.DoesNotExist:
        return HttpResponse("Wizyta nie istnieje", status=404)

    is_valid, error_response = sprawdz_czy_mozna_zmienic(user, wizyta)
    if not is_valid:
        return error_response

    if request.method == "POST":
        form = WizytaForm(request.POST, instance=wizyta, opiekun=user.opiekun)
        if form.is_valid():
            wizyta = form.save()
            return redirect("lista-wizyt")
    else:
        form = WizytaForm(instance=wizyta, opiekun=user.opiekun)

    # nie zmieniamy pola zwierze podczas przekładania wizyty
    form.fields['zwierze'].widget = forms.HiddenInput()
    form.initial['zwierze'] = wizyta.zwierze_id

    return render(request, 'przychodnia/wizyty/przeloz_wizyte.html', {'wizyta': wizyta, 'form': form})


# ODWOŁANIE WIZYTY PRZEZ OPIEKUNA
@login_required
def odwolaj_wizyte(request, pk):
    user = request.user
    
    try:
        wizyta = Wizyta.objects.get(id=pk)
    except Wizyta.DoesNotExist:
        return HttpResponse("Wizyta nie istnieje", status=404)

    is_valid, error_response = sprawdz_czy_mozna_zmienic(user, wizyta)
    if not is_valid:
        return error_response

    if request.method == "POST":
        wizyta.status = STATUS_WIZYTA.Odwołana
        wizyta.save()
        return redirect("lista-wizyt")

    return render(request, 'przychodnia/wizyty/odwolaj_wizyte.html', {'wizyta': wizyta})


# REALIZACJA WIZYTY PRZEZ WETERYNARZA
@login_required
def zrealizuj_wizyte(request, pk):
    user = request.user
    
    try:
        wizyta = Wizyta.objects.get(id=pk)
    except Wizyta.DoesNotExist:
        return HttpResponse("Wizyta nie istnieje", status=404)

    if not hasattr(user, 'weterynarz') or wizyta.weterynarz != user.weterynarz:
        return HttpResponse("Brak dostępu", status=403)

    if wizyta.status != STATUS_WIZYTA.Zaplanowana:
        return HttpResponseForbidden("Ta wizyta już się odbyła lub została odwołana.")

    if wizyta.data_wizyty != date.today():
        return HttpResponseForbidden("Można realizować tylko wizyty z dzisiejszego dnia.")

    if request.method == "POST":
        form = NotatkaForm(request.POST)

        if form.is_valid():
            wizyta.notatka = form.cleaned_data["notatka"]
            wizyta.status = STATUS_WIZYTA.Zrealizowana
            wizyta.save()
            return redirect("lista-wizyt")

    else:
        form = NotatkaForm()

    return render(request, 'przychodnia/wizyty/zrealizuj_wizyte.html', {'wizyta': wizyta, 'form': form})


# LISTA ZWIERZĄT DLA OPIEKUNA/WETERYNARZA
@login_required
def lista_zwierzat(request):
    user = request.user

    if hasattr(user, "opiekun"):
        zwierzeta = Zwierze.objects.filter(
            opiekun=user.opiekun
        )

    elif hasattr(user, "weterynarz"):
        zwierzeta = Zwierze.objects.all()

    else:
        return HttpResponseForbidden()
    
    return render(request, 'przychodnia/zwierzeta/lista_zwierzat.html', {'zwierzeta': zwierzeta})


# SZCZEGÓŁY ZWIERZAKA
@login_required
def zwierze_detail(request, pk):
    user = request.user
    
    try:
        zwierze = Zwierze.objects.get(id=pk)
    except Zwierze.DoesNotExist:
        return HttpResponse("Zwierzę nie istnieje", status=404)

    if hasattr(user, 'opiekun'):
        if zwierze.opiekun != user.opiekun:
            return HttpResponse("Brak dostępu", status=403)

    elif hasattr(user, 'weterynarz'):
        pass

    else:
        return HttpResponse("Brak roli użytkownika", status=403)

    return render(request, 'przychodnia/zwierzeta/zwierze_detail.html', {'zwierze': zwierze})


# HISTORIA WIZYT ZWIERZAKA
@login_required
def historia_wizyt(request, pk):
    user = request.user
    
    try:
        zwierze = Zwierze.objects.get(id=pk)
    except Zwierze.DoesNotExist:
        return HttpResponse("Zwierzę nie istnieje", status=404)

    if hasattr(user, 'opiekun'):
        if zwierze.opiekun != user.opiekun:
            return HttpResponse("Brak dostępu", status=403)

    elif hasattr(user, 'weterynarz'):
        pass

    else:
        return HttpResponse("Brak roli użytkownika", status=403)

    wizyty = Wizyta.objects.filter(
        zwierze=zwierze,
        status=STATUS_WIZYTA.Zrealizowana
    ).order_by('-data_wizyty', '-godzina_wizyty')

    return render(request, 'przychodnia/zwierzeta/historia_wizyt.html', {'zwierze': zwierze, 'wizyty': wizyty})


# DODAWANIE ZWIERZAKA PRZEZ OPIEKUNA
@login_required
def dodaj_zwierze(request):
    user = request.user
    
    if not hasattr(user, 'opiekun'):
        return HttpResponse("Brak dostępu", status=403)

    if request.method == "POST":
        form = ZwierzeForm(request.POST, opiekun=user.opiekun)
        if form.is_valid():
            zwierze = form.save()
            return redirect('lista-zwierzat')
    else:
        form = ZwierzeForm(opiekun=user.opiekun)

    return render(request, 'przychodnia/zwierzeta/dodaj_zwierze.html', {'form': form})