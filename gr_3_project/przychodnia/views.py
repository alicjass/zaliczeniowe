from django.shortcuts import render
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