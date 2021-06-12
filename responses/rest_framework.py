""" That file provides responses for the django-rest-framework """
from typing import no_type_check

try:
    from rest_framework.response import Response
except ImportError:
    raise ImportError("You need to install django-rest-framework in order to user rest_framework responses")

from responses.base import BaseLoggedResponseMixin, BaseLoggedResponseProxyMixin


class LoggedRESTResponseMixin(BaseLoggedResponseMixin):
    """
    That class helps you to not only log your data, but return
    Django rest framework Response() as the formatted result.
    It will create a new Response() object from the data that you supplied,
    and after that it will pass status_code and *args with **kwargs inside of it.
    """

    @no_type_check
    def log_response_as_error(
        self, data, log_message: str, status_code: int, *args, **kwargs,
    ) -> Response:
        result_data = super(LoggedRESTResponseMixin, self).log_response_as_error(
            data=data, log_message=log_message,
        )
        return Response(data=result_data, status=status_code, *args, **kwargs)

    @no_type_check
    def log_response_as_info(
        self, data, log_message: str, status_code: int, *args, **kwargs,
    ) -> Response:
        result_data = super(LoggedRESTResponseMixin, self).log_response_as_info(
            data=data, log_message=log_message,
        )
        return Response(data=result_data, status=status_code, *args, **kwargs)


class LoggedRESTResponseProxyMixin(BaseLoggedResponseProxyMixin):
    """ Use that class if you already have Response(), but still want to log the results """


__all__ = [
    "LoggedRESTResponseMixin",
    "LoggedRESTResponseProxyMixin",
]
