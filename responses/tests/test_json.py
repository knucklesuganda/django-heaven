from django.http import JsonResponse

from responses.exceptions import ResponseProgrammingException
from responses.json import LoggedJsonResponseMixin
from responses.tests.base import BaseLoggedResponseMixinTest


class LoggedJsonResponseMixinTest(BaseLoggedResponseMixinTest):
    """ That is the tests for the LoggedJsonResponseMixin responses """
    testing_class = LoggedJsonResponseMixin

    info_data = [1, 2, 3]
    error_data = [4, 5, 6]

    def test_proxy_safe_is_true_only(self):
        try:
            self.response_class.log_response_as_info(
                data=JsonResponse({"data": self.info_data}),
                log_message="Test log message",
                status_code=200,
            )
            self.response_class.log_response_as_error(
                data=JsonResponse({"data": self.info_data}),
                log_message="Test log message",
                status_code=200,
            )
        except Exception as exc:
            self.fail(exc)

        with self.assertRaises(ResponseProgrammingException):
            self.response_class.log_response_as_info(
                data=JsonResponse(data=[1, 2, 3], safe=False),
                log_message="Test log message",
                status_code=200,
            )

        with self.assertRaises(ResponseProgrammingException):
            self.response_class.log_response_as_error(
                data=JsonResponse(data=[1, 2, 3], safe=False),
                log_message="Test log message",
                status_code=200,
            )

    def test_proxy_response_validation_function(self):
        with self.assertRaises(ResponseProgrammingException):
            self.testing_class().proxy_response_validation(
                JsonResponse(data=[1, 2, 3], safe=False), status_code=200,
            )

        self.testing_class().proxy_response_validation(JsonResponse(data={"data": 10}), status_code=200)
