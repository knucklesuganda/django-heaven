from functools import wraps

from django.conf import settings
from django.core.exceptions import FieldError

from services.exceptions import ServiceProgrammingException


SERVICES_SETTINGS = settings.DJANGO_HEAVEN['SERVICES']


class ServiceFunctionDecorator:
    def __init__(
        self, force_error_message: bool = SERVICES_SETTINGS.get('FORCE_ERROR_MESSAGE_ARGUMENT', True),
        force_info_message: bool = SERVICES_SETTINGS.get('FORCE_INFO_MESSAGE_ARGUMENT', True),
    ):
        self.force_error_message = force_error_message
        self.force_info_message = force_info_message

    def __logger_argument_check_forced(self, argument_name: str, kwargs):
        """ Checks that the appropriate logger argument is provided if the user set is as forced """
        if getattr(self, f"force_{argument_name}", False):
            if kwargs.get(argument_name) is None:
                raise ValueError(f"You must provide {argument_name} argument")
            del kwargs[argument_name]

        return kwargs

    def format_logger_message(self, message: str, resulted_service) -> str:
        """ Use that function in order to format your message. __format__ will be implemented in the future """
        if resulted_service is None:    # if an error happens, then we cannot use the values of None
            return message

        for replace_key, replace_value in (
            ("$service$", resulted_service),
            ("$result$", resulted_service.result),
        ):
            message = message.replace(replace_key, str(replace_value))

        return message

    def __call__(self, function):
        """
        That decorator is used on every service function. It either runs the functions,
        logs the result and returns it, or logs the result in service_function_error_handler().

        You need to provide named-only arguments called: 'error_message' and 'info_message'.
        These arguments act as the log messages that we will use in error or success scenarios.
        If you don't want to provide an argument, then try tuning
        settings.DJANGO_HEAVEN.SERVICES.FORCE_ERROR_MESSAGE_ARGUMENT argument and the same one
        with INFO instead of ERROR.

        returned_result_in_info is another argument that you may provide. If so, we will
        automatically replace %result% substring in the info message with the result returned from the
        function().
        """

        def service_function_decorator_wrapper(service, *args, **kwargs):
            error_message = kwargs.get('error_message')
            info_message = kwargs.get('info_message')

            kwargs = self.__logger_argument_check_forced(argument_name='info_message', kwargs=kwargs)
            kwargs = self.__logger_argument_check_forced(argument_name='error_message', kwargs=kwargs)

            # We delete it so it does not interfere with other ORM arguments.

            try:
                new_service = service.__class__(objects=function(service, *args, **kwargs))

                if info_message is not None:
                    service.logger_obj.info(
                        self.format_logger_message(info_message, new_service),
                    )

                return new_service

            except (FieldError, ServiceProgrammingException) as exc:
                # Field error is related to the wrong arguments, that may be typo,
                # so we don't want to except these as the normal exception
                raise exc
            except Exception as exc:
                error_message = error_message or SERVICES_SETTINGS['DEFAULT_ERROR_LOG_MESSAGE']

                if settings.DEBUG:  # We add the exception to the log in DEBUG mode
                    error_message += f". Exception: {exc}"

                service.logger_obj.error(self.format_logger_message(error_message, None,))
                return service.service_function_error_handler(exc=exc)

        return service_function_decorator_wrapper


def service_function_for_write(function: callable):
    """ That decorator marks service function that can change the information in the database """

    @wraps(function)
    def service_function_for_write_wrapper(service, *args, **kwargs):
        if service.read_only:
            raise ServiceProgrammingException(f"You are calling write function on read_only service {service}")

        return function(service, *args, **kwargs)

    return service_function_for_write_wrapper


__all__ = [
    'ServiceFunctionDecorator',
    'service_function_for_write',
]
