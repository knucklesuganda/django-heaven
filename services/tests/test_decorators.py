from unittest.mock import patch, Mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from services import service_function_decorator, Service
from services.exceptions import ServiceProgrammingException
from services.users import UserService


class TestServiceFunctionDecorator(TestCase):
    @staticmethod
    def service_function_success(service, *args, **kwargs):
        return User.objects.all()

    @staticmethod
    def service_function_programming_exception(service, *args, **kwargs):
        raise ServiceProgrammingException()

    @staticmethod
    def service_function_normal_exception(service, *args, **kwargs):
        raise ValueError()

    logger_obj = Mock()

    class ServiceForTest(Service):
        model = User

    def setUp(self) -> None:
        self.test_service = self.ServiceForTest()
        self.test_service.logger_obj = self.logger_obj
        self.service_test_kwargs = {
            "info_message": "test info",
            "error_message": "test error",
        }

    def _test_init_force_argument(self, init_argument_name: str, settings_argument_name: str):
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

    def test_init_force_error_message_argument(self):
        self._test_init_force_argument(
            init_argument_name="force_error_message",
            settings_argument_name='FORCE_ERROR_MESSAGE_ARGUMENT',
        )

    def test_init_force_info_message_argument(self):
        self._test_init_force_argument(
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
        service_decorator = service_function_decorator()
        initial_log_message = "hello"
        self.assertEqual(service_decorator.format_logger_message(initial_log_message, None), initial_log_message)

    def _test_format_logger_message_formatting(self, formatting_argument, formatting_value):
        service_decorator = service_function_decorator()
        initial_log_message = f"hello {formatting_argument}"
        service = UserService(objects=User.objects.all())
        self.assertEqual(
            service_decorator.format_logger_message(initial_log_message, service),
            initial_log_message.replace(formatting_argument, str(formatting_value)),
        )

    def test_format_logger_message_resulted_service_in_log_message(self):
        self._test_format_logger_message_formatting(
            formatting_argument="$service$",
            formatting_value=UserService(objects=User.objects.all()),
        )

    def test_format_logger_message_resulted_service_objects_in_log_message(self):
        self._test_format_logger_message_formatting(
            formatting_argument="$objects$",
            formatting_value=UserService(objects=User.objects.all()).objects,
        )

    def test_call_returns_function(self):
        service_decorator = service_function_decorator()
        self.assertTrue(callable(service_decorator(lambda a: 10)))

    def test_call_service_function_decorator_wrapper_arguments_forced_error_message(self):
        with patch('services.service_function_decorator') as decorator_mock:
            decorator_mock()(lambda service: User.objects.all())(
                self.test_service, **self.service_test_kwargs,
            )

    def test_call_service_function_calls_provided_function(self):
        was_called = False

        def test_service_function(service):
            nonlocal was_called
            was_called = True
            return User.objects.all()

        service_decorator = service_function_decorator()(test_service_function)
        service_decorator(self.test_service, **self.service_test_kwargs)
        self.assertTrue(was_called)

    def test_call_service_function_removes_logger_arguments(self):
        self.service_function = Mock()
        self.service_function.return_value = User.objects.first()

        service_decorator = service_function_decorator()(self.service_function)
        service_decorator(self.test_service, **self.service_test_kwargs)

        self.service_function.assert_called_once()
        self.service_function.assert_called_with(self.test_service)

    def test_call_service_logger_info_if_info_message_is_not_none(self):
        info_message = "test message"
        service_decorator = service_function_decorator()(self.service_function)
        service_decorator(self.test_service, **{
            **self.service_test_kwargs, "info_message": info_message,     # it is better to write it here,
            # even though it is already written in setUp()
        })

        self.logger_obj.info.assert_called_once()
        self.logger_obj.info.assert_called_with(info_message)

    def _mock_format_message_and_call_service_decorator(self, call_args, force_error, force_info):
        service_function_decorator.format_logger_message = Mock()
        service_decorator = service_function_decorator(force_error, force_info)(self.service_function)
        return service_decorator(self.test_service, **call_args)

    def test_call_service_logger_info_if_info_message_calls_format_message(self):
        service_result = self._mock_format_message_and_call_service_decorator({
            **self.service_test_kwargs, "info_message": "hello",
            # It is better to write info_message in here, even though it is already written in setUp()
        }, force_error=True, force_info=True)

        service_function_decorator.format_logger_message.assert_called_once()
        service_function_decorator.format_logger_message.assert_called_with(
            "test message", service_result,
        )

    def test_no_service_logger_info_call_if_info_message_is_none(self):
        self._mock_format_message_and_call_service_decorator(
            {**self.service_test_kwargs, "info_message": None},
            force_error=True, force_info=False,
        )
        service_function_decorator.format_logger_message.assert_not_called()

        test_message = "hello"
        result_service = self._mock_format_message_and_call_service_decorator(
            {**self.service_test_kwargs, "info_message": test_message},
            force_error=True, force_info=False,
        )
        service_function_decorator.format_logger_message.assert_called_with(
            test_message, result_service,
        )

    def test_service_decorator_returns_new_service(self):
        result_service = self._mock_format_message_and_call_service_decorator(
            self.service_test_kwargs, force_error=True, force_info=True,
        )

        self.assertIsInstance(result_service, self.ServiceForTest)
        self.assertEqual(
            list(result_service.objects), list(self.service_function(self.ServiceForTest())),
        )

    def test_service_re_raises_programming_exception(self):
        service_decorator = service_function_decorator()(self.service_function_programming_exception)

        with self.assertRaises(ServiceProgrammingException):
            service_decorator(self.ServiceForTest(), **self.service_test_kwargs)
