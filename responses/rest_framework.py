""" That file provides responses for the django-rest-framework """
from typing import no_type_check

try:
    from rest_framework.response import Response
except ImportError:
    raise ImportError("You need to install django-rest-framework in order to use rest_framework responses")

from responses.base import BaseLoggedResponseMixin


class LoggedRESTResponseMixin(BaseLoggedResponseMixin):
    """
    That class helps you to not only log your data, but return
    Django rest framework Response() as the formatted result.
    It will create a new Response() object from the data that you supplied,
    and after that it will pass status_code and *args with **kwargs inside of it.
    """
    response_type = Response

    @no_type_check
    def log_response_as_error(
        self, data, log_message: str, status_code: int, **kwargs,
    ) -> Response:
        return self.log_response_proxy_or_creation(
            log_function=super(LoggedRESTResponseMixin, self).log_response_as_error,
            data=data,
            log_message=log_message,
            status_code=status_code,
            **kwargs,
        )

    @no_type_check
    def log_response_as_info(
        self, data, log_message: str, status_code: int, **kwargs,
    ) -> Response:
        return self.log_response_proxy_or_creation(
            log_function=super(LoggedRESTResponseMixin, self).log_response_as_info,
            data=data,
            log_message=log_message,
            status_code=status_code,
            **kwargs,
        )


__all__ = [
    "LoggedRESTResponseMixin",
]
