from typing import no_type_check, Union

from django.http import HttpResponseRedirect

from responses.base import BaseLoggedResponseMixin


class LoggedRedirectResponseMixin(BaseLoggedResponseMixin):
    """ That class allows you to still log your responses, but call a redirect instead of dict() """
    response_type = HttpResponseRedirect

    @no_type_check
    def log_response_as_info(
        self, data: Union[HttpResponseRedirect, str], log_message: str,
        redirect_code: int, kwargs: dict = None,
    ) -> HttpResponseRedirect:
        return self.log_response_proxy_or_creation(
            log_function=super(LoggedRedirectResponseMixin, self).log_response_as_info,
            data=data,
            log_message=log_message,
            status_code=redirect_code,
            kwargs=kwargs,
        )

    @no_type_check
    def log_response_as_error(
        self, data: Union[HttpResponseRedirect, str], log_message: str,
        redirect_code: int, kwargs: dict = None,
    ) -> HttpResponseRedirect:
        return self.log_response_proxy_or_creation(
            log_function=super(LoggedRedirectResponseMixin, self).log_response_as_error,
            data=data,
            log_message=log_message,
            status_code=redirect_code,
            kwargs=kwargs,
        )


__all__ = [
    'LoggedRedirectResponseMixin',
]
