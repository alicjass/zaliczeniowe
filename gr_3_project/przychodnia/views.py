from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Opiekun, Zwierze, Weterynarz, Wizyta, STATUS_WIZYTA
from .forms import RegistrationForm, ProfilForm, WizytaForm, NotatkaForm, ZwierzeForm
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


# REJESTRACJA - KROK 1: dane Usera + wybór typu użytkownika
def user_register_step1(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # zapisujemy dane w sesji
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password1'],
                'typ_uzytkownika': form.cleaned_data['typ_uzytkownika']
            }
            return redirect('user-register-step2')
    else:
        # jesli dane są w sesji, wyswietlaja sie jako domyslne
        registration_data = request.session.get('registration_data', {})
        initial = {
            'username': registration_data.get('username'),
            'typ_uzytkownika': registration_data.get('typ_uzytkownika')
        }
        form = RegistrationForm(initial=initial)
    
    return render(request, 'przychodnia/rejestracja_step1.html', {'form': form})

# REJESTRACJA - KROK 2: uzupełnienie profilu i utworzenie konta 
def user_register_step2(request):
    registration_data = request.session.get('registration_data')
    
    if not registration_data:
        return redirect('user-register-step1')
    
    typ_uzytkownika = registration_data['typ_uzytkownika']
    
    if request.method == "POST":
        form = ProfilForm(request.POST, typ_uzytkownika=typ_uzytkownika)
        if form.is_valid():
            # tworzymy User
            user = User.objects.create_user(
                username=registration_data['username'],
                password=registration_data['password'],
                first_name=form.cleaned_data['imie'],
                last_name=form.cleaned_data['nazwisko']
            )
            
            # tworzymy profil
            profil_data = {
                'user': user,
                'imie': form.cleaned_data['imie'],
                'nazwisko': form.cleaned_data['nazwisko'],
                'plec': form.cleaned_data['plec']
            }
            
            if typ_uzytkownika == 'opiekun':
                Opiekun.objects.create(**profil_data)
                redirect_url = 'przyszle-wizyty'
            else:
                profil_data['specjalizacja'] = form.cleaned_data.get('specjalizacja', '')
                Weterynarz.objects.create(**profil_data)
                redirect_url = 'dzisiejsze-wizyty'
            
            del request.session['registration_data']
            
            # logujemy i przekierowujemy
            login(request, user)
            return redirect(redirect_url)
    else:
        form = ProfilForm(typ_uzytkownika=typ_uzytkownika)
    
    return render(request, 'przychodnia/rejestracja_step2.html', {
        'form': form,
        'typ_uzytkownika': typ_uzytkownika
    })


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

            elif hasattr(user, 'weterynarz'):
                return redirect('dzisiejsze-wizyty')
            
            elif hasattr(user, 'opiekun'):
                return redirect('przyszle-wizyty')

        else:
            return render(request, 'przychodnia/login.html', {'error': 'Nieprawidłowe dane'})
    
    return render(request, 'przychodnia/login.html')

def user_logout(request):
    logout(request)
    return redirect('user-login')


# PROFIL UŻYTKOWNIKA
@login_required
def user_profil(request):
    user = request.user
    
    opiekun = None
    weterynarz = None
    
    if hasattr(user, 'opiekun'):
        opiekun = user.opiekun
        
    elif hasattr(user, 'weterynarz'):
        weterynarz = user.weterynarz
    
    return render(request, 'przychodnia/user/user_profil.html', {
        'user': user,
        'opiekun': opiekun,
        'weterynarz': weterynarz
    })


# EDYCJA PROFILU UŻYTKOWNIKA
@login_required
def edytuj_profil(request):
    user = request.user
    
    if hasattr(user, 'opiekun'):
        instance = user.opiekun
    
    elif hasattr(user, 'weterynarz'):
        instance = user.weterynarz
    
    else:
        return HttpResponse("Brak dostępu", status=403)
    
    if request.method == "POST":
        form = ProfilForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('user-profil')
    else:
        form = ProfilForm(instance=instance)
    
    return render(request, 'przychodnia/user/edytuj_profil.html', {'form': form})


