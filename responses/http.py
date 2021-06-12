""" That file provides responses for the Django HttpResponse """
from typing import no_type_check, Union

from django.http import HttpResponse, StreamingHttpResponse

from responses.base import BaseLoggedResponseMixin


class LoggedHttpResponseProxyMixin(BaseLoggedResponseMixin):
    """
    That class helps you to return HttpResponse as a proxy. I will not create
    LoggedHttpResponseMixin since a lot of people use render, and it is complicated and useless
    to bring such responses to the same structure, however, logging is an important thing and
    we use that class to log the http responses.
    """


__all__ = [
    "LoggedHttpResponseProxyMixin",
]
