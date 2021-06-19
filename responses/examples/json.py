""" That file contains examples for responses.json response classes """
from django.http import JsonResponse

from responses.examples.base import HeavenTestView
from responses.json import LoggedJsonResponseMixin


class HeavenTestJsonView(LoggedJsonResponseMixin, HeavenTestView):
    error_data = {"errors": [1, 2, 3], "reason": "because"}
    success_data = "OK"


class HeavenTestJsonProxyView(LoggedJsonResponseMixin, HeavenTestView):
    error_data = JsonResponse({"errors": "Proxy error", "reason": "because"})
    success_data = JsonResponse({"hello": "Proxy success"})
