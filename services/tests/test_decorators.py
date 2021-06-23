from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from services import Service, service_function_decorator
from services.users import UserService


class TestServiceFunctionDecorator(TestCase):
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


