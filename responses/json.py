""" That file contains responses for pure Django JsonResponse """
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from responses.base import BaseLoggedResponseMixin, BaseLoggedResponseProxyMixin


class LoggedJsonResponseMixin(BaseLoggedResponseMixin):
    """
    Use that class in order to create a new JsonResponse() with structured data inside. Mind that
    I always use safe=False, since it is not a great idea from my point of view, and heaven must be a safe place.
    """
    def log_response_as_info(self, data, log_message: str, encoder=DjangoJSONEncoder, *args, **kwargs):
        result_response = super(LoggedJsonResponseMixin, self).log_response_as_info(
            data=data, log_message=log_message, *args, **kwargs,
        )
        return JsonResponse(result_response, encoder=encoder, safe=True)

    def log_response_as_error(self, data, log_message: str, encoder=DjangoJSONEncoder, *args, **kwargs):
        result_response = super(LoggedJsonResponseMixin, self).log_response_as_error(
            data=data, log_message=log_message, *args, **kwargs,
        )
        return JsonResponse(result_response, encoder=encoder, safe=True)


class LoggedJsonResponseProxyMixin(BaseLoggedResponseProxyMixin):
    """
    That class is used as a proxy for already built JsonResponse() objects. But, again, we check
    safe=True because the heaven must be safe.
    """

    def test_response_is_safe(self, data):
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

    def log_response_as_info(self, data, log_message: str, *args, **kwargs):
        self.test_response_is_safe(data)

        return super(LoggedJsonResponseProxyMixin, self).log_response_as_info(
            data=data, log_message=log_message, *args, **kwargs
        )

    def log_response_as_error(self, data, log_message: str, *args, **kwargs):
        self.test_response_is_safe(data)

        return super(LoggedJsonResponseProxyMixin, self).log_response_as_info(
            data=data, log_message=log_message, *args, **kwargs
        )


__all__ = [
    'LoggedJsonResponseMixin',
    'LoggedJsonResponseProxyMixin',
]
