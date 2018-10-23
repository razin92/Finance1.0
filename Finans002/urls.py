"""Finans001 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views
admin.autodiscover()

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name="index"),
    url(r'^calc/', include('calc.urls')),
    url(r'^lib/', include('lib.urls')),
    url(r'^cabletv/', include('cabletv.urls')),
    url(r'^salary/', include('salary.urls')),
    url(r'^report/', include('report.urls')),
    url(r'^login/$', views.login_page, name="login"),
    url(r'^login-redirect/$', views.login_view, name="login-redirect"),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^bot/', include('telebot.urls')),
    url(r'^api/', include('api.urls'), name='api'),
]
