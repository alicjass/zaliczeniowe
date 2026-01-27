from django.http import HttpResponseForbidden
from functools import wraps


# DEKORATORY: sprawdzamy typ użytkownika
def opiekun_required(view_func):
    """Wymaga, aby użytkownik był opiekunem"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'opiekun'):
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper


def weterynarz_required(view_func):
    """Wymaga, aby użytkownik był weterynarzem"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'weterynarz'):
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper


def opiekun_or_weterynarz_required(view_func):
    """Wymaga, aby użytkownik był opiekunem lub weterynarzem"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (hasattr(request.user, 'opiekun') or hasattr(request.user, 'weterynarz')):
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper


# FUNKCJE POMOCNICZE: sprawdzamy dostęp do obiektów (zwierząt/wizyt)
def sprawdz_dostep_do_zwierzecia(user, zwierze):
    """Sprawdza, czy użytkownik ma dostęp do zwierzęcia"""
    if hasattr(user, 'opiekun'):
        if zwierze.opiekun != user.opiekun:  # opiekun: tylko swoje zwierzęta
            return False, HttpResponseForbidden()
    elif hasattr(user, 'weterynarz'):
        pass  # weterynarz: wszystkie zwierzęta
    else:
        return False, HttpResponseForbidden()
    
    return True, None


def sprawdz_dostep_do_wizyty(user, wizyta):
    """Sprawdza, czy użytkownik ma dostęp do wizyty"""
    if hasattr(user, 'opiekun'):
        if wizyta.zwierze.opiekun != user.opiekun:  # opiekun: tylko wizyty swoich zwierząt
            return False, HttpResponseForbidden()
    elif hasattr(user, 'weterynarz'):
        pass  # weterynarz: wszystkie wizyty
    else:
        return False, HttpResponseForbidden()
    
    return True, None