from django.urls import path, include

urlpatterns = [
    path('django_heaven_responses/', include('responses.examples.urls')),
]
