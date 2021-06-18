""" That file provides responses for the Django HttpResponse """
from responses.base import BaseLoggedResponseMixin


class LoggedHttpResponseMixin(BaseLoggedResponseMixin):
    """
    That class helps you to return HttpResponse as a proxy. A lot of people use render, and it
    is complicated and useless to bring such responses to the same structure, however, logging is an
    important thing and we use that class to log the http responses.
    """


__all__ = [
    "LoggedHttpResponseMixin",
]
