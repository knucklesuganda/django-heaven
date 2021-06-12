from typing import no_type_check

from django.http import HttpResponseRedirect

from responses.base import BaseLoggedResponseMixin, BaseLoggedResponseProxyMixin


class LoggedRedirectResponseMixin(BaseLoggedResponseMixin):
    """ That class allows you to still log your responses, but call a redirect instead of dict() """

    @no_type_check
    def log_response_as_info(
        self, redirect_to: str, kwargs: dict, log_message: str, redirect_code: int,
    ) -> HttpResponseRedirect:
        """
        That function will call normal LoggedResponseMixin info function, but will return redirect instead.
        :params:
            - redirect_to(str): page you want to redirect your user to
            - kwargs(dict): additional arguments for that page
            - redirect_code(int): permanent(308) or temporary(307) redirect
        :rtype: HttpResponseRedirect
        :returns: redirect to another page
        """
        super(LoggedRedirectResponseMixin, self).log_response_as_info(
            data=None, log_message=log_message, status_code=redirect_code,
        )
        return HttpResponseRedirect(redirect_to, **kwargs)

    @no_type_check
    def log_response_as_error(
        self, redirect_to: str, kwargs: dict, log_message: str, redirect_code: int,
    ) -> HttpResponseRedirect:
        """
        That function will call normal LoggedResponseMixin error function, but will return redirect instead.
        :params:
            - redirect_to(str): page you want to redirect your user to
            - kwargs(dict): additional arguments for that page
            - redirect_code(int): permanent(308) or temporary(307) redirect
        :rtype: HttpResponseRedirect
        :returns: redirect to another page
        """
        super(LoggedRedirectResponseMixin, self).log_response_as_error(
            data=None, log_message=log_message, status_code=redirect_code,
        )
        return HttpResponseRedirect(redirect_to, **kwargs)


class LoggedRedirectResponseProxyMixin(BaseLoggedResponseProxyMixin):
    """ Use that class to redirect the client to an already existing HttpResponseRedirect object """
