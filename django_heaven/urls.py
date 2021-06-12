"""django_heaven URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path

from django_heaven.examples.http import HeavenTestHttpView
from django_heaven.examples.json import HeavenTestJsonView, HeavenTestJsonProxyView
from django_heaven.examples.redirect import HeavenTestRedirectView, HeavenTestRedirectProxyView
from django_heaven.examples.general import HeavenTestAPIView

try:
    from django_heaven.examples.rest_framework import HeavenTestRESTProxyView, HeavenTestRESTView
    has_rest = True
except ImportError:
    has_rest = False

if not settings.DEBUG:
    raise Warning("Do not use django-heaven testing views in production!")


app_name = 'heaven'

urlpatterns = [
    path('example/list/', HeavenTestAPIView.as_view()),

    # http
    path('example/http/', HeavenTestHttpView.as_view(), name='example_http'),

    # json
    path('example/json/', HeavenTestJsonView.as_view(), name='example_json'),
    path('example/json/proxy/', HeavenTestJsonProxyView.as_view(), name='example_json_proxy'),

    # redirect
    path('example/redirect/', HeavenTestRedirectView.as_view(), name='example_redirect'),
    path('example/redirect/proxy/', HeavenTestRedirectProxyView.as_view(), name='example_redirect_proxy'),
]

if has_rest:
    urlpatterns += [
        # rest framework
        path('example/rest/', HeavenTestRESTView.as_view(), name='example_rest'),
        path('example/rest/proxy/', HeavenTestRESTProxyView.as_view(), name='example_rest_proxy'),
    ]
