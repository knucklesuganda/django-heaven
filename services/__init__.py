from services.services import Service
from services.decorators import (
    service_function_decorator,
    service_function_for_write,
    get_objects_or_instance_decorator,
)

__all__ = [
    'Service',
    'service_function_for_write',
    'service_function_decorator',
    'get_objects_or_instance_decorator',
]

