from logging import getLogger
from unittest.mock import patch

from django.test import TestCase

from django.conf import settings
from responses.base import BaseLoggedResponseMixin, BaseLoggedResponseProxyMixin


class BaseLoggedResponseMixinTest(TestCase):
    """ That is the base class for the responses tests """
    testing_class = None
    is_proxy = False

    info_data = None
    error_data = None

    @classmethod
    def setUpClass(cls):
        super(BaseLoggedResponseMixinTest, cls).setUpClass()
        cls.response_class: BaseLoggedResponseMixin = cls.testing_class()
        cls.response_class.logger_obj = getLogger(settings.TEST_LOGGER_NAME)

    def test_child_of_base_logged_response_mixin(self):
        self.assertIn(BaseLoggedResponseMixin, self.testing_class.mro())

    def test_child_of_base_logged_response_proxy_mixin(self):
        if self.is_proxy:
            self.assertIn(BaseLoggedResponseProxyMixin, self.testing_class.mro())

    def __test_log_response_base(self, log_function: str):
        with patch.object(self.response_class.logger_obj, log_function) as mock_logger:
            log_message = "test log message"
            getattr(self.response_class, f'log_response_as_{log_function}')(
                data=getattr(self, f"{log_function}_data"), log_message=log_message
            )

            mock_logger.assert_called_once_with(log_message)

    def test_log_response_as_info_logging_message(self):
        self.__test_log_response_base('info')

    def test_log_response_as_error_logging_message(self):
        self.__test_log_response_base('error')

