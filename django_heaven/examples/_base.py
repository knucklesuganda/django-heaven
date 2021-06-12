""" That file contains examples for responses.http response classes """
from random import randint

from django.views import View


class HeavenTestView(View):
    """
    That view will teach you how to use different responses.
    As long as you return a normal great response - you are fine.
    Make some requests and look in the console while you are making them.

    error_data - data that should be returned in the error response
    success_data - data that should be returned in the successful response
    """
    error_data = None
    success_data = None

    def get(self, request):
        if randint(0, 1):
            # Some error happened, or some checks failed in our view, we log an error and return the result
            return self.log_response_as_error(
                data=self.error_data,
                log_message=f"Wow, that is bad. An error happened in {self.__class__.__name__}()",
            )

        # Everything is alright, we can return a normal view
        return self.log_response_as_info(
            data=self.success_data,
            log_message=f"Everything was great in {self.__class__.__name__}()",
        )


__all__ = [
    'HeavenTestView',
]
