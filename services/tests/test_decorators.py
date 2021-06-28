from typing import Any
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from services import service_function_decorator
from services.decorators import ObjectsOrKwargsDecorator, ServiceFunctionDecorator
from services.exceptions import ServiceProgrammingException
from services.tests.test_utils import (
    ServiceForTest,
    service_function_success,
    service_function_normal_exception,
    service_function_programming_exception,
)


class TestServiceFunctionDecorator(TestCase):
    def setUp(self) -> None:
        self.service = ServiceForTest()

    # Utilities
    def util_init_force_argument(self, init_argument_name: str, settings_argument_name: str):
        service_decorator = service_function_decorator(**{init_argument_name: True})
        self.assertTrue(getattr(service_decorator, init_argument_name))

        service_decorator = service_function_decorator(**{init_argument_name: False})
        self.assertFalse(getattr(service_decorator, init_argument_name))

        initial_argument_value = settings.DJANGO_HEAVEN['SERVICES'][settings_argument_name]

        settings.DJANGO_HEAVEN['SERVICES'][settings_argument_name] = True
        service_decorator = service_function_decorator()
        self.assertTrue(getattr(service_decorator, init_argument_name))

        settings.DJANGO_HEAVEN['SERVICES'][settings_argument_name] = False
        service_decorator = service_function_decorator()
        self.assertFalse(getattr(service_decorator, init_argument_name))

        settings.DJANGO_HEAVEN['SERVICES'][settings_argument_name] = initial_argument_value

    def util_format_logger_message_formatting(self, logger_message, formatting_value, return_value):
        service_decorator = service_function_decorator()

        service = ServiceForTest(objects=User.objects.all())
        service_decorator.format_logger_message.return_value = return_value

        self.assertEqual(
            service_decorator.format_logger_message(logger_message, service),
            logger_message.replace(logger_message, str(formatting_value)),
        )

    def util_mock_decorator_function_and_call(
        self, call_args, force_error, force_info, service_function: callable,
        mocked_function: str, return_value: str,
    ):
        setattr(service_function_decorator, mocked_function, Mock())
        setattr(getattr(service_function_decorator, mocked_function), 'return_value', return_value)

        service_decorator = service_function_decorator(force_error, force_info)(service_function)
        return service_decorator(self.service, **call_args)

    def util_mock_decorator_format_logger_message_and_call(
        self, call_args, force_error, force_info, service_function: callable, return_value: Any,
    ):
        return self.util_mock_decorator_function_and_call(
            call_args=call_args,
            force_error=force_error,
            force_info=force_info,
            service_function=service_function,
            mocked_function='format_logger_message',
            return_value=return_value,
        )
    # Utilities

    def test_init_force_error_message_argument(self):
        self.util_init_force_argument(
            init_argument_name="force_error_message",
            settings_argument_name='FORCE_ERROR_MESSAGE_ARGUMENT',
        )

    def test_init_force_info_message_argument(self):
        self.util_init_force_argument(
            init_argument_name="force_info_message",
            settings_argument_name='FORCE_INFO_MESSAGE_ARGUMENT',
        )

    def test_logger_argument_check_forced_is_true(self):
        service_decorator = service_function_decorator(force_error_message=True)

        try:
            service_decorator._logger_argument_check_forced("error_message", kwargs={
                "error_message": "test",
            })
        except Exception as exc:
            self.fail(exc)

        with self.assertRaises(ValueError):
            service_decorator._logger_argument_check_forced(
                argument_name="error_message", kwargs={}
            )

    def test_logger_argument_check_forced_is_false(self):
        service_decorator = service_function_decorator(force_info_message=False)

        try:
            service_decorator._logger_argument_check_forced("info_message", kwargs={
                "info_message": "test",
            })
            service_decorator._logger_argument_check_forced("info_message", {})
        except Exception as exc:
            self.fail(exc)

    def test_logger_argument_check_forced_deletes_argument(self):
        service_decorator = service_function_decorator(force_info_message=True)

        self.assertDictEqual(service_decorator._logger_argument_check_forced("info_message", kwargs={
            "info_message": "test",
        }), {})

        service_decorator.force_info_message = False
        self.assertDictEqual(service_decorator._logger_argument_check_forced("info_message", kwargs={
            "info_message": "test",
        }), {})

    def test_format_logger_message_no_resulted_service(self):
        log_message = "hello"
        service_function_decorator.format_logger_message.return_value = log_message

        service_decorator = service_function_decorator()
        self.assertEqual(service_decorator.format_logger_message(log_message, None), log_message)

    def test_format_logger_message_resulted_service_in_log_message(self):
        service_value = ServiceForTest(objects=User.objects.all())
        self.util_format_logger_message_formatting(
            logger_message="$service$",
            formatting_value=service_value,
            return_value=str(service_value),
        )

    def test_format_logger_message_resulted_service_objects_in_log_message(self):
        service_value = ServiceForTest(objects=User.objects.all())
        self.util_format_logger_message_formatting(
            logger_message="$objects$",
            formatting_value=service_value.objects,
            return_value=str(service_value.objects),
        )

    def test_decorator_call_returns_function(self):
        service_decorator = service_function_decorator()
        self.assertTrue(callable(service_decorator(lambda: None)))

    def test_call_service_function_calls_provided_function(self):
        was_called = False

        def test_service_function(service):
            nonlocal was_called
            was_called = True
            return User.objects.all()

        service_decorator = service_function_decorator()(test_service_function)
        service_decorator(self.service, **ServiceForTest.service_kwargs)
        self.assertTrue(was_called)

    def test_call_service_function_removes_logger_arguments(self):
        self.service_function = Mock()
        self.service_function.return_value = User.objects.first()

        service_decorator = service_function_decorator()(self.service_function)
        service_decorator(self.service, **ServiceForTest.service_kwargs)

        self.service_function.assert_called_once()
        self.service_function.assert_called_with(self.service)

    def test_call_service_logger_info_if_info_message_is_not_none(self):
        info_message = "test message"
        service_decorator = service_function_decorator()(service_function_success)
        service_decorator(self.service, **{
            **ServiceForTest.service_kwargs, "info_message": info_message,
            # it is better to write it here, even though it is already written in setUp()
        })

        ServiceForTest.logger_obj.info.assert_called_with(info_message)

    def test_call_service_logger_info_if_info_message_calls_format_message(self):
        info_message = "test message"
        service_result = self.util_mock_decorator_format_logger_message_and_call(
            {
                **ServiceForTest.service_kwargs, "info_message": info_message,
                # It is better to write info_message in here, even though it is already written in setUp()
            },
            force_error=True, force_info=True,
            service_function=service_function_success,
            return_value=info_message,
        )

        service_function_decorator.format_logger_message.assert_called_once()
        service_function_decorator.format_logger_message.assert_called_with(
            info_message, service_result,
        )

    def test_no_service_logger_info_call_if_info_message_is_none(self):
        self.util_mock_decorator_format_logger_message_and_call(
            {
                **ServiceForTest.service_kwargs,
                "info_message": None,
            },
            force_error=True, force_info=False,
            service_function=service_function_success,
            return_value=None,
        )
        service_function_decorator.format_logger_message.assert_not_called()

        info_message = "hello"
        result_service = self.util_mock_decorator_format_logger_message_and_call(
            {**ServiceForTest.service_kwargs, "info_message": info_message},
            force_error=True, force_info=False,
            service_function=service_function_success,
            return_value=info_message,
        )
        service_function_decorator.format_logger_message.assert_called_with(
            info_message, result_service,
        )

    def test_service_decorator_returns_new_service(self):
        result_service = self.util_mock_decorator_format_logger_message_and_call(
            ServiceForTest.service_kwargs, force_error=True, force_info=True,
            service_function=service_function_success, return_value="",
        )

        self.assertIsInstance(result_service, ServiceForTest)
        self.assertEqual(
            list(result_service.objects), list(service_function_success(ServiceForTest())),
        )

    def test_service_re_raises_programming_exception(self):
        service_decorator = service_function_decorator()(service_function_programming_exception)

        with self.assertRaises(ServiceProgrammingException):
            service_decorator(ServiceForTest(), **ServiceForTest.service_kwargs)

    @override_settings(DEBUG=True)
    def test_service_formats_error_message_on_normal_exception(self):
        service_decorator = service_function_decorator()(service_function_normal_exception)
        service_decorator.format_logger_message = Mock()

        error_message = "test message. Exception: "
        service_decorator(ServiceForTest(), **{
            **ServiceForTest.service_kwargs, "error_message": error_message,
        })
        service_decorator.format_logger_message.assert_called_with(error_message, None)

    def test_service_exception_logs_error_on_normal_exception(self):
        error_message = "test message"
        self.util_mock_decorator_format_logger_message_and_call(
            call_args={
                **ServiceForTest.service_kwargs,
                "error_message": error_message,
            },
            force_error=True,
            force_info=False,
            service_function=service_function_normal_exception,
            return_value=error_message,
        )

        ServiceForTest.logger_obj.error.assert_called_once()
        ServiceForTest.logger_obj.error.assert_called_with(error_message)


class TestGetObjectsOrInstanceDecorator(TestCase):
    def util_decorate_success_function(self) -> callable:
        decorator_instance = ObjectsOrKwargsDecorator()
        return decorator_instance(service_function_success)

    def util_call_decorated_success_function(self):
        decorated_function = self.util_decorate_success_function()
        return decorated_function(
            service=ServiceForTest(), info_message="info message", error_message="error message",
        )

    def test_service_function_decorator_in_mro(self):
        self.assertIn(ServiceFunctionDecorator, ObjectsOrKwargsDecorator.mro())

    def test_super_service_function_call_invoked(self):
        with patch('services.decorators.ServiceFunctionDecorator.__call__') as service_call_function:
            self.util_call_decorated_success_function()
            service_call_function.assert_called_once()
            service_call_function.assert_called_with(service_function_success)

    def test_call_returns_callable(self):
        self.assertTrue(callable(self.util_decorate_success_function()))

    def test(self):
        pass
