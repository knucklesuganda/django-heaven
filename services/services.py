"""
That is the file that contains all the base services.
Service is a wrapper for the Model. You will not make any direct ORM queries in your projects.
Instead, your code will have different services for various models. Every service will have optimized
ORM queries with logging and custom error handling. That is, you will split your views and serializers
to work with business logic in services.
"""
from django.conf import settings
from django.db.models import Model, QuerySet, Manager

from services.exceptions import ServiceException, ServiceProgrammingException
from services.decorators import (
    service_function_decorator,
    service_function_for_write,
    get_objects_or_instance_decorator,
)

SERVICES_SETTINGS = settings.DJANGO_HEAVEN['SERVICES']


class Service:
    """ The most base service for the django-heaven. Use that instead of direct model calls """
    model: Model = None    # your django ORM model
    read_only: bool = False  # if you only want to read from that model. May be useful for the read-only models
    raise_exception: bool = SERVICES_SETTINGS.get('RAISE_EXCEPTION', True)
    logger_obj = SERVICES_SETTINGS.get('LOGGER_OBJ')

    def __init__(self, objects=None):
        class_name = self.__class__.__name__
        self.objects = objects if objects is not None else self.model.objects

        if self.model is None:
            raise ValueError(f"You need to assign a model in {class_name}")

    @property
    def objects(self):
        """ Return the result of the service """
        return self._objects

    @objects.setter
    def objects(self, value):
        if self.model is not None:
            type_check_value = value.model if isinstance(value, (QuerySet, Manager)) else type(value)

            if not type_check_value == self.model:
                raise ServiceProgrammingException(
                    "Trying to set service objects as the different model type."
                    f"Your {self.__class__.__name__} works with {self.model}, "
                    f"  but value is {type(type_check_value)}"
                )

        self._objects = value

    def service_function_error_handler(self, exc: Exception):
        """
        That function is called whenever we receive an error in any of service functions.
        By default we will return None or will raise an error depending on self.raise_exception.
        If you do not reassign that, we will get global: settings.DJANGO_HEAVEN.SERVICES.RAISE_EXCEPTION
        value.
        """
        if self.raise_exception:
            raise ServiceException(exc)

    @service_function_decorator()
    def get(self, *args, **model_fields):
        if not args and not model_fields:
            raise ServiceProgrammingException("You need to provide *args or **kwargs in service get() function")

        return self.objects.get(*args, **model_fields)

    @service_function_decorator()
    def filter(self, *args, **model_fields):
        return self.objects.filter(*args, **model_fields)

    @service_function_decorator()
    def all(self):
        return self.objects.all()

    @service_function_decorator()
    def order_by(self, *args):
        return self.objects.order_by(*args)

    def get_argument_from_kwargs(self, kwargs: dict, argument: str):
        try:
            return kwargs[argument]
        except KeyError:
            raise ServiceProgrammingException(
                f"You must provide named-only argument '{argument}' in {self.__class__.__name__}",
            )

    def pop_argument_from_kwargs(self, kwargs: dict, argument: str):
        argument_value = self.get_argument_from_kwargs(kwargs=kwargs, argument=argument)
        del kwargs[argument]
        return kwargs, argument_value

    def refresh_from_db(self, **kwargs):
        """ Use that in order to refresh your model from the database"""
        kwargs, instance = self.pop_argument_from_kwargs(kwargs=kwargs, argument='instance')
        return instance.refresh_from_db(fields=kwargs.get('fields'), using=kwargs.get('using'))

    @get_objects_or_instance_decorator()
    def first(self, **kwargs):
        return kwargs['instance'].first()

    @get_objects_or_instance_decorator()
    def last(self, **kwargs):
        return kwargs['instance'].last()

    @service_function_for_write
    @get_objects_or_instance_decorator()
    def update(self, **kwargs):
        """
        Provide named-only argument 'instance' that will act as an instance you want to update.
        That method will automatically use 'update_fields' for the fields that you want to update.

        Arguments you can provide:
            - instance!: the instance that you want to update
            - using: what database you want to use
        """
        kwargs, instance = self.pop_argument_from_kwargs(kwargs=kwargs, argument='instance')
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
    @get_objects_or_instance_decorator()
    def create(self, *args, **kwargs):
        """Provide arguments to create an instance of your model."""
        instance = self.model_create_method()(*args, **kwargs)
        return instance

    @service_function_for_write
    @get_objects_or_instance_decorator()
    def delete(self, **kwargs):
        """ Delete an instance of your model """
        instance = self.get_argument_from_kwargs(kwargs, argument='instance')
        instance.delete()

    def _bulk_operation(self, bulk_function, **kwargs):
        instances = self.get_argument_from_kwargs(kwargs, 'instances')
        return bulk_function([
            self.model(**instance) for instance in instances
        ], **kwargs.get('arguments'))

    @service_function_for_write
    @service_function_decorator()
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
    @service_function_decorator()
    def bulk_update(self, **kwargs):
        return self._bulk_operation(bulk_function=self.model.objects.bulk_create, **kwargs,)

    def __str__(self):
        return f"{{{self.__class__.__name__} {self.objects}}}"

    def __repr__(self):
        return str(self)
