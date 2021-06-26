from unittest.mock import Mock

from django.contrib.auth.models import User

from services import Service
from services.exceptions import ServiceProgrammingException


def service_function_success(service, *args, **kwargs):
    return User.objects.all()


def service_function_programming_exception(service, *args, **kwargs):
    raise ServiceProgrammingException()


def service_function_normal_exception(service, *args, **kwargs):
    raise ValueError()


logger_obj = Mock()


class ServiceForTest(Service):
    model = User
    logger_obj = logger_obj
    service_kwargs = {
        "info_message": "test info",
        "error_message": "test error",
    }
