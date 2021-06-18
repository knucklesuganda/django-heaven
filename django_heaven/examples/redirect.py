""" That file contains examples for responses.redirect response classes """
from random import randint

from django.http import HttpResponseRedirect

from responses.redirect import LoggedRedirectResponseMixin
from django_heaven.examples._base import HeavenTestView


class HeavenTestRedirectView(LoggedRedirectResponseMixin, HeavenTestView):
    """
    That view will teach you how to use LoggedRedirectResponseMixin.
    As long as you return an HttpResponseRedirect - you are fine.
    Make some requests and look in the console while you are making them.
    """
    def get(self, request):
        if randint(0, 1):
            return self.log_response_as_error(
                redirect_to='https://google.com/',
                log_message="Redirected to google",
                redirect_code=302,
            )

        return self.log_response_as_info(
            redirect_to='https://example.com/',
            log_message="Redirected to example",
            redirect_code=302,
        )
