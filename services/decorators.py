from functools import wraps

from django.conf import settings
from django.core.exceptions import FieldError

from services.exceptions import ServiceProgrammingException


SERVICES_SETTINGS = settings.DJANGO_HEAVEN['SERVICES']


class ServiceFunctionDecorator:
    def __init__(self, force_error_message: bool = None, force_info_message: bool = None):
        if force_error_message is None:
            force_error_message = SERVICES_SETTINGS['FORCE_ERROR_MESSAGE_ARGUMENT']
        if force_info_message is None:
            force_info_message = SERVICES_SETTINGS['FORCE_INFO_MESSAGE_ARGUMENT']

        self.force_error_message = force_error_message
        self.force_info_message = force_info_message

    def _logger_argument_check_forced(self, argument_name: str, kwargs):
        """ Checks that the appropriate logger argument is provided if the user set is as forced """
        argument_value = kwargs.get(argument_name)

        if getattr(self, f"force_{argument_name}", False):
            if argument_value is None:
                raise ValueError(f"You must provide {argument_name} argument")

        if argument_value is not None:
            del kwargs[argument_name]

        return kwargs

    def format_logger_message(self, message: str, resulted_service) -> str:
        """ Use that function in order to format your message. __format__ will be implemented in the future """
        if resulted_service is None:    # if an error happens, then we cannot use the values of None
            return message

        for replace_key, replace_value in (
            ("$service$", resulted_service),
            ("$objects$", resulted_service.objects),
        ):
            message = message.replace(replace_key, str(replace_value))

        return message

    def __call__(self, function: callable):
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

            kwargs = self._logger_argument_check_forced(argument_name='info_message', kwargs=kwargs)
            kwargs = self._logger_argument_check_forced(argument_name='error_message', kwargs=kwargs)
            # We delete the arguments so they do not interfere with other ORM arguments.

            try:
                new_service = service.__class__(objects=function(service, *args, **kwargs))

                if info_message is not None:
                    service.logger_obj.info(
                        self.format_logger_message(info_message, new_service),
                    )

                return new_service

            except (FieldError, ServiceProgrammingException) as programmer_exc:
                # Field error is related to the wrong arguments, that may be typo,
                # so we don't want to except these as the normal exception
                raise programmer_exc
            except Exception as exc:
                error_message = error_message or SERVICES_SETTINGS['DEFAULT_ERROR_LOG_MESSAGE']

                if settings.DEBUG or SERVICES_SETTINGS['ADD_EXCEPTION_TO_LOG']:
                    error_message += f". Exception: {exc}"

                service.logger_obj.error(self.format_logger_message(
                    message=error_message, resulted_service=None,
                ))
                return service.service_function_error_handler(exc=exc)

        return service_function_decorator_wrapper


class GetObjectsOrInstanceDecorator(ServiceFunctionDecorator):
    """
    That is the decorator that you want to use if your function will
    work with the instance provided in the kwargs, or using the current objects
    of your service.
    """
    def __call__(self, function: callable):
        function = super(get_objects_or_instance_decorator, self).__call__(function)

        def service_function_objects_or_instance_wrapper(service, *args, **kwargs):
            if kwargs.get('instance') is None:
                kwargs['instance'] = service.objects

            return function(service, *args, **kwargs)

        return service_function_objects_or_instance_wrapper


def service_function_for_write(function: callable):
    """ That decorator marks service function that can change the information in the database """

    @wraps(function)
    def service_function_for_write_wrapper(service, *args, **kwargs):
        if service.read_only:
            raise ServiceProgrammingException(f"You are calling write function on read_only service {service}")

        return function(service, *args, **kwargs)

    return service_function_for_write_wrapper


def service_function_default_arguments(**defaults):
    """
    That function provides the default argument into kwargs of the service function
    you are using. All you need to do is add key and value pairs for the service defaults.
    """

    def service_function_default_arguments_decorator(function: callable):

        @wraps(function)
        def service_function_default_argument_wrapper(service, *args, **kwargs):
            for default_key, default_value in defaults:
                if kwargs.get(default_key) is None:
                    kwargs[default_key] = default_value

            return function(service, *args, **kwargs)

        return service_function_default_argument_wrapper

    return service_function_default_arguments_decorator


service_function_decorator = ServiceFunctionDecorator
get_objects_or_instance_decorator = GetObjectsOrInstanceDecorator

__all__ = [
    'ServiceFunctionDecorator',
    'service_function_decorator',
    'get_objects_or_instance_decorator',
    'service_function_for_write',
    'service_function_default_arguments',
]
