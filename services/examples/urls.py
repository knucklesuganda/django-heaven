from django.urls import path

from services.examples.own_service_example import HeavenOwnServiceTestView

app_name = 'heaven_services'

urlpatterns = [
    path('example/own_service_example/', HeavenOwnServiceTestView.as_view()),

]
