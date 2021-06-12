""" That file contains examples for responses.json response classes """
from random import randint

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from responses.rest_framework import LoggedRESTResponseMixin, LoggedRESTResponseProxyMixin


class HeavenTestRESTView(LoggedRESTResponseMixin, ListAPIView):
    def list(self, request, *args, **kwargs):
        if randint(0, 1):
            return self.log_response_as_error(
                data={"rest_error": "Framework error"},
                log_message="REST error in test view",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return self.log_response_as_info(
            data=[1, 2, 3, 4, 5, 6, 7, 8],
            log_message="REST success in test view",
            status_code=status.HTTP_200_OK,
        )


class HeavenTestRESTProxyView(LoggedRESTResponseProxyMixin, ListAPIView):
    queryset = []

    def list(self, request, *args, **kwargs):
        if randint(0, 1):
            return self.log_response_as_error(
                data=Response({"rest_error": "REST proxy error"}),
                log_message="REST error in test view",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return self.log_response_as_info(
            data=Response("REST Proxy success"),
            log_message="REST success in test view",
            status_code=status.HTTP_200_OK,
        )
