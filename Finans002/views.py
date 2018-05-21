from django.http import request, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from salary.models import Worker
from .forms import LoginForm

@login_required()
def index(request):
    workers = Worker.objects.filter(user=request.user)
    if workers.__len__() > 0:
        return HttpResponseRedirect(reverse('salary:work_report_create'))
    return HttpResponseRedirect(reverse('calc:transaction'))

def login_page(request):
    error = ''
    form = LoginForm
    return render(request, "login.html", {'error': error, 'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
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
                'form': form,
            }
            return render(request, "login.html", context)

    else:
        error = 'Неправильный логин или пароль'
        context = {
            'error': error,
            'form': form,
        }
        return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))