from django.urls import path, include

urlpatterns = [
    path('django_heaven_responses/', include('responses.examples.urls')),
    path('django_heaven_services/', include('services.examples.urls')),
]
