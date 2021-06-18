"""
That is the file that contains all the base services.
Service is a wrapper for the Model. You will not make any direct ORM queries in your projects.
Instead, your code will have different services for various models. Every service will have optimized
ORM queries with logging and custom error handling. That is, you will split your views and serializers
to work with business logic in services.
"""
from django.conf import settings
from django.db.models import Model

from services.exceptions import ServiceException, ServiceProgrammingException
from services.decorators import ServiceFunctionDecorator, service_function_for_write

SERVICES_SETTINGS = settings.DJANGO_HEAVEN['SERVICES']


class BaseService:
    """ The most base service for the django-heaven. Use that instead of direct model calls """
    model: Model = None    # your django ORM model
    read_only: bool = False  # if you only want to read from that model. May be useful for the read-only models
    raise_exception: bool = SERVICES_SETTINGS.get('RAISE_EXCEPTION', True)
    logger_obj = SERVICES_SETTINGS.get('LOGGER_OBJ')

    def __init__(self, objects=None, instance=None):
        class_name = self.__class__.__name__
        self._objects = objects or self.model.objects

        if self.model is None:
            raise ValueError(f"You need to assign model in {class_name}")
        elif not isinstance(self.read_only, bool):
            raise ValueError(f"'write_only' must be a bool() value in {class_name}")

    @property
    def result(self):
        """ Return the result of the service """
        return self._objects

    def service_function_error_handler(self, exc: Exception):
        """
        That function is called whenever we receive an error in any of service functions.
        By default we will return None or will raise an error depending on self.raise_exception.
        If you do not reassign that, we will get global: settings.DJANGO_HEAVEN.SERVICES.RAISE_EXCEPTION
        value.
        """
        if self.raise_exception:
            raise ServiceException(exc)

    @ServiceFunctionDecorator()
    def get(self, *args, **model_fields):
        if not args and not model_fields:
            raise ServiceProgrammingException("You need to provide *args or **kwargs in service get() function")

        return self._objects.get(*args, **model_fields)

    @ServiceFunctionDecorator()
    def filter(self, *args, **model_fields):
        return self._objects.filter(*args, **model_fields)

    @ServiceFunctionDecorator()
    def all(self):
        return self._objects.all()

    @ServiceFunctionDecorator()
    def order_by(self, *args):
        return self._objects.order_by(*args)

    def _get_argument_from_kwargs(self, kwargs: dict, argument: str):
        try:
            return kwargs[argument]
        except KeyError:
            raise ServiceProgrammingException(
                f"You must provide named-only argument '{argument}' in {self.__class__.__name__}",
            )

    def refresh_from_db(self, **kwargs):
        """ Use that in order to refresh your model from the database"""
        instance = self._get_argument_from_kwargs(kwargs=kwargs, argument='instance')
        return instance.refresh_from_db(fields=kwargs.get('fields'), using=kwargs.get('using'))

    @ServiceFunctionDecorator()
    def first(self):
        return self._objects.first()

    @ServiceFunctionDecorator()
    def last(self):
        return self._objects.last()

    @service_function_for_write
    @ServiceFunctionDecorator()
    def update(self, **kwargs):
        """
        Provide named-only argument 'instance' that will act as an instance you want to update.
        That method will automatically use 'update_fields' for the fields that you want to update.

        Arguments you can provide:
            - instance!: the instance that you want to update
            - using: what database you want to use
        """
        instance = self._get_argument_from_kwargs(kwargs=kwargs, argument='instance')
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

    @service_function_for_write
    @ServiceFunctionDecorator()
    def create(self, *args, **kwargs):
        """Provide arguments to create an instance of your model."""
        instance = self.model_create_method()(*args, **kwargs)
        return instance

    @service_function_for_write
    @ServiceFunctionDecorator()
    def delete(self, **kwargs):
        """ Delete an instance of your model """
        instance = self._get_argument_from_kwargs(kwargs, argument='instance')
        instance.delete()

    def _bulk_operation(self, bulk_function, **kwargs):
        instances = self._get_argument_from_kwargs(kwargs, 'instances')
        return bulk_function([
            self.model(**instance) for instance in instances
        ], **kwargs.get('arguments'))

    @service_function_for_write
    @ServiceFunctionDecorator()
    def bulk_create(self, **kwargs):
        """
        Use that to create a lot of models at once.
        Provide kwargs in that order:
        instances=[
            {"arg" 1},
            {"arg": 2}
        ]
        """
        return self._bulk_operation(bulk_function=self.model.objects.bulk_create, **kwargs,)

    @service_function_for_write
    @ServiceFunctionDecorator
    def bulk_update(self, **kwargs):
        return self._bulk_operation(bulk_function=self.model.objects.bulk_create, **kwargs,)

    def __str__(self):
        return f"{{{self.__class__.__name__} {self.result}}}"

    def __repr__(self):
        return str(self)
