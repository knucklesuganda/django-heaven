from unittest.mock import patch
from django.http import HttpResponseRedirect

from responses.redirect import LoggedRedirectResponseMixin
from responses.tests.base import BaseLoggedResponseMixinTest


class LoggedRedirectResponseMixinTest(BaseLoggedResponseMixinTest):
    testing_class = LoggedRedirectResponseMixin
    info_data = HttpResponseRedirect("https://google.com")
    error_data = HttpResponseRedirect("https://example.com")

    def _test_log_response_base(self, log_function: str):
        with patch.object(self.response_class.logger_obj, log_function) as mock_logger:
            log_message = "test log message"
            getattr(self.response_class, f'log_response_as_{log_function}')(
                data=getattr(self, f"{log_function}_data"), log_message=log_message,
                redirect_code=302,
            )

            mock_logger.assert_called_once_with(log_message)
