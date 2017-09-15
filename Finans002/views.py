from django.http import request, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required()
def index(request):

    return render(request, "index.html")

def login_page(request):
    error = ''
    return render(request, "login.html", {'error': error})


def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            error = 'Аккаунт не активирован!'
            context = {
                'error': error,
            }
            return render(request, "login.html", context)

    else:
        error = 'Неправильный логин или пароль'
        context = {
            'error': error,
        }
        return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))