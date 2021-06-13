from django.http import JsonResponse

from responses.json import LoggedJsonResponseMixin, LoggedJsonResponseProxyMixin
from responses.tests.base import BaseLoggedResponseMixinTest


class LoggedJsonResponseMixinTest(BaseLoggedResponseMixinTest):
    """ That is the tests for the LoggedJsonResponseMixin responses """
    testing_class = LoggedJsonResponseMixin
    is_proxy = False

    info_data = [1, 2, 3]
    error_data = [4, 5, 6]


class LoggedJsonResponseProxyMixinTest(BaseLoggedResponseMixinTest):
    testing_class = LoggedJsonResponseProxyMixin
    is_proxy = True

    info_data = JsonResponse(data={"message": "Hello"})
    error_data = JsonResponse(data={"really": "yes"})

    def test_safe_is_true_only(self):
        try:
            self.response_class.log_response_as_info(data=self.info_data, log_message="Test log message")
            self.response_class.log_response_as_error(data=self.info_data, log_message="Test log message")
        except Exception as exc:
            self.fail(exc)

        with self.assertRaises(ValueError):
            self.response_class.log_response_as_info(
                data=JsonResponse(data=[1, 2, 3], safe=False),
                log_message="Test log message",
            )

        with self.assertRaises(ValueError):
            self.response_class.log_response_as_error(
                data=JsonResponse(data=[1, 2, 3], safe=False),
                log_message="Test log message",
            )

    def test_wrong_data_provided_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.response_class.log_response_as_info(data=[1, 2, 3], log_message="Test log message")

        with self.assertRaises(ValueError):
            self.response_class.log_response_as_error(data=[1, 2, 3], log_message="Test log message")
