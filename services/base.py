"""
That is the file that contains all the base services.
Service is a wrapper for the Model. You will not make any direct ORM queries in your projects.
Instead, your code will have different services for various models. Every service will have optimized
ORM queries with logging and custom error handling. That is, you will split your views and serializers
to work with business logic in services.
"""
from functools import wraps

from django.conf import settings
from django.db.models import Model
from django.core.exceptions import FieldError

from services.exceptions import ServiceException, ServiceProgrammingException

SERVICES_SETTINGS = settings.DJANGO_HEAVEN['SERVICES']


def service_function_decorator(function: callable):
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
    force_error_message_arg = SERVICES_SETTINGS.get('FORCE_ERROR_MESSAGE_ARGUMENT', True)
    force_info_message_arg = SERVICES_SETTINGS.get('FORCE_INFO_MESSAGE_ARGUMENT', True)

    @wraps(function)
    def service_function_decorator_wrapper(self, *args, **kwargs):
        nonlocal function
        error_message = kwargs.get('error_message')
        info_message = kwargs.get('info_message')

        if force_error_message_arg:
            if error_message is None:
                raise ValueError("You must provide error_message argument")
            del kwargs['error_message']     # We delete it so it does not interfere with other ORM arguments.

        if force_info_message_arg:
            if info_message is None:
                raise ValueError("You must provide info_message argument")
            del kwargs['info_message']      # We delete it so it does not interfere with other ORM arguments.

        returned_result_in_info = kwargs.get('returned_result_in_info')
        if returned_result_in_info:
            del kwargs['returned_result_in_info']

        try:
            result = function(self, *args, **kwargs)

            if info_message is not None:
                if returned_result_in_info:
                    info_message = info_message.replace('$result$', str(result))

                self.logger_obj.info(info_message)

            return result

        except (FieldError, ServiceProgrammingException) as exc:
            # Field error is related to the wrong arguments, that may be typo,
            # so we don't want to except these as the normal exception
            raise exc
        except Exception as exc:
            if error_message is not None:
                self.logger_obj.error(error_message)

            return self.service_function_error_handler(exc=exc)

    return service_function_decorator_wrapper


class BaseService:
    """ The most base service for the django-heaven. Use that instead of direct model calls """
    model: Model = None    # your django ORM model
    write_only: bool = False  # if you only want to read from that model. May be useful for the read-only models
    raise_exception: bool = SERVICES_SETTINGS.get('RAISE_EXCEPTION', True)
    logger_obj = SERVICES_SETTINGS.get('LOGGER_OBJ')

    def __init__(self, objects=None):
        class_name = self.__class__.__name__
        self.objects = objects or self.model.objects

        if self.model is None:
            raise ValueError(f"You need to assign model in {class_name}")
        elif not isinstance(self.write_only, bool):
            raise ValueError(f"'write_only' must be a bool() value in {class_name}")

    def service_function_error_handler(self, exc: Exception):
        """
        That function is called whenever we receive an error in any of service functions.
        By default we will return None or will raise an error depending on self.raise_exception.
        If you do not reassign that, we will get global: settings.DJANGO_HEAVEN.SERVICES.RAISE_EXCEPTION
        value.
        """
        if self.raise_exception:
            raise ServiceException(exc)

    @service_function_decorator
    def get(self, *args, **model_fields):
        if not args and not model_fields:
            raise ServiceProgrammingException("You need to provide *args or **kwargs in service get() function")

        return self.objects.get(*args, **model_fields)

    @service_function_decorator
    def filter(self, *args, **model_fields):
        return self.objects.filter(*args, **model_fields)

    @service_function_decorator
    def all(self):
        return self.objects.all()

    @service_function_decorator
    def order_by(self, *args):
        return self.objects.order_by(*args)

    def _get_instance_from_kwargs(self, kwargs):
        try:
            return kwargs['instance']
        except KeyError:
            raise ServiceProgrammingException("You must provide named-only argument 'instance' in update()")

    def refresh_from_db(self, **kwargs):
        """ Use that in order to refresh your model from the database"""
        instance = self._get_instance_from_kwargs(kwargs)
        return instance.refresh_from_db(fields=kwargs.get('fields'), using=kwargs.get('using'))

    @service_function_decorator
    def first(self):
        return self.objects.first()

    @service_function_decorator
    def last(self):
        return self.objects.last()

    @service_function_decorator
    def update(self, **kwargs):
        """
        Provide named-only argument 'instance' that will act as an instance you want to update.
        That method will automatically use 'update_fields' for the fields that you want to update.

        Arguments you can provide:
            - instance!: the instance that you want to update
            - using: what database you want to use
        """
        instance = self._get_instance_from_kwargs(kwargs)
        using_argument: str = kwargs.get('using')

        for field, value in kwargs.items():
            setattr(instance, field, value)

        instance.save(update_fields=kwargs.keys(), force_update=True, using=using_argument)
        return instance

    def model_create_method(self) -> callable:
        """
        That is the function that returns another function that will be used as a creation method
        for your models. For example, in Django User we have create_user() instead of create().
        You will need to reassign your creation function in here.
        """
        return self.model.objects.create

    @service_function_decorator
    def create(self, *args, **kwargs):
        """Provide arguments to create an instance of your model."""
        instance = self.model_create_method()(*args, **kwargs)
        return instance

    @service_function_decorator
    def delete(self, **kwargs):
        instance = self._get_instance_from_kwargs(kwargs)
        instance.delete()
        return True
