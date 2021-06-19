""" That file contains base classes for the formatted Responses """
from django.conf import settings


RESPONSES_SETTINGS = settings.DJANGO_HEAVEN['RESPONSES']


class BaseLoggedResponseMixin:
    """
    That class helps you bring all your responses to the similar structure and log the results.
    We follow the simple rule: if your data is an instance of any item of
    settings.DJANGO_HEAVEN.RESPONSES.RAW_TYPES, then we convert it to a dictionary, or using
    self.data_conversion_function().
    """
    logger_obj = RESPONSES_SETTINGS['LOGGER_OBJ']
    raw_types = RESPONSES_SETTINGS['RAW_TYPES']
    response_type = None

    def data_conversion_function(self, data, **kwargs):
        """
        That function accepts the raw data from the self._log_response() and uses it
        to convert it to a similar structured responses.
        """
        return {
            RESPONSES_SETTINGS['DEFAULT_RESPONSE_VERB']: data,
        }

    def _log_response(self, log_function: callable, data, log_message: str, **kwargs):
        """
        That function is used to log the response and return your converted data.
        Do not use it directly, create a wrapper that will work with it internally or
        use our wrappers.
        :params:
            - log_function(callable): any function that will log the response
            - data(str or dict): data that you provide, if it's an item
                of settings.DJANGO_HEAVEN.RESPONSES.RAW_TYPES, then we will convert it
                to a dict() or using self.data_conversion_function(), otherwise we will just
                leave it as it is.
            - log_message(str): the message that you want to put in logs
        :returns: either dict() or list() with logs and message formatting
        """
        log_function(log_message)

        if isinstance(data, self.raw_types):
            data = self.data_conversion_function(data, **kwargs)

        return data

    def log_response_as_info(self, data, log_message: str, **kwargs):
        """
        That function helps you to log the response as an informational message.
        Parameters are the same as the are in the _log_response() function
        """
        return self._log_response(
            data=data,
            log_function=self.logger_obj.info,
            log_message=log_message,
            **kwargs,
        )

    def log_response_as_error(self, data, log_message: str, **kwargs):
        """
        That function helps you to log the response as an error message.
        Parameters are the same as the are in the _log_response() function
        """
        return self._log_response(
            data=data,
            log_function=self.logger_obj.error,
            log_message=log_message,
            **kwargs,
        )

    def proxy_response_validation(self, data, status_code: int, **kwargs):
        """ That function works as the additional validation for the response from the outer code. """

    def log_response_proxy_or_creation(
        self, log_function: callable, data, log_message: str, status_code: int, **kwargs,
    ):
        """
        That is the function that helps you to log your response either creating the
        response from the data provided or act as a proxy depending on
        the self.response_base_type variable.
        """
        result_data = log_function(data=data, log_message=log_message, **kwargs)

        if isinstance(data, self.response_type):
            self.proxy_response_validation(data, status_code, **kwargs)
            return data

        return self.response_type(
            data=result_data, status=status_code, **(kwargs.get('response_kwargs') or {}),
        )


__all__ = [
    'BaseLoggedResponseMixin',
]
