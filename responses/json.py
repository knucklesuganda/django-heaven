""" That file contains responses for pure Django JsonResponse """
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from responses.base import BaseLoggedResponseMixin


class LoggedJsonResponseMixin(BaseLoggedResponseMixin):
    """
    Use that class in order to create a new JsonResponse() with structured data inside. Mind that
    I always use safe=False, since it is not a great idea from my point of view, and heaven must be a safe place.
    """
    def check_response_is_safe(self, data):
        """ Tests that the JsonResponse() is a safe one """
        try:
            if not isinstance(json.loads(data.content), dict):
                raise ValueError(
                    "JsonResponse() must be a safe one. Change your response structure to a dictionary"
                )
        except json.JSONDecodeError:
            raise ValueError(f"Data provided in JsonResponse() cannot be decoded. Data: {data}")
        except (AttributeError, TypeError, ValueError):
            raise ValueError(f"Provide only JsonResponse() objects in LoggedJsonResponseProxyMixin()")

    def _log_json_response(
        self, log_function: callable, data, log_message: str, encoder=DjangoJSONEncoder, **kwargs,
    ):
        """ That function is used not to copy the code that we use in log_info and log_error """
        result_response = log_function(data=data, log_message=log_message, **kwargs)

        if isinstance(data, JsonResponse):
            self.check_response_is_safe(data)
            return data

        return JsonResponse(result_response, encoder=encoder, safe=True,
                            **(kwargs.get('response_kwargs') or {}))

    def log_response_as_info(self, data, log_message: str, encoder=DjangoJSONEncoder, **kwargs):
        return self._log_json_response(
            log_function=super(LoggedJsonResponseMixin, self).log_response_as_error,
            data=data,
            log_message=log_message,
            encoder=encoder,
            **kwargs,
        )

    def log_response_as_error(self, data, log_message: str, encoder=DjangoJSONEncoder, **kwargs):
        return self._log_json_response(
            log_function=super(LoggedJsonResponseMixin, self).log_response_as_error,
            data=data,
            log_message=log_message,
            encoder=encoder,
            **kwargs,
        )


__all__ = [
    'LoggedJsonResponseMixin',
]
