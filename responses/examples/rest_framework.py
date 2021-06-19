""" That file contains examples for responses.json response classes """
from random import randint

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from responses.rest_framework import LoggedRESTResponseMixin


class CustomLoggedRESTResponseMixin(LoggedRESTResponseMixin):
    def data_conversion_function(self, data, *args, **kwargs):
        return {
            "data": data,
            "status_code": kwargs.get('status_code'),
            "errors": kwargs.get('errors'),
        }


class HeavenTestRESTView(CustomLoggedRESTResponseMixin, ListAPIView):
    def list(self, request, *args, **kwargs):
        if randint(0, 1):
            return self.log_response_as_error(
                data={"rest_error": "Framework error"},
                log_message="REST error in test view",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors={"error1": "hello"},
            )

        return self.log_response_as_info(
            data="REST success in test view",
            log_message="REST success in test view",
            status_code=status.HTTP_200_OK,
        )


class HeavenTestRESTProxyView(LoggedRESTResponseMixin, ListAPIView):
    queryset = []

    def list(self, request, *args, **kwargs):
        if randint(0, 1):
            return self.log_response_as_error(
                data=Response("Rest proxy error"),
                log_message="REST error in test proxy view",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return self.log_response_as_info(
            data=Response("REST Proxy success"),
            log_message="REST success in test proxy view",
            status_code=status.HTTP_200_OK,
        )

