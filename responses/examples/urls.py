import sys

from django.conf import settings
from django.urls import path

from responses.examples.http import HeavenTestHttpView
from responses.examples.general import HeavenTestAPIView
from responses.examples.redirect import HeavenTestRedirectView
from responses.examples.json import HeavenTestJsonView, HeavenTestJsonProxyView

try:
    from responses.examples.rest_framework import HeavenTestRESTProxyView, HeavenTestRESTView
    has_rest = True
except ImportError:
    has_rest = False

if not settings.DEBUG and 'test' not in sys.argv:
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
]

if has_rest:
    urlpatterns += [
        # rest framework
        path('example/rest/', HeavenTestRESTView.as_view(), name='example_rest'),
        path('example/rest/proxy/', HeavenTestRESTProxyView.as_view(), name='example_rest_proxy'),
    ]
