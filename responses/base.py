""" That file contains base classes for the formatted Responses """
from django.conf import settings


RESPONSES_SETTINGS = settings.DJANGO_HEAVEN['RESPONSES']


class BaseLoggedResponseMixin:
    """
    That class helps you bring all your responses to the similar structure and log the results.
    We follow the simple rule: if your data is an instance of any item of
    settings.DJANGO_HEAVEN.RESPONSES.RAW_TYPES, then we convert it to a dictionary, or using
    self.data_conversion_function()
    """
    logger_obj = None

    def __init__(self, *args, **kwargs):
        super(BaseLoggedResponseMixin, self).__init__(*args, **kwargs)
        response_global_logger = RESPONSES_SETTINGS.get('LOGGER_OBJ')

        if self.logger_obj:
            return
        elif self.logger_obj is None and not response_global_logger:
            raise TypeError("There is no logger assigned in LoggedResponseMixin or in global settings")
        elif response_global_logger:
            self.logger_obj = response_global_logger

    def data_conversion_function(self, data, *args, **kwargs):
        """
        That function accepts the raw data from the self._log_response() and uses it
        to convert it to a similar structured responses.
        """
        return {RESPONSES_SETTINGS.get('DEFAULT_RESPONSE_VERB', "detail"): data}

    def _log_response(self, log_function: callable, data, log_message: str, *args, **kwargs):
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

        if isinstance(data, RESPONSES_SETTINGS.get('RAW_TYPES', (str, int, bytes))):
            data = self.data_conversion_function(data)

        return data

    def log_response_as_info(self, data, log_message: str, *args, **kwargs):
        """
        That function helps you to log the response as an informational message.
        Parameters are the same as the are in the _log_response() function
        """
        return self._log_response(
            data=data,
            log_function=self.logger_obj.info,
            log_message=log_message,
        )

    def log_response_as_error(self, data, log_message: str, *args, **kwargs):
        """
        That function helps you to log the response as an error message.
        Parameters are the same as the are in the _log_response() function
        """
        return self._log_response(
            data=data,
            log_function=self.logger_obj.error,
            log_message=log_message,
        )


class BaseLoggedResponseProxyMixin(BaseLoggedResponseMixin):
    """
    That class is really similar to BaseLoggedResponseMixin, but instead of the response construction
    we directly provide what we want to return. That may be useful if your responses come from different
    modules, have cookies or sessions in them. You can directly use that class, but you will find
    ancestors with difference in class names only. That is used in order to bring more descriptive
    names to classes in the real projects.
    """

    def data_conversion_function(self, data, *args, **kwargs):
        return data

    def log_response_as_info(self, data, log_message: str, *args, **kwargs):
        """
        That function helps you to log the response as an informational message.
        Parameters are the same as the are in the _log_response() function
        """
        super(BaseLoggedResponseProxyMixin, self).log_response_as_info(
            data=data, log_message=log_message, *args, **kwargs,
        )
        return data

    def log_response_as_error(self, data, log_message: str, *args, **kwargs):
        """
        That function helps you to log the response as an error message.
        Parameters are the same as the are in the _log_response() function
        """
        super(BaseLoggedResponseProxyMixin, self).log_response_as_error(
            data=data, log_message=log_message, *args, **kwargs,
        )
        return data