# LISTA NADCHODZĄCYCH WIZYT DLA OPIEKUNA/WETERYNARZA
@login_required
def przyszle_wizyty(request):
    user = request.user

    Wizyta.aktualizuj_przeterminowane_wizyty()

    if hasattr(user, "opiekun"):
        wizyty = Wizyta.objects.filter(
            zwierze__opiekun=user.opiekun,
            status=STATUS_WIZYTA.Zaplanowana  # tylko zaplanowane wizyty
        )

    elif hasattr(user, "weterynarz"):
        wizyty = Wizyta.objects.filter(
            weterynarz=user.weterynarz,
            data_wizyty__gt=date.today()  # wszystkie statusy, ale tylko przyszle wizyty
        )

    else:
        return HttpResponseForbidden()
    
    return render(request, 'przychodnia/wizyty/przyszle_wizyty.html', {'wizyty': wizyty})


# DZISIEJSZE WIZYTY WETERYNARZA
@login_required
def dzisiejsze_wizyty(request):
    user = request.user
    
    Wizyta.aktualizuj_przeterminowane_wizyty()

    if not hasattr(user, "weterynarz"):
        return HttpResponseForbidden()

    wizyty = Wizyta.objects.filter(
        weterynarz=user.weterynarz,
        data_wizyty=date.today()  # wszystkie statusy, ale tylko dzisiejsze wizyty
    )
    
    return render(request, 'przychodnia/wizyty/dzisiejsze_wizyty.html', {'wizyty': wizyty})


# HISTORIA WIZYT DLA OPIEKUNA/WETERYNARZA
@login_required
def historia_wizyt(request):
    user = request.user

    if hasattr(user, "opiekun"):
        wizyty = Wizyta.objects.filter(
            zwierze__opiekun=user.opiekun,
            status=STATUS_WIZYTA.Zrealizowana
        ).order_by('-data_wizyty', '-godzina_wizyty')

    elif hasattr(user, "weterynarz"):
        wizyty = Wizyta.objects.filter(
            weterynarz=user.weterynarz,
            status=STATUS_WIZYTA.Zrealizowana
        ).order_by('-data_wizyty', '-godzina_wizyty')

    else:
        return HttpResponseForbidden()
    
    return render(request, 'przychodnia/wizyty/historia_wizyt.html', {'wizyty': wizyty})


# SZCZEGÓŁY WIZYTY
@login_required
def wizyta_detail(request, pk):
    user = request.user
    
    Wizyta.aktualizuj_przeterminowane_wizyty()

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
            return redirect('przyszle-wizyty')
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
            return redirect("przyszle-wizyty")
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
        return redirect("przyszle-wizyty")

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
            return redirect("dzisiejsze-wizyty")

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
def historia_zwierzaka(request, pk):
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

    return render(request, 'przychodnia/zwierzeta/historia_zwierzaka.html', {'zwierze': zwierze, 'wizyty': wizyty})


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


# EDYCJA ZWIERZAKA PRZEZ OPIEKUNA
@login_required
def edytuj_zwierze(request, pk):
    user = request.user
    
    try:
        zwierze = Zwierze.objects.get(id=pk)
    except Zwierze.DoesNotExist:
        return HttpResponse("Zwierzę nie istnieje", status=404)

    if not hasattr(user, 'opiekun') or zwierze.opiekun != user.opiekun:
        return HttpResponse("Brak dostępu", status=403)
    
    if request.method == "POST":
        form = ZwierzeForm(request.POST, instance=zwierze, opiekun=user.opiekun)
        if form.is_valid():
            zwierze = form.save()
            return redirect("zwierze-detail", pk=zwierze.pk)
    else:
        form = ZwierzeForm(instance=zwierze, opiekun=user.opiekun)

    return render(request, 'przychodnia/zwierzeta/edytuj_zwierze.html', {'zwierze': zwierze, 'form': form})