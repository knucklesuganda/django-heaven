""" That file provides responses for the Django HttpResponse """
from django.http import HttpResponse, StreamingHttpResponse

from responses.base import BaseLoggedResponseMixin


class LoggedHttpResponseMixin(BaseLoggedResponseMixin):
    response_type = HttpResponse


class LoggedHttpStreamingResponseMixin(BaseLoggedResponseMixin):
    response_type = StreamingHttpResponse


__all__ = [
    "LoggedHttpResponseMixin",
    "LoggedHttpStreamingResponseMixin",
]
