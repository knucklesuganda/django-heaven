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

    def _log_rest_response(
        self, log_function: callable, data, log_message: str, status_code: int, **kwargs,
    ):
        result_data = log_function(data=data, log_message=log_message, **kwargs)
        if isinstance(data, Response):
            return data

        return Response(data=result_data, status=status_code, **(kwargs.get('response_kwargs') or {}))

    @no_type_check
    def log_response_as_error(
        self, data, log_message: str, status_code: int, **kwargs,
    ) -> Response:
        return self._log_rest_response(
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
        return self._log_rest_response(
            log_function=super(LoggedRESTResponseMixin, self).log_response_as_info,
            data=data,
            log_message=log_message,
            status_code=status_code,
            **kwargs,
        )


__all__ = [
    "LoggedRESTResponseMixin",
]
