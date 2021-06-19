""" That file contains responses for pure Django JsonResponse """
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from responses.base import BaseLoggedResponseMixin
from responses.exceptions import ResponseProgrammingException


class LoggedJsonResponseMixin(BaseLoggedResponseMixin):
    """
    Use that class in order to create a new JsonResponse() with structured data inside. Mind that
    I always use safe=False, since it is not a great idea from my point of view, and heaven must be a safe place.
    """
    response_type = JsonResponse

    def proxy_response_validation(self, data, status_code: int, **kwargs):
        """ Tests that the JsonResponse() is a safe one """
        try:
            if not isinstance(json.loads(data.content), dict):
                raise ResponseProgrammingException(
                    "JsonResponse() must be a safe one. Change your response structure to a dictionary"
                )
            if not isinstance(data, JsonResponse):
                raise ResponseProgrammingException(
                    f"Provide only JsonResponse() objects in LoggedJsonResponseProxyMixin()"
                )

        except json.JSONDecodeError:
            raise ResponseProgrammingException(
                f"Data provided in JsonResponse() cannot be decoded. Data: {data}"
            )

    def log_response_as_info(self, data, log_message: str, encoder=DjangoJSONEncoder, **kwargs):
        return self.log_response_proxy_or_creation(
            log_function=super(LoggedJsonResponseMixin, self).log_response_as_info,
            data=data,
            log_message=log_message,
            encoder=encoder,
            **kwargs,
        )

    def log_response_as_error(self, data, log_message: str, encoder=DjangoJSONEncoder, **kwargs):
        return self.log_response_proxy_or_creation(
            log_function=super(LoggedJsonResponseMixin, self).log_response_as_error,
            data=data,
            log_message=log_message,
            encoder=encoder,
            **kwargs,
        )


__all__ = [
    'LoggedJsonResponseMixin',
]
